# Troubleshooting Guide

Common issues and solutions for YatsurugiCapture.

## Installation Issues

### PyQt5 DLL Load Failed (Windows)

**Error:**
```
ImportError: DLL load failed while importing QtWidgets: The specified module could not be found.
```

**Cause:** PyQt5 version 5.15.11 has DLL loading issues on some Windows systems.

**Solution:**
```bash
# Uninstall current PyQt5
pip uninstall PyQt5 PyQt5-Qt5 PyQt5-sip -y

# Install compatible version
pip install PyQt5==5.15.10

# Or reinstall from requirements
pip install -r requirements.txt
```

**Prevention:** The requirements.txt now pins PyQt5 to avoid this issue.

### PyAudio Installation Fails

**Error:**
```
error: Microsoft Visual C++ 14.0 or greater is required
```

**Solutions:**

**Option 1: Pre-built wheel**
```bash
pip install pipwin
pipwin install pyaudio
```

**Option 2: Unofficial binaries** (Windows)
Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
```bash
pip install PyAudio‑0.2.13‑cp313‑cp313‑win_amd64.whl
```

**Option 3: Install PortAudio first**
```bash
# Linux
sudo apt-get install portaudio19-dev  # Debian/Ubuntu
sudo pacman -S portaudio               # Arch

# Then
pip install pyaudio
```

### Module Not Found After Installing

**Error:**
```
ModuleNotFoundError: No module named 'audio_handler'
```

**Cause:** Running from wrong directory or Python path issue.

**Solution:**
```bash
# Ensure you're in project root
cd /path/to/YatsurugiCapture

# Run with correct path
python3 src/capture_app.py

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python3 src/capture_app.py
```

## Runtime Issues

### No Capture Devices Detected

**Error:** "No devices found" or empty device list

**Solutions:**

1. **Check v4l-utils installed:**
   ```bash
   v4l2-ctl --list-devices
   ```
   If command not found: `sudo pacman -S v4l-utils`

2. **Check device permissions:**
   ```bash
   ls -l /dev/video*
   ```
   If permission denied:
   ```bash
   sudo usermod -a -G video $USER
   # Logout and login again
   ```

3. **Check device is recognized:**
   ```bash
   lsusb  # Should show your capture card
   dmesg | grep -i video  # Check kernel messages
   ```

### Audio Passthrough Not Working

**Issue:** No audio or "Failed to start audio passthrough"

**Solutions:**

1. **Check PortAudio installed:**
   ```bash
   pacmd list-sources  # PulseAudio
   # or
   pactl list short sources
   ```

2. **Check audio device selected:**
   - Select correct audio device from dropdown
   - Try "None" and then reselect

3. **Check PulseAudio running:**
   ```bash
   systemctl --user status pulseaudio
   # Or
   pulseaudio --check
   ```

4. **Restart PulseAudio:**
   ```bash
   pulseaudio -k
   pulseaudio --start
   ```

### Application Crashes on Startup

**Symptom:** Application closes immediately or segfaults

**Solutions:**

1. **Run with debug output:**
   ```bash
   python3 src/capture_app.py 2>&1 | tee debug.log
   ```

2. **Check Qt platform:**
   ```bash
   export QT_DEBUG_PLUGINS=1
   python3 src/capture_app.py
   ```

3. **Try different Qt platform:**
   ```bash
   export QT_QPA_PLATFORM=xcb  # or wayland
   python3 src/capture_app.py
   ```

### Recording Fails or Produces Corrupt Files

**Issue:** Can't start recording or files won't play

**Solutions:**

1. **Check disk space:**
   ```bash
   df -h
   ```

2. **Try different codec/format:**
   - Save as .mkv instead of .mp4
   - Use .avi for compatibility

3. **Check write permissions:**
   ```bash
   touch /path/to/save/test.txt
   ```

4. **Check FFmpeg/codecs:**
   ```bash
   ffmpeg -codecs | grep -i h264
   ```

## Test Issues

### Tests Can't Find Modules

**Error:**
```
ModuleNotFoundError: No module named 'audio_handler'
```

**Solution:**
```bash
# Run from project root
cd /path/to/YatsurugiCapture
pytest tests/

# Or if that fails, ensure conftest.py exists
ls tests/conftest.py
```

### Tests Fail with PyQt5 Errors

**Error:** X server or display errors

**Solution:**
```bash
# Use offscreen platform
export QT_QPA_PLATFORM=offscreen
pytest tests/
```

Or tests set this automatically - check `test_capture_app.py`.

### Pytest Not Found

**Error:**
```
ModuleNotFoundError: No module named pytest
```

**Solution:**
```bash
pip install pytest pytest-mock
# Or
pip install -r requirements-dev.txt
```

## Build Issues

### PyInstaller Build Fails

**Issue:** Can't create executable

**Solutions:**

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Clear cache:**
   ```bash
   rm -rf build/ dist/
   pyinstaller YatsurugiCapture.spec
   ```

3. **Check hidden imports:**
   Edit `YatsurugiCapture.spec` to add missing modules.

### Built Binary Won't Run

**Issue:** Executable crashes or shows errors

**Solutions:**

1. **Run from terminal to see errors:**
   ```bash
   ./dist/YatsurugiCapture
   ```

2. **Check system dependencies:**
   ```bash
   ldd dist/YatsurugiCapture  # Linux
   # Ensure v4l-utils, portaudio are installed
   ```

3. **Rebuild with debug:**
   ```bash
   pyinstaller --debug all YatsurugiCapture.spec
   ```

## Performance Issues

### High CPU Usage

**Solutions:**

1. **Lower resolution:**
   - Use 720p instead of 1080p or 4K

2. **Lower FPS:**
   - Use 30fps instead of 60fps

3. **Close other applications**

4. **Check if hardware acceleration is working:**
   - OpenCV may be using CPU only

### Laggy Video / Dropped Frames

**Solutions:**

1. **Reduce buffer size:**
   Already optimized in code (`CAP_PROP_BUFFERSIZE = 1`)

2. **Check USB bandwidth:**
   - Use USB 3.0 port
   - Disconnect other USB devices

3. **Use MJPEG format:**
   Already set in code for better performance

## Linux-Specific Issues

### Wayland vs X11

**Issue:** Application behaves differently on Wayland

**Solutions:**

1. **Force X11:**
   ```bash
   export QT_QPA_PLATFORM=xcb
   python3 src/capture_app.py
   ```

2. **Check session type:**
   ```bash
   echo $XDG_SESSION_TYPE
   ```

### V4L2 Permission Denied

**Error:**
```
Failed to open /dev/video0: Permission denied
```

**Solution:**
```bash
# Add user to video group
sudo usermod -a -G video $USER

# Logout and login, then verify
groups | grep video

# Or temporary fix (until reboot)
sudo chmod 666 /dev/video*
```

## Getting Help

If you're still having issues:

1. **Check existing issues:**
   https://github.com/yourusername/YatsurugiCapture/issues

2. **Create new issue with:**
   - Operating system and version
   - Python version (`python --version`)
   - Full error message
   - Steps to reproduce
   - Output of:
     ```bash
     pip list
     v4l2-ctl --list-devices
     ```

3. **For security issues:**
   See [SECURITY.md](../SECURITY.md) (if exists)

## Quick Fixes Summary

| Issue | Quick Fix |
|-------|-----------|
| PyQt5 DLL error | `pip install PyQt5==5.15.10` |
| No audio devices | `sudo pacman -S portaudio` |
| No video devices | `sudo usermod -a -G video $USER` |
| Import errors | Run from project root |
| Tests fail | `export QT_QPA_PLATFORM=offscreen` |
| High CPU | Lower resolution/FPS |
| Permission denied | Add to video group, logout/login |

## Additional Resources

- [README.md](../README.md) - Main documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development setup
- [DEPENDENCIES.md](DEPENDENCIES.md) - Dependency information
- [PYCHARM_SETUP.md](PYCHARM_SETUP.md) - IDE setup
