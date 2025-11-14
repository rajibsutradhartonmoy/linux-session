# Building Linux Session Saver

This guide will help you build the Linux Session Saver application from source.

## Prerequisites

### 1. Install Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

Verify installation:
```bash
rustc --version
cargo --version
```

### 2. Install Node.js and npm

#### Debian/Ubuntu
```bash
sudo apt update
sudo apt install nodejs npm
```

#### Fedora/RHEL
```bash
sudo dnf install nodejs npm
```

#### Arch Linux
```bash
sudo pacman -S nodejs npm
```

### 3. Install Tauri Dependencies

#### Debian/Ubuntu
```bash
sudo apt install libwebkit2gtk-4.0-dev \
    build-essential \
    curl \
    wget \
    file \
    libssl-dev \
    libgtk-3-dev \
    libayatana-appindicator3-dev \
    librsvg2-dev
```

#### Fedora/RHEL
```bash
sudo dnf install webkit2gtk4.0-devel \
    openssl-devel \
    curl \
    wget \
    file \
    libappindicator-gtk3-devel \
    librsvg2-devel
```

#### Arch Linux
```bash
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

### 4. Install wmctrl (Optional but Recommended)

For better application detection:

```bash
# Debian/Ubuntu
sudo apt install wmctrl

# Fedora/RHEL
sudo dnf install wmctrl

# Arch Linux
sudo pacman -S wmctrl
```

## Building

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd linux-session-saver
npm install
```

### 2. Development Build

To run in development mode with hot-reload:

```bash
npm run tauri dev
```

This will:
- Compile the Rust backend
- Launch the application
- Enable auto-reload on file changes

### 3. Production Build

To create an optimized production build:

```bash
npm run tauri build
```

This will create:
- Binary executable in `src-tauri/target/release/linux-session-saver`
- .deb package in `src-tauri/target/release/bundle/deb/`
- AppImage in `src-tauri/target/release/bundle/appimage/`
- Other formats based on your system

## Installing

### Option 1: Debian/Ubuntu (.deb package)

```bash
sudo dpkg -i src-tauri/target/release/bundle/deb/linux-session-saver_*.deb
```

### Option 2: AppImage (Universal)

```bash
chmod +x src-tauri/target/release/bundle/appimage/linux-session-saver_*.AppImage
./src-tauri/target/release/bundle/appimage/linux-session-saver_*.AppImage
```

You can move the AppImage to a convenient location:
```bash
mv src-tauri/target/release/bundle/appimage/linux-session-saver_*.AppImage ~/.local/bin/session-saver
```

### Option 3: Direct Binary

```bash
# Copy the binary to your local bin
cp src-tauri/target/release/linux-session-saver ~/.local/bin/session-saver

# Make sure ~/.local/bin is in your PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Troubleshooting Build Issues

### Rust not found
```bash
source $HOME/.cargo/env
# Or restart your terminal
```

### Missing system libraries
If you get errors about missing libraries, install the Tauri dependencies for your distribution (see step 3 above).

### Webkit errors
Make sure you have webkit2gtk installed:
```bash
# Debian/Ubuntu
sudo apt install libwebkit2gtk-4.0-dev

# Fedora
sudo dnf install webkit2gtk4.0-devel
```

### Node/npm version issues
Make sure you have a recent version of Node.js (v14 or higher):
```bash
node --version
npm --version
```

### Build takes too long
The first build will take longer as Rust compiles all dependencies. Subsequent builds will be much faster.

### Out of memory during build
If building on a low-memory system, try:
```bash
# Build with fewer parallel jobs
cargo build --release -j 2
```

## Clean Build

To start fresh:

```bash
# Clean Rust artifacts
cd src-tauri
cargo clean
cd ..

# Clean node modules
rm -rf node_modules
npm install

# Rebuild
npm run tauri build
```

## Build for Distribution

To create packages for distribution:

```bash
npm run tauri build
```

This creates platform-specific packages in `src-tauri/target/release/bundle/`:
- `deb/` - Debian/Ubuntu packages
- `appimage/` - Universal Linux AppImages
- `rpm/` - RPM packages (if configured)

## Next Steps

After building, see the main [README.md](README.md) for usage instructions.
