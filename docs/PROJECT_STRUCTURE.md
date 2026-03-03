# YatsurugiCapture Project Structure

This document explains the project organization and what each directory contains.

## Directory Layout

```
YatsurugiCapture/
├── src/                    # Source code
├── tests/                  # Unit tests
├── scripts/                # Build and utility scripts
├── assets/                 # Icons, desktop files, and resources
├── docs/                   # Documentation
├── .github/workflows/      # CI/CD pipelines
└── [config files]          # Root-level configuration
```

## Directory Details

### `src/`
Contains the main application source code:
- **`capture_app.py`** - Main GUI application with PyQt5
- **`audio_handler.py`** - Audio capture and passthrough module

### `tests/`
Unit tests for the application:
- **`test_capture_app.py`** - Tests for main application
- **`test_audio_handler.py`** - Tests for audio module

Run tests with: `pytest tests/`

### `scripts/`
Build and installation scripts:
- **`build_release.sh`** - Linux build script
- **`build_release.bat`** - Windows build script
- **`create_icons.sh`** - Generate PNG icons from SVG
- **`install_desktop.sh`** - Install desktop entry on Linux

### `assets/`
Application resources:
- **`icon.svg`** - Source icon file (version controlled)
- **`YatsurugiCapture.desktop`** - Linux desktop entry
- **`icons/`** - Generated PNG icons (gitignored)
- **`icon.ico`** - Windows icon file (gitignored)

### `docs/`
Documentation files:
- This file and other documentation

### `.github/workflows/`
CI/CD automation:
- **`build-release.yml`** - Automated release builds for Linux and Windows

## Configuration Files (Root)

- **`requirements.txt`** - Python dependencies
- **`YatsurugiCapture.spec`** - PyInstaller build configuration
- **`.gitignore`** - Git ignore rules
- **`README.md`** - Project README

## Build Artifacts (Gitignored)

The following directories are created during builds but not committed:
- **`build/`** - Temporary PyInstaller build files
- **`dist/`** - Final executable output
- **`assets/icons/`** - Generated icon files
- **`__pycache__/`** - Python bytecode cache

## Running the Application

### From Source
```bash
python3 src/capture_app.py
```

### Building Release
```bash
# Generate icons (optional)
scripts/create_icons.sh

# Build executable
scripts/build_release.sh
```

### Installing Desktop Entry
```bash
scripts/install_desktop.sh
```

## Development Workflow

1. **Make changes** in `src/` directory
2. **Add tests** in `tests/` directory
3. **Run tests**: `pytest tests/`
4. **Build locally**: `scripts/build_release.sh`
5. **Commit and push** to GitHub
6. **Tag release**: `git tag v1.0.0 && git push origin v1.0.0`
7. **CI/CD automatically builds** binaries for Linux and Windows

## Benefits of This Structure

✅ **Clean separation** - Source, tests, scripts, and assets are organized
✅ **Easy to navigate** - Clear purpose for each directory
✅ **Standard layout** - Follows Python project conventions
✅ **CI/CD friendly** - Scripts work from any directory
✅ **Maintainable** - Easy for contributors to understand
