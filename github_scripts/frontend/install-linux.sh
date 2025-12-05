#!/bin/bash

# REMZA019 Gaming Desktop - Linux Installation Script
# Copyright © 2025 019Solutions

set -e

echo "🎮 REMZA019 Gaming Desktop - Linux Installer"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root for DEB install
if [ "$EUID" -ne 0 ] && [ "$1" == "deb" ]; then
    echo -e "${RED}Error: DEB installation requires sudo/root${NC}"
    echo "Run: sudo $0 deb"
    exit 1
fi

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    VERSION=$VERSION_ID
else
    DISTRO="unknown"
fi

echo -e "${GREEN}Detected OS: $DISTRO $VERSION${NC}"
echo ""

# Function to install AppImage
install_appimage() {
    echo "📦 Installing AppImage (Portable Version)..."
    
    # Find AppImage file
    APPIMAGE=$(find . -name "REMZA019-Gaming-*.AppImage" | head -n 1)
    
    if [ -z "$APPIMAGE" ]; then
        echo -e "${RED}Error: AppImage file not found!${NC}"
        echo "Please download REMZA019-Gaming-*.AppImage first"
        exit 1
    fi
    
    # Make executable
    chmod +x "$APPIMAGE"
    
    # Move to /opt (optional)
    read -p "Install to /opt? (requires sudo) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo mkdir -p /opt/remza019-gaming
        sudo cp "$APPIMAGE" /opt/remza019-gaming/
        sudo ln -sf /opt/remza019-gaming/"$(basename $APPIMAGE)" /usr/local/bin/remza019-gaming
        echo -e "${GREEN}✅ Installed to /opt/remza019-gaming/${NC}"
        echo -e "${GREEN}✅ Symlink created: /usr/local/bin/remza019-gaming${NC}"
    else
        echo -e "${GREEN}✅ AppImage ready to run from current directory${NC}"
        echo "Run: ./$APPIMAGE"
    fi
    
    # Create desktop entry
    read -p "Create desktop shortcut? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_desktop_entry "$APPIMAGE"
    fi
}

# Function to install DEB package
install_deb() {
    echo "📦 Installing DEB package..."
    
    # Find DEB file
    DEB=$(find . -name "REMZA019-Gaming-*.deb" | head -n 1)
    
    if [ -z "$DEB" ]; then
        echo -e "${RED}Error: DEB file not found!${NC}"
        echo "Please download REMZA019-Gaming-*.deb first"
        exit 1
    fi
    
    # Install dependencies
    echo "Installing dependencies..."
    apt-get update
    apt-get install -y libgtk-3-0 libnotify4 libnss3 libxss1 libxtst6 xdg-utils libatspi2.0-0 libdrm2 libgbm1 libxcb-dri3-0
    
    # Install DEB
    dpkg -i "$DEB" || apt-get install -f -y
    
    echo -e "${GREEN}✅ REMZA019 Gaming installed successfully!${NC}"
    echo "Launch from: Applications menu or run 'remza019-gaming'"
}

# Function to create desktop entry
create_desktop_entry() {
    local EXEC_PATH=$1
    
    DESKTOP_FILE="$HOME/.local/share/applications/remza019-gaming.desktop"
    
    mkdir -p "$HOME/.local/share/applications"
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=REMZA019 Gaming
Comment=Professional Gaming Platform by 019Solutions
Exec=$EXEC_PATH
Icon=remza019-gaming
Terminal=false
Type=Application
Categories=Game;Entertainment;
Keywords=gaming;fortnite;streaming;remza019;
StartupWMClass=REMZA019 Gaming
EOF
    
    chmod +x "$DESKTOP_FILE"
    
    echo -e "${GREEN}✅ Desktop shortcut created${NC}"
    echo "Check your applications menu!"
}

# Main menu
echo "Select installation method:"
echo "1) AppImage (Portable - Recommended for most users)"
echo "2) DEB Package (Ubuntu/Debian - Requires sudo)"
echo "3) Exit"
echo ""
read -p "Choose [1-3]: " choice

case $choice in
    1)
        install_appimage
        ;;
    2)
        install_deb
        ;;
    3)
        echo "Installation cancelled"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "=============================================="
echo -e "${GREEN}🎉 Installation Complete!${NC}"
echo ""
echo "System Requirements:"
echo "  - RAM: 4 GB minimum"
echo "  - Disk: 500 MB free space"
echo "  - Internet: For updates and content"
echo ""
echo "Support:"
echo "  - Website: https://019solutions.com"
echo "  - Discord: REMZA019 Gaming Community"
echo ""
echo -e "${GREEN}Enjoy REMZA019 Gaming Desktop! 🎮${NC}"
echo "Powered by 019Solutions"
echo "=============================================="
