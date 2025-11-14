#!/usr/bin/env python3
"""
Linux Session Manager - Core functionality for saving and restoring application sessions
"""

import json
import os
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class SessionManager:
    """Manages application sessions on Linux"""

    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the session manager"""
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".config" / "session-saver"

        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_file = self.config_dir / "sessions.json"
        self.sessions = self._load_sessions()

    def _load_sessions(self) -> Dict:
        """Load sessions from JSON file"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {self.sessions_file}, starting fresh")
                return {}
        return {}

    def _save_sessions(self):
        """Save sessions to JSON file"""
        with open(self.sessions_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)

    def get_running_apps(self) -> List[Dict[str, str]]:
        """
        Get list of currently running applications

        Returns:
            List of dicts with 'name', 'command', and 'pid' keys
        """
        apps = []

        # Try wmctrl first (works with X11)
        try:
            result = subprocess.run(['wmctrl', '-lp'],
                                  capture_output=True,
                                  text=True,
                                  check=True)

            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                parts = line.split(None, 4)
                if len(parts) >= 5:
                    pid = parts[2]
                    window_name = parts[4]

                    # Get command from /proc
                    try:
                        with open(f'/proc/{pid}/cmdline', 'r') as f:
                            cmdline = f.read().replace('\x00', ' ').strip()

                        if cmdline:
                            apps.append({
                                'name': window_name,
                                'command': cmdline,
                                'pid': pid
                            })
                    except (FileNotFoundError, PermissionError):
                        continue

        except (subprocess.CalledProcessError, FileNotFoundError):
            # wmctrl not available or failed, try alternative method
            print("Note: wmctrl not found, using alternative detection method")
            apps = self._get_apps_from_ps()

        # Remove duplicates based on command
        seen_commands = set()
        unique_apps = []
        for app in apps:
            if app['command'] not in seen_commands:
                seen_commands.add(app['command'])
                unique_apps.append(app)

        return unique_apps

    def _get_apps_from_ps(self) -> List[Dict[str, str]]:
        """Fallback method to get apps using ps command"""
        apps = []
        try:
            # Get graphical applications (those with DISPLAY set)
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                check=True
            )

            for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    pid = parts[1]
                    command = parts[10]

                    # Filter out system processes and shell commands
                    if any(skip in command for skip in ['ps aux', 'grep', '/bin/sh', 'bash', 'sudo']):
                        continue

                    # Try to get a better name
                    name = command.split()[0].split('/')[-1] if command else 'Unknown'

                    apps.append({
                        'name': name,
                        'command': command,
                        'pid': pid
                    })

        except subprocess.CalledProcessError:
            print("Error: Could not get process list")

        return apps

    def save_session(self, session_name: str, apps: Optional[List[Dict]] = None) -> bool:
        """
        Save current session

        Args:
            session_name: Name for the session
            apps: Optional list of apps to save, if None will detect current apps

        Returns:
            True if successful, False otherwise
        """
        if apps is None:
            apps = self.get_running_apps()

        if not apps:
            print("Warning: No applications found to save")
            return False

        self.sessions[session_name] = {
            'created': datetime.now().isoformat(),
            'apps': apps
        }

        self._save_sessions()
        print(f"✓ Session '{session_name}' saved with {len(apps)} application(s)")
        return True

    def load_session(self, session_name: str) -> bool:
        """
        Load and execute a saved session

        Args:
            session_name: Name of the session to load

        Returns:
            True if successful, False otherwise
        """
        if session_name not in self.sessions:
            print(f"Error: Session '{session_name}' not found")
            return False

        session = self.sessions[session_name]
        apps = session['apps']

        print(f"Loading session '{session_name}' with {len(apps)} application(s)...")

        success_count = 0
        for app in apps:
            try:
                # Parse command to handle spaces and arguments properly
                cmd = app['command'].split()

                # Launch in background
                subprocess.Popen(cmd,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               start_new_session=True)

                print(f"  ✓ Launched: {app['name']}")
                success_count += 1

            except Exception as e:
                print(f"  ✗ Failed to launch {app['name']}: {e}")

        print(f"\n✓ Successfully launched {success_count}/{len(apps)} application(s)")
        return True

    def delete_session(self, session_name: str) -> bool:
        """
        Delete a saved session

        Args:
            session_name: Name of the session to delete

        Returns:
            True if successful, False otherwise
        """
        if session_name not in self.sessions:
            print(f"Error: Session '{session_name}' not found")
            return False

        del self.sessions[session_name]
        self._save_sessions()
        print(f"✓ Session '{session_name}' deleted")
        return True

    def update_session(self, session_name: str, remove_indices: Optional[List[int]] = None) -> bool:
        """
        Update a session by removing specific apps

        Args:
            session_name: Name of the session to update
            remove_indices: List of app indices to remove (0-based)

        Returns:
            True if successful, False otherwise
        """
        if session_name not in self.sessions:
            print(f"Error: Session '{session_name}' not found")
            return False

        session = self.sessions[session_name]
        apps = session['apps']

        if not remove_indices:
            print("No apps specified to remove")
            return False

        # Sort in reverse to avoid index shifting issues
        remove_indices = sorted(set(remove_indices), reverse=True)

        removed_count = 0
        for idx in remove_indices:
            if 0 <= idx < len(apps):
                removed_app = apps.pop(idx)
                print(f"  ✓ Removed: {removed_app['name']}")
                removed_count += 1
            else:
                print(f"  ✗ Invalid index: {idx}")

        if removed_count > 0:
            session['apps'] = apps
            self._save_sessions()
            print(f"\n✓ Updated session '{session_name}', removed {removed_count} app(s)")
            return True

        return False

    def list_sessions(self) -> Dict:
        """
        Get all saved sessions

        Returns:
            Dictionary of all sessions
        """
        return self.sessions

    def show_session(self, session_name: str):
        """
        Display details of a specific session

        Args:
            session_name: Name of the session to show
        """
        if session_name not in self.sessions:
            print(f"Error: Session '{session_name}' not found")
            return

        session = self.sessions[session_name]
        print(f"\nSession: {session_name}")
        print(f"Created: {session['created']}")
        print(f"Applications ({len(session['apps'])}):")

        for idx, app in enumerate(session['apps']):
            print(f"  [{idx}] {app['name']}")
            print(f"      Command: {app['command']}")
