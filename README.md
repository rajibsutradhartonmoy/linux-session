# Linux Session Saver

<div align="center">

A beautiful, modern GUI application to save and restore your Linux application sessions.

![Tauri](https://img.shields.io/badge/Tauri-1.5-blue)
![Rust](https://img.shields.io/badge/Rust-1.70+-orange)
![License](https://img.shields.io/badge/license-MIT-green)

**Never lose your workspace setup again!**

</div>

## ✨ Features

- 💾 **Save Sessions** - Capture all currently running applications in a named session
- 🚀 **Load Sessions** - Restore all applications from a saved session with one click
- 📋 **Manage Sessions** - View, edit, and delete your saved sessions
- ✏️ **Edit Sessions** - Remove specific apps from saved sessions
- 🔍 **Scan Apps** - View currently running applications in real-time
- 🎨 **Beautiful UI** - Modern, dark-themed interface built with Tauri
- ⚡ **Fast & Lightweight** - Built with Rust and web technologies

## 🖼️ Screenshots

### Sessions View
View and manage all your saved sessions with a clean, modern interface.

### Current Apps
Scan and save your currently running applications.

## 🚀 Quick Start

### Prerequisites

Before building the application, you need:

1. **Rust** (1.70 or higher)
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. **Node.js and npm** (for Tauri CLI)
   ```bash
   # Debian/Ubuntu
   sudo apt install nodejs npm

   # Fedora/RHEL
   sudo dnf install nodejs npm
   ```

3. **System Dependencies** (for Tauri)
   ```bash
   # Debian/Ubuntu
   sudo apt install libwebkit2gtk-4.0-dev \
       build-essential \
       curl \
       wget \
       file \
       libssl-dev \
       libgtk-3-dev \
       libayatana-appindicator3-dev \
       librsvg2-dev

   # Fedora/RHEL
   sudo dnf install webkit2gtk4.0-devel \
       openssl-devel \
       curl \
       wget \
       file \
       libappindicator-gtk3-devel \
       librsvg2-devel

   # Arch Linux
   sudo pacman -S webkit2gtk \
       base-devel \
       curl \
       wget \
       file \
       openssl \
       appmenu-gtk-module \
       gtk3 \
       libappindicator-gtk3 \
       librsvg
   ```

4. **wmctrl** (optional, for better app detection)
   ```bash
   # Debian/Ubuntu
   sudo apt install wmctrl

   # Fedora/RHEL
   sudo dnf install wmctrl

   # Arch Linux
   sudo pacman -S wmctrl
   ```

### Building from Source

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd linux-session-saver
   ```

2. **Install Tauri CLI**
   ```bash
   npm install
   ```

3. **Build the application**
   ```bash
   npm run tauri build
   ```

   The compiled application will be in `src-tauri/target/release/`

4. **Install the application**
   ```bash
   # The .deb or .AppImage will be in src-tauri/target/release/bundle/
   # For Debian/Ubuntu:
   sudo dpkg -i src-tauri/target/release/bundle/deb/*.deb

   # Or use the AppImage:
   chmod +x src-tauri/target/release/bundle/appimage/*.AppImage
   ./src-tauri/target/release/bundle/appimage/*.AppImage
   ```

### Development Mode

To run the application in development mode:

```bash
npm run tauri dev
```

## 📖 Usage

### 1. Scan Current Applications

1. Open the application
2. Go to the **"Current Apps"** tab
3. Click the **"Scan"** button
4. You'll see all your currently running applications

### 2. Save a Session

1. After scanning apps, enter a name for your session
2. Click **"Save Session"**
3. Your session is now saved!

### 3. Load a Session

1. Go to the **"Sessions"** tab
2. Find the session you want to restore
3. Click the **"Load"** button
4. All applications from that session will launch

### 4. Edit a Session

1. In the **"Sessions"** tab, click **"Edit"** on any session
2. Select the apps you want to remove (checkboxes appear)
3. Click **"Remove Selected"**
4. The session is updated without those apps

### 5. Delete a Session

1. In the **"Sessions"** tab, click **"Delete"** on any session
2. Confirm the deletion
3. The session is permanently removed

## 🏗️ Architecture

This application is built with:

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Rust with Tauri framework
- **UI Framework**: Custom CSS with modern design
- **Data Storage**: JSON files in `~/.config/session-saver/`

### Project Structure

```
linux-session-saver/
├── ui/                      # Frontend files
│   ├── index.html          # Main HTML
│   ├── styles.css          # Styling
│   └── app.js              # JavaScript logic
├── src-tauri/              # Rust backend
│   ├── src/
│   │   └── main.rs         # Main Rust code
│   ├── Cargo.toml          # Rust dependencies
│   ├── tauri.conf.json     # Tauri configuration
│   └── build.rs            # Build script
├── package.json            # Node.js dependencies
└── README.md              # This file
```

## 💾 Data Storage

Sessions are stored in JSON format at:
```
~/.config/session-saver/sessions.json
```

The file structure is:
```json
{
  "sessions": {
    "session-name": {
      "created": "2025-11-14T10:30:00Z",
      "apps": [
        {
          "name": "Firefox",
          "command": "/usr/lib/firefox/firefox",
          "pid": "1234"
        }
      ]
    }
  }
}
```

## 🔧 How It Works

1. **App Detection**:
   - Uses `wmctrl` to detect running GUI applications on X11
   - Falls back to `ps` command if `wmctrl` is not available
   - Reads `/proc/{pid}/cmdline` to get full command details

2. **Session Storage**:
   - Sessions stored as JSON in user's config directory
   - Each session contains app names, commands, and metadata

3. **App Launching**:
   - Uses the original command-line arguments to relaunch apps
   - Spawns processes in the background

## ⚠️ Limitations

- **Wayland**: Works best on X11. On Wayland, app detection may be limited
- **State**: Saves which apps to launch, but not their internal state (open files, window positions, etc.)
- **Window Management**: Window positions and sizes are not saved
- **CLI Apps**: Only GUI applications are reliably detected
- **Some Apps**: Apps that require specific environment variables or working directories may not launch correctly

## 🐛 Troubleshooting

### No apps detected
- Make sure `wmctrl` is installed: `sudo apt install wmctrl`
- Check that you're running X11 (not Wayland)
- Some applications may not be visible to process scanning

### App won't launch from session
- Verify the application is still installed
- Check that the command path is still valid
- Some apps may require specific environment setup

### Build errors
- Ensure all system dependencies are installed
- Update Rust: `rustup update`
- Clear build cache: `cargo clean` in `src-tauri/` directory

### Permission denied
- Make sure you have write permissions to `~/.config/session-saver/`
- Check file permissions on the sessions.json file

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📝 Todo / Future Features

- [ ] Save window positions and sizes
- [ ] Support for Wayland
- [ ] Auto-save sessions on logout
- [ ] Session groups/categories
- [ ] Import/export sessions
- [ ] Scheduled session loading
- [ ] System tray integration
- [ ] Workspace switching support

## 📄 License

MIT License - feel free to use and modify as needed.

## 🙏 Acknowledgments

- Built with [Tauri](https://tauri.app/) - A framework for building desktop applications
- Uses `wmctrl` for window management on Linux
- Inspired by session management tools on other platforms

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Open an issue on GitHub
3. Consult the [Tauri documentation](https://tauri.app/v1/guides/)

---

<div align="center">

**Made with ❤️ for the Linux community**

</div>
