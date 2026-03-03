# Dependencies Explained

This document explains the project dependencies and different installation methods.

## Runtime Dependencies

These are required to run YatsurugiCapture:

| Package | Purpose | Why Required |
|---------|---------|--------------|
| **opencv-python** | Video capture and processing | Interfaces with V4L2, handles video frames |
| **PyQt5** | GUI framework | Window, buttons, layouts, UI elements |
| **pyaudio** | Audio capture and playback | Audio passthrough from capture card |
| **numpy** | Array operations | Used by OpenCV and in tests |

## System Dependencies

These must be installed via your package manager:

| Package | Purpose | Platform |
|---------|---------|----------|
| **v4l-utils** | Video4Linux utilities | Linux only |
| **portaudio** | Audio I/O library | All platforms |
| **python3-dev** | Python headers | Build dependencies |

## PyQt5 vs python-qt5/python-pyqt5

### The Confusion

Different platforms have different package names for the same thing:

| Platform | pip package | System package |
|----------|-------------|----------------|
| **All platforms** | `PyQt5` | N/A |
| **Arch/CachyOS** | `PyQt5` | `python-pyqt5` |
| **Ubuntu/Debian** | `PyQt5` | `python3-pyqt5` |
| **Fedora** | `PyQt5` | `python3-qt5` |

### What's the Difference?

**pip package (`PyQt5`):**
- Installed with: `pip install PyQt5`
- Cross-platform (Windows, macOS, Linux)
- Includes bundled Qt libraries
- Consistent versions across platforms
- Required for PyInstaller builds

**System package (`python-pyqt5` etc.):**
- Installed with: `pacman -S python-pyqt5` (Arch)
- Linux distribution packages
- Uses system Qt libraries
- Managed by package manager
- Better system integration

### Which Should You Use?

**For Development:** Use **pip** (`PyQt5`)
- ✅ Consistent across all contributors
- ✅ Works everywhere
- ✅ Required for building executables
- ✅ Easier to manage versions

**For Personal Use (Arch only):** Either works
- System package: Better integration, updates via pacman
- pip package: Consistent with development

## Installation Methods

### Method 1: pip (Recommended)

```bash
# System dependencies
sudo pacman -S v4l-utils portaudio  # Arch/CachyOS

# Python packages
pip install -r requirements.txt
```

**Pros:**
- ✅ Cross-platform
- ✅ Consistent versions
- ✅ Works with PyInstaller
- ✅ Easy to update

**Cons:**
- ⚠️ Larger download (includes Qt binaries)
- ⚠️ Separate from system package manager

### Method 2: System Packages (Arch only)

```bash
# Everything via pacman
sudo pacman -S python-pyqt5 python-opencv v4l-utils portaudio

# Only pyaudio via pip (not in official repos)
pip install pyaudio
```

**Pros:**
- ✅ Integrates with system Qt
- ✅ Updates via pacman
- ✅ Smaller footprint (reuses system libraries)

**Cons:**
- ⚠️ Arch/CachyOS specific
- ⚠️ Different versions than other platforms
- ⚠️ May not work for building with PyInstaller

### Method 3: Virtual Environment (Development)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements-dev.txt
```

**Pros:**
- ✅ Isolated from system
- ✅ No conflicts with other projects
- ✅ Easy to clean up

**Cons:**
- ⚠️ Need to activate before running
- ⚠️ Takes more disk space

## For End Users (Binary Release)

**No Python dependencies needed!**

The PyInstaller-built executables bundle everything:
- ✅ Python interpreter
- ✅ All Python packages (PyQt5, OpenCV, etc.)
- ✅ Qt libraries

Users only need:
```bash
sudo pacman -S v4l-utils portaudio
```

## Development Dependencies

Additional packages in `requirements-dev.txt`:

| Package | Purpose |
|---------|---------|
| **pytest** | Running tests |
| **pytest-mock** | Mocking in tests |
| **pytest-cov** | Code coverage |
| **autoflake** | Remove unused imports |
| **pylint** | Code linting |
| **flake8** | Style checking |
| **black** | Code formatting |
| **mypy** | Type checking |
| **pyinstaller** | Building executables |

## Dependency Management

### Updating Dependencies

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update all (carefully!)
pip install --upgrade -r requirements.txt
```

### Automated Updates

Dependabot automatically:
- Checks for updates weekly
- Creates PRs for new versions
- Includes changelogs and compatibility info

See [DEPENDENCY_MANAGEMENT.md](DEPENDENCY_MANAGEMENT.md) for details.

## Troubleshooting

### "ModuleNotFoundError: No module named 'PyQt5'"

**Solution:**
```bash
pip install PyQt5
# or
sudo pacman -S python-pyqt5
```

### "ModuleNotFoundError: No module named 'cv2'"

**Solution:**
```bash
pip install opencv-python
# or
sudo pacman -S python-opencv
```

### "PyAudio not found" or build errors

**Solution:**
```bash
# Install PortAudio first
sudo pacman -S portaudio

# Then install PyAudio
pip install pyaudio
```

### "Import errors after system package install"

If you installed system packages but still get import errors:
```bash
# Uninstall pip versions first
pip uninstall PyQt5 opencv-python

# Then system packages should work
sudo pacman -S python-pyqt5 python-opencv
```

## Recommendations

### For Contributors
Use **pip** (`requirements-dev.txt`) - ensures consistency

### For Arch Users (Personal Use)
Either works, but **pip is recommended** for easier updates

### For Binary Releases
Use **PyInstaller** - bundles everything automatically

## Summary

- **Keep `PyQt5` in requirements.txt** ✅
- **`python-qt5` is just the Arch package name** for the same library
- **Both work**, but pip is more consistent across platforms
- **For development**, always use pip
- **For binary releases**, users need neither (bundled by PyInstaller)
