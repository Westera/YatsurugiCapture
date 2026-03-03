# PyCharm Setup Guide

This guide explains how to set up PyCharm for YatsurugiCapture development and addresses common warnings.

## Quick Setup

1. **Open project in PyCharm**
   ```
   File → Open → Select YatsurugiCapture directory
   ```

2. **Configure Python interpreter**
   ```
   File → Settings → Project → Python Interpreter
   → Add Interpreter → Virtualenv or System Interpreter
   ```

3. **Install dependencies**
   ```
   pip install -r requirements-dev.txt
   ```

4. **Mark directories**
   ```
   Right-click `src/` → Mark Directory As → Sources Root
   Right-click `tests/` → Mark Directory As → Test Sources Root
   ```

## Understanding PyCharm Warnings

### ✅ False Alarms (Can Ignore)

#### "Package containing module 'PyQt5' is not listed in project requirements"
**Status:** False alarm
**Reason:** PyQt5 IS in requirements.txt, PyCharm sometimes doesn't detect it properly
**Solution:** Already configured in `.idea/inspectionProfiles/Project_Default.xml`

#### "Cannot find reference 'connect' in 'pyqtSignal'"
**Status:** False alarm
**Reason:** PyQt5 uses dynamic typing for signals, type stubs are incomplete
**Example:**
```python
self.timer.timeout.connect(self.update_frame)  # This is correct!
```
**Solution:** Already suppressed in inspection profile

#### "Cannot find reference 'VideoWriter_fourcc'"
**Status:** False alarm
**Reason:** OpenCV Python stubs are incomplete
**Example:**
```python
cv2.VideoWriter_fourcc('M','J','P','G')  # This exists!
```
**Solution:** Already suppressed in inspection profile

#### SQL-related warnings
**Status:** False alarm
**Example:**
```python
self.audio_combo.setToolTip("Select audio input device...")
# PyCharm thinks this is SQL!
```
**Solution:** Disabled SQL inspection in profile

### ✅ Fixed Issues

#### "Remove redundant parentheses"
**Status:** Fixed
**Before:**
```python
return (1920, 1080)
```
**After:**
```python
return 1920, 1080
```

#### "Parameter 'event' value is not used"
**Status:** Fixed
**Before:**
```python
def video_double_click(self, event):
```
**After:**
```python
def video_double_click(self, _event):  # Underscore indicates unused
```

### ⚠️ Known Limitations (Not Fixable)

#### "Instance attribute defined outside __init__"
**Status:** Informational - not critical
**Reason:** PyQt5 UI elements are created in `init_ui()` called from `__init__`
**This is fine:** Keeps UI code organized and readable

#### Type warnings for Qt methods
**Status:** PyQt5 type hints limitation
**Example:**
```python
scaled_pixmap = QPixmap.fromImage(qt_image).scaled(...)
# Warning: Type mismatch (but code works fine)
```
**Reason:** PyQt5's type stubs don't cover all overloads

## Suppressing Inspections

### Project-wide (Already Configured)
File: `.idea/inspectionProfiles/Project_Default.xml`

This file configures:
- Ignore PyQt5 signal warnings
- Ignore OpenCV stub warnings
- Disable SQL inspections for strings

### Per-file Suppression

Add at top of file:
```python
# noinspection PyUnresolvedReferences
```

### Per-line Suppression

```python
self.timer.timeout.connect(self.update_frame)  # noqa
```

## Recommended PyCharm Settings

### Code Style
```
Settings → Editor → Code Style → Python
→ Line length: 127 (matches black config)
```

### Inspections
```
Settings → Editor → Inspections → Python
→ Enable: PEP 8 coding style violation
→ Enable: Type checker
→ Disable: SQL (for this project)
```

### External Tools

Add Black formatter:
```
Settings → Tools → External Tools → Add
Name: Black
Program: black
Arguments: $FilePath$
Working directory: $ProjectFileDir$
```

Add Autoflake:
```
Settings → Tools → External Tools → Add
Name: Autoflake
Program: autoflake
Arguments: --in-place --remove-all-unused-imports $FilePath$
Working directory: $ProjectFileDir$
```

## Running the Application

### From PyCharm

1. Right-click `src/capture_app.py`
2. Select "Run 'capture_app'"

Or create run configuration:
```
Run → Edit Configurations → Add New (Python)
Script path: src/capture_app.py
Working directory: (project root)
```

### Running Tests

1. Right-click `tests/` directory
2. Select "Run 'pytest in tests'"

Or:
```
Terminal → pytest tests/
```

## Debugging

### Set Breakpoints
Click left gutter in editor to add breakpoint

### Start Debugging
Right-click → Debug 'capture_app'

### Debug Console
View variables, evaluate expressions

## Troubleshooting

### "Module not found" errors

**Check interpreter:**
```
Settings → Project → Python Interpreter
→ Verify all packages from requirements.txt are installed
```

**Reinstall dependencies:**
```bash
pip install -r requirements-dev.txt
```

### Inspection profile not loading

**Manually configure:**
```
Settings → Editor → Inspections
→ Profile: Project Default (should be auto-selected)
```

### PyCharm slow or laggy

**Exclude directories:**
```
Right-click on: build/, dist/, __pycache__/, .pytest_cache/
→ Mark Directory As → Excluded
```

**Increase memory:**
```
Help → Edit Custom VM Options
→ Increase -Xmx value (e.g., -Xmx2048m)
```

## Type Hints

We're gradually adding type hints to improve code quality:

```python
def get_device_path(self) -> Optional[str]:
    """Extract device path from combo box selection"""
    ...

def get_resolution(self) -> Tuple[int, int]:
    """Get selected resolution as tuple"""
    ...
```

### When to Add Type Hints

- ✅ Function signatures (return types)
- ✅ Complex function parameters
- ✅ Class attributes (if ambiguous)
- ❌ Don't overdo it - readability first!

## Summary

### Current Status
- ✅ False alarms: Suppressed via inspection profile
- ✅ Style issues: Fixed (redundant parentheses)
- ✅ Unused parameters: Fixed (using underscore)
- ✅ Type hints: Added to key functions
- ⚠️ Some warnings remain: PyQt5/OpenCV type stub limitations

### What You Should Do
1. Keep inspection profile (`.idea/inspectionProfiles/Project_Default.xml`)
2. Ignore PyQt5 signal warnings (they're false positives)
3. Ignore OpenCV method warnings (incomplete stubs)
4. Fix any **new** warnings you introduce
5. Add type hints when helpful

### What's Normal
- Some yellow warnings from PyQt5 signals
- Some yellow warnings from OpenCV methods
- These don't indicate bugs - code works correctly!

The project is properly configured. PyCharm warnings that remain are due to third-party library limitations, not code issues.
