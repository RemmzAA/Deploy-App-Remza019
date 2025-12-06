# 🚀 RENDER.COM ENVIRONMENT VARIABLES SETUP

## ⚠️ VAŽNO: ENVIRONMENT VARIABLES

Environment variables **NISU** u ovom repository-ju zbog bezbednosti.

---

## 📝 KAKO DODATI NA RENDER.COM:

### Korak 1: Otvorite Render Dashboard
👉 https://dashboard.render.com

### Korak 2: Pronađite Backend Servis
Kliknite na vaš backend servis

### Korak 3: Idite na Environment Tab
U levom meniju → **"Environment"**

### Korak 4: Dodajte Variables

Za SVAKU environment variable:
1. Kliknite **"Add Environment Variable"**
2. Unesite **Key** i **Value**
3. Kliknite **"Save"**

---

## 📋 POTREBNE ENVIRONMENT VARIABLES:

```
MONGO_URL
DB_NAME
CORS_ORIGINS
ALLOWED_ORIGINS
SECRET_KEY
JWT_SECRET
SMTP_HOST
SMTP_PORT
SMTP_USER
SMTP_PASSWORD
FROM_EMAIL
FROM_NAME
FRONTEND_URL
TWITCH_CLIENT_ID
TWITCH_CLIENT_SECRET
YOUTUBE_API_KEY
YOUTUBE_CHANNEL_ID
DISCORD_BOT_TOKEN
EMERGENT_LLM_KEY
PORT
```

**NAPOMENA:** Vrednosti za ove variables su u vašem lokalnom `.env` fajlu ili u vašem password manager-u.

**NIKAD** ne commit-ujte prave vrednosti na GitHub!

---

## 🔐 BEZBEDNOST:

- ✅ `.env` fajlovi su u `.gitignore`
- ✅ Nikad ne push-ujte API ključeve
- ✅ Koristite Render dashboard za env variables
- ✅ Ne delite credentials javno

---

## ✅ NAKON DODAVANJA:

1. Kliknite **"Manual Deploy"**
2. Sačekajte 5-10 minuta
3. Backend će raditi sa novim credentials

---

**Za pitanja kontaktirajte developera.**
