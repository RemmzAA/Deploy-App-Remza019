const { app, BrowserWindow } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    backgroundColor: '#000000',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    },
    show: true // UVEK PRIKAŽI
  });

  // Load app
  const startUrl = app.isPackaged
    ? `file://${path.join(__dirname, 'build/index.html')}`
    : 'http://localhost:3000';

  console.log('Loading URL:', startUrl);
  mainWindow.loadURL(startUrl);

  // Open DevTools for debugging
  mainWindow.webContents.openDevTools();

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

console.log('REMZA019 Gaming - Simple Version Started');
