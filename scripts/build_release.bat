@echo off
REM Build script for creating YatsurugiCapture release on Windows

echo =========================================
echo YatsurugiCapture Release Builder
echo =========================================
echo.

REM Check if PyInstaller is installed
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the application
echo.
echo Building standalone executable...
pyinstaller YatsurugiCapture.spec

REM Check if build was successful
if exist "dist\YatsurugiCapture.exe" (
    echo.
    echo =========================================
    echo Build successful!
    echo =========================================
    echo.
    echo Executable location: dist\YatsurugiCapture.exe
    for %%I in (dist\YatsurugiCapture.exe) do echo File size: %%~zI bytes
    echo.
    echo To create a release package:
    echo   cd dist
    echo   tar -czf YatsurugiCapture-windows-x64.zip YatsurugiCapture.exe
    echo.
) else (
    echo.
    echo =========================================
    echo Build failed!
    echo =========================================
    exit /b 1
)
