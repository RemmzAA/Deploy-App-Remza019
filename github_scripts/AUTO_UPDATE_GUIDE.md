# 🌐 AUTO-UPDATE & REMOTE MANAGEMENT SYSTEM

## Powered by 019Solutions

---

## 📋 OVERVIEW

REMZA019 Gaming softver sada ima ugrađenu **automatsku proveru ažuriranja** i **sistem za daljinsko upravljanje**. Ovo omogućava:

- ✅ **Automatsko obaveštavanje o novim verzijama**
- ✅ **Daljinska konfiguracija i kontrola**
- ✅ **Real-time monitoring svih instalacija**
- ✅ **Centralizovano upravljanje funkcionalnostima**
- ✅ **Push updates za sve korisnike odjednom**

---

## 🔄 AUTO-UPDATE SISTEM

### Kako funkcioniše?

1. **Automatska provera** - Svaki softver proverava nove verzije svakih 30 minuta
2. **Notifikacija** - Korisnik dobija obaveštenje kada je nova verzija dostupna
3. **Jednostavno ažuriranje** - Jedan klik za preuzimanje nove verzije
4. **Sigurnost** - Sve verzije su digitalno potpisane od 019Solutions

### Backend API Endpoints:

```
GET  /api/version/current              - Trenutna verzija sistema
GET  /api/version/check-update         - Provera dostupnih ažuriranja
POST /api/version/register-installation - Registracija instalacije
POST /api/version/heartbeat            - Heartbeat signal (provera da li radi)
GET  /api/version/changelog            - Kompletna istorija promena
```

### Frontend Komponenta:

**VersionChecker** - Automatski prikazuje:
- Trenutnu verziju (dole desno na sajtu)
- "Update Available" badge ako postoji nova verzija
- Klikabilni link za preuzimanje

---

## 🎛️ REMOTE MANAGEMENT SISTEM

### Šta možete kontrolisati?

**Feature Flags (Uključi/Isključi funkcionalnosti):**
- `polls_enabled` - Polls sistem
- `predictions_enabled` - Predictions sistem
- `leaderboard_enabled` - Leaderboard
- `chat_enabled` - Real-time chat
- `donations_enabled` - Donation sistem
- `email_notifications_enabled` - Email notifikacije

**Settings (Podešavanja):**
- `max_poll_options` - Maksimalan broj opcija u poll-u (default: 5)
- `max_prediction_time` - Vreme trajanja predikcije (default: 3600s = 1h)
- `leaderboard_refresh_interval` - Interval refresh-a (default: 30s)
- `chat_message_limit` - Limit poruka u chat-u (default: 200)

**Maintenance Mode:**
- Uključite održavanje kada radite update-ove
- Svi korisnici dobijaju poruku da je sistem u održavanju

**Announcements:**
- Pošaljite globalnu poruku svim korisnicima
- Npr. "Nova funkcija dostupna!" ili "Planirano održavanje"

### Backend API Endpoints:

```
GET  /api/remote/remote-config         - Učitaj daljinsku konfiguraciju
POST /api/remote/update-remote-config  - Ažuriraj konfiguraciju (ADMIN)
POST /api/remote/command                - Pošalji komandu instalaciji (ADMIN)
GET  /api/remote/pending-commands/{id} - Preuzmi pending komande
POST /api/remote/command-executed      - Označi komandu kao izvršenu
GET  /api/remote/installation-status   - Status svih instalacija (ADMIN)
GET  /api/remote/analytics             - Analytics dashboard (ADMIN)
WS   /api/remote/monitor/{id}          - WebSocket real-time monitoring
```

### Remote Commands:

**Dostupne komande:**
- `restart` - Restartuj instalaciju
- `clear_cache` - Obriši keš
- `update_config` - Ažuriraj konfiguraciju
- `enable_feature` - Uključi funkcionalnost
- `disable_feature` - Isključi funkcionalnost

**Primeri:**

```javascript
// Restart sve instalacije
POST /api/remote/command
{
  "command": "restart",
  "target": "all",
  "params": {}
}

// Uključi polls za određenu instalaciju
POST /api/remote/command
{
  "command": "enable_feature",
  "target": "installation-12345",
  "params": {"feature": "polls_enabled"}
}
```

---

## 📊 REAL-TIME MONITORING

### Šta se prati?

Svaka instalacija šalje **real-time status**:
- CPU usage (%)
- Memory usage (%)
- Disk usage (%)
- Uptime (sekunde)
- Error count
- Last error message

### WebSocket Connection:

```javascript
// Instalacija se povezuje sa serverom
const ws = new WebSocket('wss://api.019solutions.com/api/remote/monitor/{installation_id}');

// Šalje status svakih 30 sekundi
ws.send(JSON.stringify({
  status: "active",
  cpu_usage: 25.5,
  memory_usage: 512,
  disk_usage: 45.2,
  uptime: 86400,
  error_count: 0
}));
```

---

## 🔐 SECURITY & AUTHENTICATION

### Admin Authentication:

Svi admin endpoint-i zahtevaju JWT token:

```
Authorization: Bearer <admin_token>
```

### Installation ID:

Svaka instalacija dobija **jedinstveni ID**:
```
installation_id = "remza-gaming-{platform}-{timestamp}-{random}"
```

---

## 📈 DEPLOYMENT ANALYTICS

### Admin Dashboard Metrics:

**Instalacije:**
- Total installations
- Platform distribution (web/desktop/mobile)
- OS distribution (Windows/Mac/Linux/iOS/Android)
- Version distribution

**Activity:**
- Active installations (last 5 min)
- Inactive installations
- Error count
- Recent registrations (last 7 days)

**Auto-Update:**
- Users with auto-update enabled
- Users with auto-update disabled

---

## 🚀 KAKO KORISTITI?

### Za Desktop Instalacije:

1. **Instalacija registruje sebe:**
```javascript
POST /api/version/register-installation
{
  "installation_id": "unique-id",
  "version": "1.0.0",
  "platform": "desktop",
  "os": "windows",
  "last_check": "2025-01-18T12:00:00",
  "auto_update_enabled": true
}
```

2. **Periodični heartbeat (svakih 5 minuta):**
```javascript
POST /api/version/heartbeat?installation_id=unique-id
```

3. **Provera pending komandi (svakih 30 sekundi):**
```javascript
GET /api/remote/pending-commands/unique-id
```

4. **Izvršavanje komandi:**
```javascript
// Aplikacija prima komandu
{
  "command": "restart",
  "params": {}
}

// Izvršava komandu i obaveštava server
POST /api/remote/command-executed
{
  "command_id": "cmd-123",
  "installation_id": "unique-id",
  "success": true,
  "result": "Restarted successfully"
}
```

### Za Admin:

**Admin Panel → Remote Management Tab:**
- View all installations
- Send commands
- Toggle feature flags
- Update settings
- View analytics

---

## 🔧 CONFIGURATION

### Environment Variables:

```env
# Version Management
CURRENT_VERSION=1.0.0
BUILD_NUMBER=20250118001
VERSION_NAME="NIVO 1 - Engagement Edition"

# Auto-Update Server
UPDATE_SERVER_URL=https://019solutions.com/downloads
UPDATE_CHECK_INTERVAL=1800  # 30 minutes in seconds

# Remote Management
ENABLE_REMOTE_MANAGEMENT=true
HEARTBEAT_INTERVAL=300  # 5 minutes in seconds
COMMAND_CHECK_INTERVAL=30  # 30 seconds
```

---

## 📞 SUPPORT

**019Solutions Team:**
- Email: support@019solutions.com
- Website: https://019solutions.com
- Discord: discord.gg/019solutions

---

## 📝 VERSION HISTORY

### v1.0.0 - NIVO 1 (2025-01-18)
- ✅ Auto-update system
- ✅ Remote management & monitoring
- ✅ Version tracking
- ✅ Installation analytics
- ✅ Feature flags
- ✅ Remote commands
- ✅ WebSocket monitoring

**Previous Versions:** See `/api/version/changelog`

---

## ⚠️ IMPORTANT NOTES

1. **Privacy:** Installation ID je anoniman, ne prati lične podatke
2. **Security:** Sve komande zahtevaju admin autentikaciju
3. **Bandwidth:** Heartbeat koristi < 1KB svakih 5 minuta
4. **Offline Mode:** Softver radi i offline, samo nema auto-update
5. **Manual Override:** Korisnik može uvek ručno preuzeti update

---

**Powered by 019Solutions** 💚
