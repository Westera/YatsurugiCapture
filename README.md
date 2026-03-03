# YatsurugiCapture

[![CodeQL](https://github.com/yourusername/YatsurugiCapture/workflows/CodeQL%20Security%20Scan/badge.svg)](https://github.com/yourusername/YatsurugiCapture/actions)
[![Dependency Review](https://github.com/yourusername/YatsurugiCapture/workflows/Dependency%20Review/badge.svg)](https://github.com/yourusername/YatsurugiCapture/actions)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

A Linux video capture application designed for capturing and displaying video from capture cards (like Elgato HD60+)
with audio passthrough support. Perfect for Discord screen sharing, game streaming, and recording.

## Features

- 🎮 Real-time video capture from V4L2 compatible devices
- 🔊 Audio passthrough with auto-detection of capture card audio
- 📹 Video recording in multiple formats (MP4, AVI, MKV)
- 🖥️ Borderless mode for clean streaming
- ⚙️ Configurable resolution and FPS
- 🎯 Low-latency capture optimized for gaming
- 📊 Support for resolutions up to 4K (3840x2160)

## Prerequisites

### For Pre-built Binary Users
- **Linux**: V4L2 compatible capture device, v4l-utils, and portaudio
- **Windows**: Compatible capture card (note: limited V4L2 support on Windows)

### For Source Code Users
- Linux operating system (recommended)
- Python 3.7 or higher
- V4L2 compatible capture device (e.g., Elgato HD60+, capture card, or webcam)
- System packages: v4l-utils, portaudio

> **Note:** See [docs/DEPENDENCIES.md](docs/DEPENDENCIES.md) for detailed dependency information and installation options.

## Installation

### Option 1: Download Pre-built Binary (Recommended)

**No Python installation required!**

1. Download the latest release from the [Releases](https://github.com/yourusername/YatsurugiCapture/releases) page
   - **Linux**: `YatsurugiCapture-linux-x64.tar.gz`
   - **Windows**: `YatsurugiCapture-windows-x64.zip`

2. Extract the archive:
   ```bash
   # Linux
   tar -xzf YatsurugiCapture-linux-x64.tar.gz
   chmod +x YatsurugiCapture

   # Windows
   # Extract using Windows Explorer or: tar -xzf YatsurugiCapture-windows-x64.zip
   ```

3. Install system dependencies (Linux only):
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install v4l-utils portaudio19-0

   # Fedora/RHEL
   sudo dnf install v4l-utils portaudio

   # Arch Linux
   sudo pacman -S v4l-utils portaudio
   ```

4. Run the application:
   ```bash
   # Linux - Run directly
   ./YatsurugiCapture

   # Windows
   YatsurugiCapture.exe
   ```

5. **Optional**: Create desktop entry (Linux only):
   ```bash
   # Make the installer script executable
   chmod +x scripts/install_desktop.sh

   # Run the installer
   scripts/install_desktop.sh

   # Choose option 1 (system-wide) or 2 (user-only)
   ```

   After installation, you can:
   - Launch from your application menu (search for "YatsurugiCapture")
   - Add to desktop: Right-click desktop → Create Link → Browse to installed location
   - Add to taskbar/panel by right-clicking the application icon
   - For KDE Plasma: Right-click desktop → Add Widget → Application Launcher

### Option 2: Run from Source

If you prefer to run from source or want to develop:

1. Clone or download this repository:
```bash
git clone https://github.com/yourusername/YatsurugiCapture.git
cd YatsurugiCapture
```

2. Install dependencies:

   **Option A: Using pip (Recommended - Cross-platform)**
   ```bash
   # Install system dependencies first
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install v4l-utils portaudio19-dev python3-dev

   # Fedora/RHEL
   sudo dnf install v4l-utils portaudio-devel python3-devel

   # Arch/CachyOS
   sudo pacman -S v4l-utils portaudio

   # Then install Python packages
   pip install -r requirements.txt
   ```

   **Option B: Using system packages (Arch/CachyOS only)**
   ```bash
   # Install everything via pacman
   sudo pacman -S python-pyqt5 python-opencv v4l-utils portaudio

   # Still need pyaudio via pip (not in official repos)
   pip install pyaudio
   ```

4. Run the application:
```bash
python3 src/capture_app.py
```

## Usage

### Basic Usage

Start the application:
```bash
python3 src/capture_app.py
```

### Step-by-Step Guide

1. **Launch the application**
   ```bash
   python3 src/capture_app.py
   ```

2. **Select your capture device**
   - Choose your capture card or webcam from the "Capture Device" dropdown
   - The application automatically detects all V4L2 devices

3. **Configure settings**
   - **Resolution**: Choose from 4K, 2K, 1080p, 720p, or 480p
   - **FPS**: Select 60 (smooth motion), 30 (standard), or 25 fps
   - **Audio Device**: Select audio input (auto-detects capture card audio)

4. **Start capturing**
   - Click "Start Capture" to begin displaying video
   - Video will appear in the main window

5. **Enable audio passthrough (optional)**
   - Check "Audio Passthrough" to hear audio from the capture source in real-time

6. **Record video (optional)**
   - Click "Start Recording" to save video to a file
   - Choose output format (MP4, AVI, or MKV) and location

7. **Borderless mode**
   - Click "Toggle Borderless" for fullscreen capture without controls
   - Perfect for Discord screen sharing or OBS capture
   - Double-click the video or press ESC to exit borderless mode

### Common Use Cases

#### Discord Screen Sharing
```bash
# 1. Start the application
python3 src/capture_app.py

# 2. Select your capture card
# 3. Set resolution to 1920x1080 @ 30fps (recommended for Discord)
# 4. Click "Start Capture"
# 5. Click "Toggle Borderless" for clean capture
# 6. Share the YatsurugiCapture window in Discord
```

#### Recording Gameplay
```bash
# 1. Start the application
python3 src/capture_app.py

# 2. Configure settings:
#    - Resolution: 1920x1080 or higher
#    - FPS: 60 (for smooth gameplay)
# 3. Enable Audio Passthrough if you want to hear while playing
# 4. Click "Start Capture"
# 5. Click "Start Recording"
# 6. Choose file location and format
# 7. Click "Stop Recording" when done
```

#### Low-Latency Preview
```bash
# 1. Start the application
python3 src/capture_app.py

# 2. Select 1280x720 @ 60fps for minimal latency
# 3. Enable Audio Passthrough
# 4. Click "Start Capture"
```

## Keyboard Shortcuts

- **ESC** - Exit borderless mode
- **Double-click video** - Toggle borderless mode

## Troubleshooting

### No capture devices detected
- Ensure v4l-utils is installed: `sudo apt-get install v4l-utils`
- Check if your device is recognized: `v4l2-ctl --list-devices`
- Verify device permissions: `ls -l /dev/video*`
- Add user to video group: `sudo usermod -a -G video $USER` (logout/login required)

### Audio not working
- Install PortAudio: `sudo apt-get install portaudio19-dev`
- List audio devices: `pactl list short sources` (for PulseAudio)
- Check PyAudio installation: `pip install --upgrade pyaudio`

### Poor video quality or lag
- Reduce resolution (try 720p instead of 1080p)
- Lower FPS to 30 instead of 60
- Close other applications using the capture device
- Check system resources (CPU/Memory usage)

### Recording fails
- Ensure you have write permissions in the target directory
- Check available disk space
- Try a different video format (MKV is recommended for best quality)

### PyQt5 DLL errors (Windows)
- Error: "DLL load failed while importing QtWidgets"
- Solution: `pip install PyQt5==5.15.10`
- See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more details

> **📖 For more issues and solutions, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)**

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_capture_app.py

# Run with coverage
pytest tests/ --cov=src
```

### Building a Release

#### Automated CI/CD (Recommended)

Releases are automatically built via GitHub Actions when you push a tag:

```bash
# Create and push a new release tag
git tag v1.0.0
git push origin v1.0.0
```

This will:
- Build binaries for both Linux and Windows
- Generate SHA256 checksums
- Create a GitHub Release with downloadable assets
- Generate release notes automatically

You can also trigger a manual build from the GitHub Actions tab.

#### Manual Build (Local Development)

To create a standalone executable locally:

**Linux:**
```bash
# Install PyInstaller
pip install pyinstaller

# Generate icons (optional)
chmod +x scripts/create_icons.sh
scripts/create_icons.sh

# Build using the provided script
chmod +x scripts/build_release.sh
scripts/build_release.sh

# Or build manually
pyinstaller YatsurugiCapture.spec

# Create release package
cd dist
tar -czf YatsurugiCapture-linux-x64.tar.gz YatsurugiCapture
```

**Windows:**
```batch
REM Install PyInstaller
pip install pyinstaller

REM Build using the provided script
scripts\build_release.bat

REM Or build manually
pyinstaller YatsurugiCapture.spec

REM Create release package
cd dist
tar -czf YatsurugiCapture-windows-x64.zip YatsurugiCapture.exe
```

### Project Structure
```
YatsurugiCapture/
├── .github/
│   └── workflows/
│       └── build-release.yml           # CI/CD workflow for releases
├── src/
│   ├── capture_app.py                  # Main application with GUI
│   └── audio_handler.py                # Audio capture and passthrough
├── tests/
│   ├── test_capture_app.py             # Unit tests for capture app
│   └── test_audio_handler.py           # Unit tests for audio handler
├── scripts/
│   ├── build_release.sh                # Linux build script
│   ├── build_release.bat               # Windows build script
│   ├── create_icons.sh                 # Icon generation script
│   └── install_desktop.sh              # Desktop entry installer
├── assets/
│   ├── icon.svg                        # Application icon (SVG source)
│   ├── YatsurugiCapture.desktop        # Linux desktop entry file
│   ├── icons/                          # Generated PNG icons (gitignored)
│   └── icon.ico                        # Windows icon (gitignored)
├── docs/                               # Documentation (if any)
├── requirements.txt                    # Python dependencies
├── YatsurugiCapture.spec               # PyInstaller build specification
├── .gitignore                          # Git ignore rules
└── README.md                           # This file
```

## Security & Maintenance

This project uses automated tools to stay secure and up-to-date:

- 🔒 **Dependabot** - Automatic dependency updates (weekly)
- 🛡️ **CodeQL** - Security vulnerability scanning
- 📊 **Dependency Review** - Blocks vulnerable dependencies in PRs
- 🔍 **pip-audit** - Weekly security checks

See [docs/DEPENDENCY_MANAGEMENT.md](docs/DEPENDENCY_MANAGEMENT.md) for details.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines on:
- Setting up your development environment
- Code quality standards and tools
- Making pull requests
- Running tests and quality checks

## License

This project is licensed under the Apache License, Version 2.0. See the LICENSE file for details.

SPDX-License-Identifier: Apache-2.0

## Acknowledgments

- Built with OpenCV for video processing
- PyQt5 for the graphical interface
- PyAudio for audio handling
- Designed for Linux V4L2 capture devices
