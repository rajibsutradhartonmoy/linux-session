// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use std::process::Command;
use chrono::{DateTime, Utc};

#[derive(Debug, Serialize, Deserialize, Clone)]
struct App {
    name: String,
    command: String,
    pid: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct Session {
    created: DateTime<Utc>,
    apps: Vec<App>,
}

#[derive(Debug, Serialize, Deserialize)]
struct SessionsData {
    sessions: HashMap<String, Session>,
}

fn get_config_path() -> PathBuf {
    let home = std::env::var("HOME").unwrap_or_else(|_| "/tmp".to_string());
    let config_dir = PathBuf::from(home).join(".config").join("session-saver");
    fs::create_dir_all(&config_dir).ok();
    config_dir.join("sessions.json")
}

fn load_sessions() -> HashMap<String, Session> {
    let path = get_config_path();
    if path.exists() {
        let content = fs::read_to_string(path).unwrap_or_default();
        let data: Result<SessionsData, _> = serde_json::from_str(&content);
        match data {
            Ok(d) => d.sessions,
            Err(_) => HashMap::new(),
        }
    } else {
        HashMap::new()
    }
}

fn save_sessions(sessions: &HashMap<String, Session>) -> Result<(), String> {
    let path = get_config_path();
    let data = SessionsData {
        sessions: sessions.clone(),
    };
    let json = serde_json::to_string_pretty(&data).map_err(|e| e.to_string())?;
    fs::write(path, json).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
fn get_running_apps() -> Result<Vec<App>, String> {
    let mut apps = Vec::new();

    // Try wmctrl first
    let wmctrl_result = Command::new("wmctrl")
        .arg("-lp")
        .output();

    if let Ok(output) = wmctrl_result {
        if output.status.success() {
            let stdout = String::from_utf8_lossy(&output.stdout);
            for line in stdout.lines() {
                let parts: Vec<&str> = line.split_whitespace().collect();
                if parts.len() >= 5 {
                    let pid = parts[2].to_string();
                    let window_name = parts[4..].join(" ");

                    // Get command from /proc
                    let cmdline_path = format!("/proc/{}/cmdline", pid);
                    if let Ok(cmdline_bytes) = fs::read(&cmdline_path) {
                        let cmdline = String::from_utf8_lossy(&cmdline_bytes)
                            .replace('\0', " ")
                            .trim()
                            .to_string();

                        if !cmdline.is_empty() {
                            apps.push(App {
                                name: window_name,
                                command: cmdline,
                                pid,
                            });
                        }
                    }
                }
            }
        }
    } else {
        // Fallback to ps
        let ps_result = Command::new("ps")
            .args(&["aux"])
            .output();

        if let Ok(output) = ps_result {
            let stdout = String::from_utf8_lossy(&output.stdout);
            for line in stdout.lines().skip(1) {
                let parts: Vec<&str> = line.split_whitespace().collect();
                if parts.len() >= 11 {
                    let pid = parts[1].to_string();
                    let command = parts[10..].join(" ");

                    // Filter out system processes
                    if command.contains("ps aux") || command.contains("grep") {
                        continue;
                    }

                    let name = command
                        .split_whitespace()
                        .next()
                        .unwrap_or("Unknown")
                        .split('/')
                        .last()
                        .unwrap_or("Unknown")
                        .to_string();

                    apps.push(App {
                        name,
                        command,
                        pid,
                    });
                }
            }
        }
    }

    // Remove duplicates by command
    let mut seen = std::collections::HashSet::new();
    apps.retain(|app| seen.insert(app.command.clone()));

    Ok(apps)
}

#[tauri::command]
fn save_session(name: String, apps: Vec<App>) -> Result<String, String> {
    let mut sessions = load_sessions();

    let session = Session {
        created: Utc::now(),
        apps,
    };

    sessions.insert(name.clone(), session);
    save_sessions(&sessions)?;

    Ok(format!("Session '{}' saved successfully", name))
}

#[tauri::command]
fn get_sessions() -> Result<HashMap<String, Session>, String> {
    Ok(load_sessions())
}

#[tauri::command]
fn load_session(name: String) -> Result<String, String> {
    let sessions = load_sessions();

    let session = sessions.get(&name).ok_or("Session not found")?;

    let mut success_count = 0;
    let total_count = session.apps.len();

    for app in &session.apps {
        let args: Vec<&str> = app.command.split_whitespace().collect();
        if args.is_empty() {
            continue;
        }

        let result = Command::new(args[0])
            .args(&args[1..])
            .spawn();

        if result.is_ok() {
            success_count += 1;
        }
    }

    Ok(format!("Launched {}/{} applications", success_count, total_count))
}

#[tauri::command]
fn delete_session(name: String) -> Result<String, String> {
    let mut sessions = load_sessions();

    if sessions.remove(&name).is_some() {
        save_sessions(&sessions)?;
        Ok(format!("Session '{}' deleted successfully", name))
    } else {
        Err("Session not found".to_string())
    }
}

#[tauri::command]
fn update_session(name: String, indices: Vec<usize>) -> Result<String, String> {
    let mut sessions = load_sessions();

    let session = sessions.get_mut(&name).ok_or("Session not found")?;

    let mut indices_sorted = indices.clone();
    indices_sorted.sort_by(|a, b| b.cmp(a)); // Sort in reverse order

    let mut removed_count = 0;
    for idx in indices_sorted {
        if idx < session.apps.len() {
            session.apps.remove(idx);
            removed_count += 1;
        }
    }

    save_sessions(&sessions)?;

    Ok(format!("Removed {} app(s) from session '{}'", removed_count, name))
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            get_running_apps,
            save_session,
            get_sessions,
            load_session,
            delete_session,
            update_session
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
