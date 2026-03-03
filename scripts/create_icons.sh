#!/bin/bash
# Script to generate icon files in various sizes from SVG

set -e

# Get project root (parent of scripts/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Generating icon files from assets/icon.svg..."

# Check if ImageMagick or Inkscape is available
if command -v inkscape &> /dev/null; then
    CONVERTER="inkscape"
    echo "Using Inkscape for conversion"
elif command -v convert &> /dev/null; then
    CONVERTER="imagemagick"
    echo "Using ImageMagick for conversion"
else
    echo "Error: Neither Inkscape nor ImageMagick found!"
    echo "Please install one of them:"
    echo "  - Arch/CachyOS: sudo pacman -S inkscape"
    echo "  - Or: sudo pacman -S imagemagick"
    exit 1
fi

# Create icons directory
mkdir -p assets/icons

# Generate PNG icons in various sizes
SIZES=(16 22 24 32 48 64 128 256)

for size in "${SIZES[@]}"; do
    echo "Generating ${size}x${size}..."

    if [ "$CONVERTER" = "inkscape" ]; then
        inkscape assets/icon.svg -w $size -h $size -o "assets/icons/icon_${size}.png" 2>/dev/null
    else
        convert -background none assets/icon.svg -resize ${size}x${size} "assets/icons/icon_${size}.png"
    fi
done

# Create a Windows ICO file (if ImageMagick is available)
if command -v convert &> /dev/null; then
    echo "Creating assets/icon.ico for Windows..."
    convert assets/icons/icon_16.png assets/icons/icon_24.png assets/icons/icon_32.png assets/icons/icon_48.png assets/icons/icon_64.png assets/icons/icon_128.png assets/icons/icon_256.png assets/icon.ico
fi

echo ""
echo "Icon generation complete!"
echo "Generated icons in ./assets/icons/ directory"
echo ""
ls -lh assets/icons/
[ -f assets/icon.ico ] && echo "" && echo "Windows icon: assets/icon.ico ($(du -h assets/icon.ico | cut -f1))"
