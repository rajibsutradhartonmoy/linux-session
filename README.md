# Linux Session Saver

A simple and powerful CLI tool to save and restore your Linux application sessions. Never lose your workspace setup again!

## Features

- 💾 **Save Sessions** - Capture all currently running applications in a named session
- 🚀 **Load Sessions** - Restore all applications from a saved session with one command
- 📋 **List Sessions** - View all your saved sessions
- 🗑️ **Delete Sessions** - Remove sessions you no longer need
- ✏️ **Update Sessions** - Remove specific apps from a saved session
- 🔍 **Scan Apps** - View currently running applications without saving

## Installation

### Prerequisites

- Python 3.6 or higher
- `wmctrl` (optional, for better app detection on X11)

Install `wmctrl` on Debian/Ubuntu:
```bash
sudo apt-get install wmctrl
```

On Fedora/RHEL:
```bash
sudo dnf install wmctrl
```

### Quick Install

```bash
chmod +x install.sh
./install.sh
```

This will:
- Make the script executable
- Create a symbolic link in `~/.local/bin/session-saver`
- Add `~/.local/bin` to your PATH if needed

### Manual Install

```bash
# Make scripts executable
chmod +x session_saver.py session_manager.py

# Create symlink (optional, for easy access)
mkdir -p ~/.local/bin
ln -sf "$(pwd)/session_saver.py" ~/.local/bin/session-saver

# Add to PATH if not already there
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Usage

### Save Current Session

Save all currently running applications:

```bash
./session_saver.py save my-work-session
```

Or if installed:
```bash
session-saver save my-work-session
```

### Load a Session

Restore all applications from a saved session:

```bash
./session_saver.py load my-work-session
```

### List All Sessions

View all your saved sessions:

```bash
./session_saver.py list
```

Output:
```
Saved sessions (2):

  • my-work-session
    Created: 2025-11-14
    Apps: 5

  • gaming-session
    Created: 2025-11-13
    Apps: 3
```

### Show Session Details

View detailed information about a specific session:

```bash
./session_saver.py show my-work-session
```

Output:
```
Session: my-work-session
Created: 2025-11-14T10:30:45.123456
Applications (3):
  [0] Firefox
      Command: /usr/lib/firefox/firefox
  [1] Visual Studio Code
      Command: /usr/share/code/code
  [2] Terminal
      Command: gnome-terminal
```

### Delete a Session

Remove a session you no longer need:

```bash
./session_saver.py delete my-work-session
```

### Update a Session

Remove specific apps from a session using their indices (shown in `show` command):

```bash
# Remove apps at indices 0 and 2
./session_saver.py update my-work-session 0 2
```

### Scan Current Apps

View currently running applications without saving:

```bash
./session_saver.py scan
```

## How It Works

1. **Detection**: The app uses `wmctrl` to detect running GUI applications on X11 systems. If `wmctrl` is not available, it falls back to parsing process information.

2. **Storage**: Sessions are stored in JSON format at `~/.config/session-saver/sessions.json`

3. **Launching**: When loading a session, applications are launched using their original command-line arguments.

## Examples

### Daily Workflow

```bash
# Monday morning - start your work apps
session-saver load work

# End of day - save your current setup
session-saver save work-in-progress

# Tuesday morning - continue where you left off
session-saver load work-in-progress

# Clean up old sessions
session-saver list
session-saver delete work-in-progress
```

### Multiple Workspaces

```bash
# Create different sessions for different tasks
session-saver save development
session-saver save writing
session-saver save gaming
session-saver save browsing

# Switch between them easily
session-saver load development
session-saver load gaming
```

## Limitations

- **Wayland**: Works best on X11. On Wayland, app detection may be limited.
- **State**: The tool saves which applications to launch but doesn't save their internal state (open files, scroll positions, etc.)
- **Window Position**: Window positions and sizes are not saved (yet)
- **CLI Apps**: Only GUI applications are reliably detected

## Troubleshooting

### No apps detected

- Make sure `wmctrl` is installed: `sudo apt-get install wmctrl`
- Try the `scan` command to see what apps are being detected
- Some applications may not be visible to process scanning

### App won't launch

- Check that the application is still installed
- Use `show` command to verify the command is correct
- Some apps may require specific environment variables or working directories

### Permission denied

- Make sure the script is executable: `chmod +x session_saver.py`
- Check that `~/.local/bin` is in your PATH

## Configuration

Sessions are stored at: `~/.config/session-saver/sessions.json`

You can manually edit this file if needed, but be careful with the JSON syntax.

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## License

MIT License - feel free to use and modify as needed.

## Author

Created for easy session management on Linux systems.
