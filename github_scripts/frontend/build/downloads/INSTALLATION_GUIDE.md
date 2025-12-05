# 🎮 REMZA019 Gaming Desktop - Installation Guide

## Brzi Vodič za Instalaciju / Quick Installation Guide

**Verzija**: 1.0.0 - NIVO 1 Release  
**019Solutions** - Professional Gaming Platform

---

## 📥 Pre Instalacije

### Preuzimanje / Download

**Windows** 🪟
```
REMZA019-Gaming-Portable-1.0.0-Windows.zip (171 MB)
SHA256: b41ecdcbf4bfd3a3b7993bb890908bd64b41a1c7f5f8dcc605d23f0fe7b39c46
```

**Linux** 🐧
```
REMZA019-Gaming-Portable-1.0.0-Linux.tar.gz (~90 MB)
SHA256: [Generiše se nakon kreiranja]
```

### Provera Checksuma (Opciono ali Preporučeno)

**Windows:**
```powershell
CertUtil -hashfile REMZA019-Gaming-Portable-1.0.0-Windows.zip SHA256
# Uporedi sa checksumom iz CHECKSUMS.txt
```

**Linux:**
```bash
sha256sum REMZA019-Gaming-Portable-1.0.0-Linux.tar.gz
# Uporedi sa checksumom iz CHECKSUMS.txt
```

---

## 🪟 Windows Instalacija

### Metoda 1: ZIP Portable (Preporučeno)

**Koraci:**

1. **Preuzmi ZIP**
   - Desni klik → Save As
   - Sačuvaj gde god želiš

2. **Ekstraktuj ZIP**
   - Desni klik na ZIP → "Extract All..."
   - Ili koristi 7-Zip, WinRAR, etc.
   - Ekstraktuj u folder (npr. `C:\REMZA019Gaming\`)

3. **Otvori Folder**
   ```
   C:\REMZA019Gaming\win-arm64-unpacked\
   ```

4. **Pokreni Aplikaciju**
   - Dvostruki klik na: `REMZA019 Gaming.exe`
   
5. **Windows SmartScreen Upozorenje** (Može se pojaviti)
   - Klikni "More info"
   - Klikni "Run anyway"
   - Ovo je normalno za nove aplikacije

6. **Gotovo!** 🎉
   - Aplikacija se pokreće
   - Desktop badge pokazuje "💻 Desktop"

### Dodatne Opcije (Windows)

**Kreiraj Desktop Prečicu:**
1. Desni klik na `REMZA019 Gaming.exe`
2. Send to → Desktop (create shortcut)

**Kreiraj Start Menu Prečicu:**
1. Kopiraj `REMZA019 Gaming.exe` putanju
2. Windows+R → `shell:programs`
3. Desni klik → New → Shortcut
4. Zalepi putanju

**Dodaj u Taskbar:**
- Povuci `REMZA019 Gaming.exe` na Taskbar

---

## 🐧 Linux Instalacija

### Metoda 1: TAR.GZ Portable (Preporučeno)

**Koraci:**

1. **Preuzmi TAR.GZ**
   ```bash
   wget [URL]/REMZA019-Gaming-Portable-1.0.0-Linux.tar.gz
   ```

2. **Ekstraktuj**
   ```bash
   tar -xzf REMZA019-Gaming-Portable-1.0.0-Linux.tar.gz
   ```

3. **Prebaći se u Folder**
   ```bash
   cd linux-arm64-unpacked
   ```

4. **Napravi Executable**
   ```bash
   chmod +x electron
   ```

5. **Pokreni**
   ```bash
   ./electron
   ```

6. **Gotovo!** 🎉

### Dodatne Opcije (Linux)

**Instaliraj u /opt (Opciono):**
```bash
sudo mkdir -p /opt/remza019-gaming
sudo cp -r linux-arm64-unpacked/* /opt/remza019-gaming/
sudo ln -s /opt/remza019-gaming/electron /usr/local/bin/remza019-gaming

# Sada možeš pokrenuti sa:
remza019-gaming
```

**Kreiraj Desktop Entry:**
```bash
cat > ~/.local/share/applications/remza019-gaming.desktop << 'EOF'
[Desktop Entry]
Name=REMZA019 Gaming
Comment=Professional Gaming Platform
Exec=/opt/remza019-gaming/electron
Icon=remza019-gaming
Terminal=false
Type=Application
Categories=Game;Entertainment;
EOF

chmod +x ~/.local/share/applications/remza019-gaming.desktop
```

**Koristi Installation Script:**
```bash
# Ako imaš install-linux.sh
chmod +x install-linux.sh
./install-linux.sh
```

---

## ⚙️ Post-Instalacija Setup

### Prvi Start

1. **Izaberi Jezik**
   - Klikni na jezik switcher (gore levo)
   - Izaberi: 🇷🇸 SR / 🇬🇧 EN / 🇩🇪 DE

2. **Proveri LIVE Status**
   - Ako je stream live, videćeš crveni "🔴 LIVE NOW!" badge

3. **Login / Register (Opciono)**
   - Klikni "📺 PRETPLATI SE NA OBAVEŠTENJA" dugme
   - Ili koristi Viewer Menu za login

4. **Iskušaj Funkcije**
   - Pogledaj Latest Gaming Content
   - Proveri Weekly Schedule
   - Proveri Leaderboard
   - Glasaj u Poll-ovima

### Systemske Postavke

**Windows - Autostart (Opciono):**
1. Win+R → `shell:startup`
2. Napravi shortcut za `REMZA019 Gaming.exe`
3. App će startovati sa Windows-om

**Linux - Autostart (Opciono):**
```bash
cat > ~/.config/autostart/remza019-gaming.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=REMZA019 Gaming
Exec=/usr/local/bin/remza019-gaming
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
```

---

## 🔄 Ažuriranje / Updates

Aplikacija automatski proverava updates:

1. **Auto-Check**
   - Svaki 30 minuta proverava novu verziju

2. **Update Notifikacija**
   - Ako je dostupna, videćeš: "🔄 Update Available"

3. **Kako Ažurirati**
   - Klikni na notifikaciju
   - Otvara se download stranica
   - Preuzmi novu verziju
   - Ekstraktuj preko stare (zatvori app prvo)
   - Pokreni novu verziju

4. **Sve Postavke Ostaju**
   - Settings i data se čuvaju

---

## 🆘 Troubleshooting

### App Se Ne Pokreće

**Windows:**
```powershell
# Proveri ako nedostaje Microsoft Visual C++ Redistributable
# Preuzmi sa: https://aka.ms/vs/17/release/vc_redist.x64.exe
```

**Linux:**
```bash
# Proveri dependencies
ldd linux-arm64-unpacked/electron

# Ako nedostaju biblioteke
sudo apt-get install -y libgtk-3-0 libnotify4 libnss3 libxss1 libxtst6
```

### Port Already in Use Error

```bash
# Ako vidiš "Port 3000 already in use"
# Potraži koji proces koristi port:

# Windows
netstat -ano | findstr :3000
taskkill /PID [PID_NUMBER] /F

# Linux
lsof -i :3000
kill -9 [PID]
```

### Aplikacija je Spora

1. **Zatvori druge aplikacije** - Oslobodi RAM
2. **Proveri internet** - Backend zahteva vezu
3. **Očisti cache**:
   - Windows: Izbriši `%APPDATA%\remza019-gaming-desktop\`
   - Linux: Izbriši `~/.config/remza019-gaming-desktop/`
4. **Reinstaliraj** - Ponovo ekstraktuj ZIP/TAR.GZ

---

## 📊 Sistemski Info

### Instalaciona Lokacija

**Windows:**
- Program: `[Tvoj folder]\win-arm64-unpacked\`
- Data: `%APPDATA%\remza019-gaming-desktop\`
- Logs: `%APPDATA%\remza019-gaming-desktop\logs\`

**Linux:**
- Program: `/opt/remza019-gaming/` (ako instaliran)
- Data: `~/.config/remza019-gaming-desktop/`
- Logs: `~/.config/remza019-gaming-desktop/logs/`

### Deinstalacija

**Windows:**
1. Zatvori aplikaciju
2. Izbriši folder sa ekstraktovanim fajlovima
3. Izbriši `%APPDATA%\remza019-gaming-desktop\` (opciono)
4. Izbriši desktop shortcuts

**Linux:**
```bash
# Ako instaliran u /opt
sudo rm -rf /opt/remza019-gaming
sudo rm /usr/local/bin/remza019-gaming

# Očisti config
rm -rf ~/.config/remza019-gaming-desktop
rm ~/.local/share/applications/remza019-gaming.desktop
```

---

## 💡 Saveti i Trikovi

### Performance Optimization

1. **Zatvori neupo trebljene tabove** - Manje RAM usage
2. **Koristi System Tray** - Minimize to tray umesto zatvaranja
3. **Update redovno** - Nove verzije imaju optimizacije

### Keyboard Shortcuts

- `F11` - Full-screen mode
- `Ctrl+R` - Refresh app
- `Ctrl+Q` - Quit app
- `Ctrl+H` - Hide to tray (Windows/Linux)

### Multiple Instances

Da pokreneš više instanci (npr. za testing):
```bash
# Samo pokreni executable više puta
# Svaka instanca će imati svoj window
```

---

## 🔗 Korisni Linkovi

**REMZA019 Gaming:**
- Twitch: https://twitch.tv/remza019
- YouTube: https://youtube.com/@remza019
- Discord: [Link do Discord servera]

**019Solutions:**
- Website: https://019solutions.com
- Support: support@019solutions.com
- Downloads: https://019solutions.com/downloads

**Dokumentacija:**
- README.md - Opšte informacije
- ELECTRON_DESKTOP_APP_GUIDE.md - Tehnički vodič
- DEPLOYMENT_CHECKLIST.md - Deployment info

---

## 📞 Kontakt za Pomoć

### Tehnička Podrška
**Email**: support@019solutions.com
**Response Time**: 24-48 sati

### Community Support
**Discord**: REMZA019 Gaming Community
**Response Time**: Obično brzo (zajednica pomaže)

### Bug Report
Ako pronađeš bug, prijavi sa:
- OS i verzija (npr. Windows 11, Ubuntu 22.04)
- App verzija (1.0.0)
- Šta si radio kada se bug desio
- Screenshot ako moguće
- Error poruka iz logs folder-a

---

## 🎉 Završna Reč

**Hvala što koristiš REMZA019 Gaming Desktop!**

Tvoja podrška omogućava kontinuiran razvoj platforme.

**Uživaj u gaming-u! 🎮**

---

**REMZA019 Gaming Desktop v1.0.0**
Powered by 019Solutions | Professional Gaming Platform Solutions
