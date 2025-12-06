const { app, BrowserWindow, ipcMain, Menu, Tray, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const https = require('https');

// 019Solutions - Auto-Update & Remote Management
const APP_VERSION = '1.0.0';
const UPDATE_CHECK_INTERVAL = 30 * 60 * 1000; // 30 minutes
const HEARTBEAT_INTERVAL = 5 * 60 * 1000; // 5 minutes
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://deployed-app.preview.emergentagent.com';

let mainWindow;
let tray;
let installationId;

// Generate unique installation ID
function getInstallationId() {
  const idFile = path.join(app.getPath('userData'), 'installation.id');
  
  if (fs.existsSync(idFile)) {
    return fs.readFileSync(idFile, 'utf8');
  } else {
    const id = `remza-gaming-desktop-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    fs.writeFileSync(idFile, id);
    return id;
  }
}

// Create main window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    icon: path.join(__dirname, 'resources', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: true,
      allowRunningInsecureContent: false
    },
    backgroundColor: '#000000',
    titleBarStyle: 'default',
    autoHideMenuBar: false,
    show: false
  });

  // Load the app
  const startUrl = app.isPackaged
    ? `file://${path.join(__dirname, 'build/index.html')}`
    : 'http://localhost:3000';

  mainWindow.loadURL(startUrl);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Register installation on first launch
    registerInstallation();
    
    // Start auto-update checker
    startAutoUpdateChecker();
    
    // Start heartbeat
    startHeartbeat();
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Prevent navigation away from app
  mainWindow.webContents.on('will-navigate', (event, url) => {
    if (!url.startsWith(startUrl)) {
      event.preventDefault();
      shell.openExternal(url);
    }
  });

  // Handle window close
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
      return false;
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // DevTools in development
  if (!app.isPackaged) {
    mainWindow.webContents.openDevTools();
  }
}

// Create system tray
function createTray() {
  const iconPath = path.join(__dirname, 'resources', 'icon.png');
  tray = new Tray(iconPath);
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'REMZA019 Gaming',
      enabled: false
    },
    { type: 'separator' },
    {
      label: 'Show App',
      click: () => {
        mainWindow.show();
        mainWindow.focus();
      }
    },
    {
      label: 'Check for Updates',
      click: () => {
        checkForUpdates(true);
      }
    },
    { type: 'separator' },
    {
      label: `Version ${APP_VERSION}`,
      enabled: false
    },
    {
      label: 'About 019Solutions',
      click: () => {
        shell.openExternal('https://019solutions.com');
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        app.isQuitting = true;
        app.quit();
      }
    }
  ]);
  
  tray.setToolTip('REMZA019 Gaming');
  tray.setContextMenu(contextMenu);
  
  tray.on('click', () => {
    mainWindow.show();
    mainWindow.focus();
  });
}

// Register installation with backend
function registerInstallation() {
  const data = JSON.stringify({
    installation_id: installationId,
    version: APP_VERSION,
    platform: 'desktop',
    os: process.platform,
    last_check: new Date().toISOString(),
    auto_update_enabled: true
  });

  const options = {
    hostname: new URL(BACKEND_URL).hostname,
    port: 443,
    path: '/api/version/register-installation',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': data.length
    }
  };

  const req = https.request(options, (res) => {
    console.log(`Installation registered: ${res.statusCode}`);
  });

  req.on('error', (error) => {
    console.error('Registration error:', error);
  });

  req.write(data);
  req.end();
}

// Check for updates
function checkForUpdates(showNoUpdateDialog = false) {
  const options = {
    hostname: new URL(BACKEND_URL).hostname,
    port: 443,
    path: `/api/version/check-update?current_version=${APP_VERSION}`,
    method: 'GET'
  };

  const req = https.request(options, (res) => {
    let data = '';
    
    res.on('data', (chunk) => {
      data += chunk;
    });
    
    res.on('end', () => {
      try {
        const updateInfo = JSON.parse(data);
        
        if (updateInfo.is_update_available) {
          const { dialog } = require('electron');
          dialog.showMessageBox(mainWindow, {
            type: 'info',
            title: 'Update Available',
            message: `Version ${updateInfo.version} is available!`,
            detail: `${updateInfo.version_name}\n\n${updateInfo.update_notes}`,
            buttons: ['Download Update', 'Later']
          }).then((result) => {
            if (result.response === 0) {
              shell.openExternal(updateInfo.update_url);
            }
          });
        } else if (showNoUpdateDialog) {
          const { dialog } = require('electron');
          dialog.showMessageBox(mainWindow, {
            type: 'info',
            title: 'No Updates',
            message: 'You are running the latest version!',
            buttons: ['OK']
          });
        }
      } catch (error) {
        console.error('Update check error:', error);
      }
    });
  });

  req.on('error', (error) => {
    console.error('Update check request error:', error);
  });

  req.end();
}

// Start auto-update checker
function startAutoUpdateChecker() {
  checkForUpdates(false);
  setInterval(() => {
    checkForUpdates(false);
  }, UPDATE_CHECK_INTERVAL);
}

// Send heartbeat to backend
function sendHeartbeat() {
  const options = {
    hostname: new URL(BACKEND_URL).hostname,
    port: 443,
    path: `/api/version/heartbeat?installation_id=${installationId}`,
    method: 'POST'
  };

  const req = https.request(options, (res) => {
    let data = '';
    
    res.on('data', (chunk) => {
      data += chunk;
    });
    
    res.on('end', () => {
      try {
        const response = JSON.parse(data);
        
        // Check if update is available
        if (response.update_available) {
          checkForUpdates(false);
        }
        
        // Apply remote config if provided
        if (response.remote_config) {
          applyRemoteConfig(response.remote_config);
        }
      } catch (error) {
        console.error('Heartbeat response error:', error);
      }
    });
  });

  req.on('error', (error) => {
    console.error('Heartbeat error:', error);
  });

  req.end();
}

// Start heartbeat
function startHeartbeat() {
  sendHeartbeat();
  setInterval(() => {
    sendHeartbeat();
  }, HEARTBEAT_INTERVAL);
}

// Apply remote configuration
function applyRemoteConfig(config) {
  console.log('Remote config received:', config);
  
  if (config.maintenance_mode) {
    const { dialog } = require('electron');
    dialog.showMessageBox(mainWindow, {
      type: 'warning',
      title: 'Maintenance Mode',
      message: 'System is under maintenance',
      detail: config.announcement || 'Please try again later.',
      buttons: ['OK']
    });
  }
  
  if (config.announcement) {
    // Show announcement to user
    mainWindow.webContents.send('show-announcement', config.announcement);
  }
}

// Application menu
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Refresh',
          accelerator: 'CmdOrCtrl+R',
          click: () => {
            mainWindow.reload();
          }
        },
        { type: 'separator' },
        {
          label: 'Quit',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            app.isQuitting = true;
            app.quit();
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About',
          click: () => {
            const { dialog } = require('electron');
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About REMZA019 Gaming',
              message: `REMZA019 Gaming v${APP_VERSION}`,
              detail: 'Developed by 019Solutions\n\nCopyright © 2025 019Solutions\nAll Rights Reserved.',
              buttons: ['OK']
            });
          }
        },
        {
          label: 'Check for Updates',
          click: () => {
            checkForUpdates(true);
          }
        },
        { type: 'separator' },
        {
          label: '019Solutions Website',
          click: () => {
            shell.openExternal('https://019solutions.com');
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// App ready
app.whenReady().then(() => {
  installationId = getInstallationId();
  createWindow();
  createTray();
  createMenu();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    } else {
      mainWindow.show();
    }
  });
});

// Quit when all windows are closed (except on macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Before quit
app.on('before-quit', () => {
  app.isQuitting = true;
});

// IPC handlers
ipcMain.handle('get-app-version', () => {
  return APP_VERSION;
});

ipcMain.handle('get-installation-id', () => {
  return installationId;
});

ipcMain.handle('check-for-updates', () => {
  checkForUpdates(true);
});

console.log(`🚀 REMZA019 Gaming Desktop v${APP_VERSION}`);
console.log(`📦 Installation ID: ${installationId}`);
console.log(`🔧 Platform: ${process.platform}`);
console.log(`💚 Powered by 019Solutions`);
