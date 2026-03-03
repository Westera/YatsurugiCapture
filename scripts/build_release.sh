#!/bin/bash
# Build script for creating YatsurugiCapture release

set -e  # Exit on error

echo "========================================="
echo "YatsurugiCapture Release Builder"
echo "========================================="
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build the application
echo ""
echo "Building standalone executable..."
pyinstaller YatsurugiCapture.spec

# Check if build was successful
if [ -f "dist/YatsurugiCapture" ]; then
    echo ""
    echo "========================================="
    echo "Build successful!"
    echo "========================================="
    echo ""
    echo "Executable location: dist/YatsurugiCapture"
    echo "File size: $(du -h dist/YatsurugiCapture | cut -f1)"
    echo ""
    echo "To create a release package:"
    echo "  cd dist && tar -czf YatsurugiCapture-linux-x64.tar.gz YatsurugiCapture"
    echo ""
else
    echo ""
    echo "========================================="
    echo "Build failed!"
    echo "========================================="
    exit 1
fi
