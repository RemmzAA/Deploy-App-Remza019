# REMZA019 Gaming Desktop App - Installation Guide

## 019Solutions Desktop Application

This is the official desktop application for REMZA019 Gaming, providing a native cross-platform experience with auto-update capabilities and enhanced performance.

---

## 🚀 Features

### Core Features
- **Native Desktop Experience**: Runs as a standalone application on Windows, macOS, and Linux
- **Auto-Update System**: Automatically checks for updates every 30 minutes
- **System Tray Integration**: Minimize to system tray for quick access
- **Offline-First**: Works without constant internet connection
- **Enhanced Security**: Sandboxed execution with Electron's security features
- **Remote Management**: 019Solutions can push configuration updates remotely

### Technical Features
- **Version Management**: Tracks installation ID and version
- **Heartbeat System**: Regular communication with backend for updates
- **Cross-Platform**: Single codebase for all platforms
- **Professional Branding**: 019Solutions branding throughout

---

## 📦 Development

### Prerequisites
```bash
Node.js >= 16.x
Yarn package manager
```

### Install Dependencies
```bash
cd /app/frontend
yarn install
```

### Run in Development Mode
```bash
yarn electron:dev
```
This will:
1. Start the React development server
2. Wait for it to be ready
3. Launch the Electron app

---

## 🔨 Building Installers

### Build for Current Platform
```bash
yarn electron:build
```

### Build for Specific Platforms

**Windows (NSIS Installer)**
```bash
yarn electron:build-win
```
Outputs: `dist/REMZA019-Gaming-Setup-0.1.0.exe`

**macOS (DMG)**
```bash
yarn electron:build-mac
```
Outputs: `dist/REMZA019-Gaming-0.1.0.dmg`

**Linux (AppImage & DEB)**
```bash
yarn electron:build-linux
```
Outputs:
- `dist/REMZA019-Gaming-0.1.0.AppImage`
- `dist/REMZA019-Gaming-0.1.0.deb`

### Build for All Platforms
```bash
yarn electron:build-all
```

---

## 📂 Project Structure

```
frontend/
├── electron/
│   ├── main.js              # Electron main process
│   ├── preload.js           # Secure IPC bridge
│   └── resources/
│       ├── icon.png         # App icon
│       └── entitlements.mac.plist  # macOS entitlements
├── build/                   # React production build
├── dist/                    # Electron installers (generated)
└── package.json             # Electron configuration
```

---

## ⚙️ Configuration

### Electron Builder Config (package.json)
```json
{
  "build": {
    "appId": "com.019solutions.remza019gaming",
    "productName": "REMZA019 Gaming",
    "win": {
      "target": ["nsis"],
      "icon": "electron/resources/icon.png"
    },
    "mac": {
      "target": ["dmg"],
      "category": "public.app-category.entertainment"
    },
    "linux": {
      "target": ["AppImage", "deb"],
      "category": "Game"
    }
  }
}
```

### Version Management
Version is managed in `electron/main.js`:
```javascript
const APP_VERSION = '1.0.0';
```

Update this for new releases.

---

## 🔒 Security Features

### Level 3 Security Implementation
- **Context Isolation**: Enabled (renderer cannot access Node.js)
- **Node Integration**: Disabled
- **Secure IPC**: All communication through preload script
- **Web Security**: Enabled
- **No Insecure Content**: Blocked

### Preload Script
The `preload.js` exposes only necessary APIs:
```javascript
window.electronAPI = {
  getAppVersion,
  getInstallationId,
  checkForUpdates,
  onShowAnnouncement,
  platform
}
```

---

## 🔄 Auto-Update System

### How It Works
1. **Heartbeat**: Sends installation ID to backend every 5 minutes
2. **Version Check**: Checks for updates every 30 minutes
3. **Update Notification**: Shows dialog when update is available
4. **Download**: Opens download URL for new version

### Backend Integration
The app communicates with:
- `POST /api/version/register-installation` - Register new installation
- `GET /api/version/check-update?current_version=X` - Check for updates
- `POST /api/version/heartbeat?installation_id=X` - Send heartbeat

---

## 🎨 Customization

### Icon
Replace `electron/resources/icon.png` with your custom icon (512x512 PNG recommended).

### Branding
Update in `electron/main.js`:
- Window title
- Tray tooltip
- About dialog
- Menu labels

---

## 📊 Installation Analytics

Each installation generates a unique ID stored in:
```
userData/installation.id
```

This allows tracking:
- Active installations
- Update adoption rates
- Platform distribution

---

## 🐛 Troubleshooting

### DevTools
In development, DevTools open automatically.
For production builds, use `Help > Toggle Developer Tools` (if enabled in menu).

### Logs
Electron logs to:
- **Windows**: `%APPDATA%\remza019-gaming-desktop\logs\`
- **macOS**: `~/Library/Logs/remza019-gaming-desktop/`
- **Linux**: `~/.config/remza019-gaming-desktop/logs/`

### Clear Cache
Delete:
- **Windows**: `%APPDATA%\remza019-gaming-desktop\`
- **macOS**: `~/Library/Application Support/remza019-gaming-desktop/`
- **Linux**: `~/.config/remza019-gaming-desktop/`

---

## 🚀 Deployment Checklist

Before building production installers:

1. ✅ Update version in `electron/main.js`
2. ✅ Update version in `package.json`
3. ✅ Test in development mode: `yarn electron:dev`
4. ✅ Build React app: `yarn build`
5. ✅ Build installer: `yarn electron:build`
6. ✅ Test installer on clean machine
7. ✅ Upload to hosting (e.g., 019solutions.com/downloads)
8. ✅ Update backend version info
9. ✅ Test auto-update flow

---

## 📝 Release Process

### 1. Prepare Release
```bash
# Update version in electron/main.js
const APP_VERSION = '1.0.1';

# Update package.json version
"version": "1.0.1"
```

### 2. Build Installers
```bash
yarn build
yarn electron:build-all
```

### 3. Test Installers
Install and test on each platform.

### 4. Upload to Server
Upload installers to `https://019solutions.com/downloads/`

### 5. Update Backend
Update version info in backend database:
```json
{
  "version": "1.0.1",
  "version_name": "NIVO 1 Release",
  "update_url": "https://019solutions.com/downloads/REMZA019-Gaming-Setup-1.0.1.exe",
  "update_notes": "New features: Polls, Predictions, Leaderboard"
}
```

### 6. Announce Update
Existing installations will automatically detect the update.

---

## 🌐 Platform-Specific Notes

### Windows
- **Admin Rights**: NSIS installer requests admin for per-machine install
- **SmartScreen**: Users may see warning on first run (code signing recommended)
- **Desktop Shortcut**: Created automatically
- **Start Menu**: Added to Start Menu

### macOS
- **Gatekeeper**: App needs to be notarized for smooth install
- **Code Signing**: Required for distribution
- **DMG**: Drag-and-drop installer interface
- **Quarantine**: Users may need to right-click > Open first time

### Linux
- **AppImage**: Portable, no installation needed
- **DEB**: For Debian/Ubuntu systems
- **Permissions**: May need `chmod +x` for AppImage

---

## 💚 019Solutions

**REMZA019 Gaming Desktop App**
Developed by 019Solutions
Copyright © 2025 019Solutions
All Rights Reserved.

For support: https://019solutions.com
For updates: https://019solutions.com/downloads

---

## 📄 License

Commercial License - 019Solutions
This software is proprietary and confidential.
