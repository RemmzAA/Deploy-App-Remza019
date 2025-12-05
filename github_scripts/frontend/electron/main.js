const { app, BrowserWindow } = require('electron');

let mainWindow;

app.on('ready', () => {
  // NAJJEDNOSTAVNIJI MOGUĆI PROZOR
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    backgroundColor: '#000000',
    webPreferences: {
      nodeIntegration: false
    }
  });

  // UČITAJ SAMO HTML STRING - BEZ FAJLA!
  mainWindow.loadURL('data:text/html,<html><body style="background:#000;color:#0f0;font-size:30px;text-align:center;padding:100px;"><h1>REMZA019 GAMING</h1><p>If you see this - Electron WORKS!</p><p>Ako vidiš ovo - Electron RADI!</p></body></html>');

  mainWindow.webContents.openDevTools();
});

app.on('window-all-closed', () => {
  app.quit();
});

console.log('Electron test version loaded');
