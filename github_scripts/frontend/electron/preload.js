const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // Get app version
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  
  // Get installation ID
  getInstallationId: () => ipcRenderer.invoke('get-installation-id'),
  
  // Check for updates
  checkForUpdates: () => ipcRenderer.invoke('check-for-updates'),
  
  // Listen for announcements
  onShowAnnouncement: (callback) => {
    ipcRenderer.on('show-announcement', (event, message) => callback(message));
  },
  
  // Platform info
  platform: process.platform,
  isElectron: true
});

console.log('🔐 Electron preload script loaded - 019Solutions');
