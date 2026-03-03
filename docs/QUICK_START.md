# Quick Start Guide

## For End Users

### Download and Run (No Python Needed!)

1. **Download** the latest release from [Releases page](https://github.com/yourusername/YatsurugiCapture/releases)
   - Linux: `YatsurugiCapture-linux-x64.tar.gz`
   - Windows: `YatsurugiCapture-windows-x64.zip`

2. **Extract and run**:
   ```bash
   # Linux
   tar -xzf YatsurugiCapture-linux-x64.tar.gz
   chmod +x YatsurugiCapture
   ./YatsurugiCapture
   ```

3. **Install desktop entry** (optional, Linux only):
   ```bash
   scripts/install_desktop.sh
   ```

## For Developers

### Quick Setup

```bash
# Clone repository
git clone https://github.com/yourusername/YatsurugiCapture.git
cd YatsurugiCapture

# Install dependencies (Linux)
sudo pacman -S python-pyqt5 v4l-utils portaudio  # Arch/CachyOS

# Install Python packages
pip install -r requirements.txt

# Run application
python3 src/capture_app.py
```

### Build Release

```bash
# Generate icons
scripts/create_icons.sh

# Build
scripts/build_release.sh

# Output in dist/YatsurugiCapture
```

### Run Tests

```bash
pytest tests/
```

## Project Automation

✅ **Automated dependency updates** - Dependabot handles this weekly
✅ **Security scanning** - CodeQL checks for vulnerabilities
✅ **CI/CD releases** - Push a tag to trigger builds

```bash
# Create a new release
git tag v1.0.0
git push origin v1.0.0
# GitHub Actions automatically builds binaries
```

## Key Features

- 🎮 Capture from V4L2 devices (capture cards, webcams)
- 🔊 Audio passthrough
- 📹 Record to MP4/AVI/MKV
- 🖥️ Borderless mode for streaming
- ⚙️ Configurable resolution & FPS

## Documentation

- [README.md](../README.md) - Full documentation
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Project organization
- [DEPENDENCY_MANAGEMENT.md](DEPENDENCY_MANAGEMENT.md) - Keeping dependencies updated

## Support

- 🐛 [Report bugs](https://github.com/yourusername/YatsurugiCapture/issues)
- 💡 [Request features](https://github.com/yourusername/YatsurugiCapture/issues)
- 🔒 [Security issues](https://github.com/yourusername/YatsurugiCapture/security)
