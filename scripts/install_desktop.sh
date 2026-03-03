#!/bin/bash
# Installation script for YatsurugiCapture desktop entry

set -e

echo "========================================="
echo "YatsurugiCapture Desktop Entry Installer"
echo "========================================="
echo ""

# Get the project root directory (parent of scripts/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_DIR="$PROJECT_ROOT/scripts"

# Check if running from dist directory or source directory
if [ -f "$PROJECT_ROOT/YatsurugiCapture" ]; then
    BINARY_PATH="$PROJECT_ROOT/YatsurugiCapture"
elif [ -f "$PROJECT_ROOT/dist/YatsurugiCapture" ]; then
    BINARY_PATH="$PROJECT_ROOT/dist/YatsurugiCapture"
else
    echo "Error: YatsurugiCapture binary not found!"
    echo "Please build the application first with: scripts/build_release.sh"
    exit 1
fi

echo "Found binary at: $BINARY_PATH"
echo ""

# Check for icon file
ICON_FOUND=false
if [ -f "$PROJECT_ROOT/assets/icon.svg" ]; then
    ICON_PATH="$PROJECT_ROOT/assets/icon.svg"
    ICON_FOUND=true
    echo "Found icon: $ICON_PATH"
elif [ -f "$PROJECT_ROOT/assets/icons/icon_128.png" ]; then
    ICON_PATH="$PROJECT_ROOT/assets/icons/icon_128.png"
    ICON_FOUND=true
    echo "Found icon: $ICON_PATH"
fi
echo ""

# Ask user for installation type
echo "Choose installation type:"
echo "1) System-wide (requires sudo, installs to /usr/local/bin)"
echo "2) User-only (no sudo needed, installs to ~/.local/bin)"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        # System-wide installation
        echo ""
        echo "Installing system-wide..."

        # Copy binary
        sudo cp "$BINARY_PATH" /usr/local/bin/YatsurugiCapture
        sudo chmod +x /usr/local/bin/YatsurugiCapture

        # Copy desktop file
        sudo cp "$PROJECT_ROOT/assets/YatsurugiCapture.desktop" /usr/share/applications/
        sudo chmod 644 /usr/share/applications/YatsurugiCapture.desktop

        # Install icon if available
        if [ "$ICON_FOUND" = true ]; then
            if [[ "$ICON_PATH" == *.svg ]]; then
                sudo mkdir -p /usr/share/icons/hicolor/scalable/apps
                sudo cp "$ICON_PATH" /usr/share/icons/hicolor/scalable/apps/yatsurugi-capture.svg
            else
                sudo mkdir -p /usr/share/icons/hicolor/128x128/apps
                sudo cp "$ICON_PATH" /usr/share/icons/hicolor/128x128/apps/yatsurugi-capture.png
            fi
            sudo gtk-update-icon-cache /usr/share/icons/hicolor/ 2>/dev/null || true
            echo "Icon installed"
        fi

        echo ""
        echo "========================================="
        echo "Installation complete!"
        echo "========================================="
        echo ""
        echo "Binary installed to: /usr/local/bin/YatsurugiCapture"
        echo "Desktop entry: /usr/share/applications/YatsurugiCapture.desktop"
        echo ""
        echo "You can now:"
        echo "  - Launch from application menu"
        echo "  - Run from terminal: YatsurugiCapture"
        echo "  - Add to desktop or taskbar"
        ;;

    2)
        # User-only installation
        echo ""
        echo "Installing for current user..."

        # Create directories if they don't exist
        mkdir -p ~/.local/bin
        mkdir -p ~/.local/share/applications

        # Copy binary
        cp "$BINARY_PATH" ~/.local/bin/YatsurugiCapture
        chmod +x ~/.local/bin/YatsurugiCapture

        # Create desktop file with correct path
        sed "s|Exec=/usr/local/bin/YatsurugiCapture|Exec=$HOME/.local/bin/YatsurugiCapture|g" \
            "$PROJECT_ROOT/assets/YatsurugiCapture.desktop" > ~/.local/share/applications/YatsurugiCapture.desktop
        chmod 644 ~/.local/share/applications/YatsurugiCapture.desktop

        # Install icon if available
        if [ "$ICON_FOUND" = true ]; then
            if [[ "$ICON_PATH" == *.svg ]]; then
                mkdir -p ~/.local/share/icons/hicolor/scalable/apps
                cp "$ICON_PATH" ~/.local/share/icons/hicolor/scalable/apps/yatsurugi-capture.svg
            else
                mkdir -p ~/.local/share/icons/hicolor/128x128/apps
                cp "$ICON_PATH" ~/.local/share/icons/hicolor/128x128/apps/yatsurugi-capture.png
            fi
            gtk-update-icon-cache ~/.local/share/icons/hicolor/ 2>/dev/null || true
            echo "Icon installed"
        fi

        # Check if ~/.local/bin is in PATH
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            echo ""
            echo "WARNING: ~/.local/bin is not in your PATH"
            echo "Add this line to your ~/.bashrc or ~/.zshrc:"
            echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
            echo ""
        fi

        echo ""
        echo "========================================="
        echo "Installation complete!"
        echo "========================================="
        echo ""
        echo "Binary installed to: ~/.local/bin/YatsurugiCapture"
        echo "Desktop entry: ~/.local/share/applications/YatsurugiCapture.desktop"
        echo ""
        echo "You can now:"
        echo "  - Launch from application menu"
        echo "  - Run from terminal: YatsurugiCapture (if ~/.local/bin is in PATH)"
        echo "  - Add to desktop or taskbar"
        ;;

    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "To add to desktop (KDE Plasma):"
echo "  1. Right-click on desktop"
echo "  2. Select 'Add Widgets'"
echo "  3. Search for 'Application Launcher'"
echo "  4. Drag it to desktop"
echo "  5. Configure it to launch YatsurugiCapture"
echo ""
echo "Or simply search for 'YatsurugiCapture' in your application launcher!"
