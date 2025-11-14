#!/bin/bash
# Installation script for Linux Session Saver

set -e

echo "Installing Linux Session Saver..."

# Make scripts executable
chmod +x session_saver.py session_manager.py

# Create ~/.local/bin if it doesn't exist
mkdir -p "$HOME/.local/bin"

# Create symlink
INSTALL_PATH="$HOME/.local/bin/session-saver"
SCRIPT_PATH="$(pwd)/session_saver.py"

if [ -L "$INSTALL_PATH" ]; then
    rm "$INSTALL_PATH"
fi

ln -s "$SCRIPT_PATH" "$INSTALL_PATH"

echo "✓ Created symlink: $INSTALL_PATH -> $SCRIPT_PATH"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo ""
    echo "⚠ Warning: ~/.local/bin is not in your PATH"
    echo ""
    echo "Add it by running:"
    echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
    echo "  source ~/.bashrc"
    echo ""
else
    echo "✓ ~/.local/bin is already in PATH"
fi

# Check for wmctrl
echo ""
if command -v wmctrl &> /dev/null; then
    echo "✓ wmctrl is installed (recommended for better app detection)"
else
    echo "⚠ wmctrl not found (optional but recommended)"
    echo ""
    echo "Install it for better app detection:"
    echo "  Debian/Ubuntu: sudo apt-get install wmctrl"
    echo "  Fedora/RHEL:   sudo dnf install wmctrl"
    echo ""
fi

echo ""
echo "✓ Installation complete!"
echo ""
echo "Usage:"
echo "  session-saver save <name>      # Save current session"
echo "  session-saver load <name>      # Load session"
echo "  session-saver list             # List sessions"
echo "  session-saver --help           # Show all commands"
echo ""
