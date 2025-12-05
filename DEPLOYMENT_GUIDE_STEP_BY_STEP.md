# 🚀 019 Solutions - Deployment Guide (Step-by-Step)

## ✅ KORAK 1: MongoDB Atlas - ZAVRŠENO!

- [x] MongoDB cluster kreiran
- [x] Database user: `019solutions`
- [x] Password: `EjXHoowNCbV03ZdH`
- [x] IP whitelist: Omogućeno za sve IP adrese
- [x] Connection string: Ready!

---

## 🎯 KORAK 2: Backend Deployment na Render.com

### 2.1 - Idi na Render Dashboard

**Tvoje akcije:**
1. Otvori: **https://dashboard.render.com**
2. Ako nemaš account, registruj se (koristi GitHub login za jednostavnost)
3. Ako već imaš account, login

---

### 2.2 - Kreiraj Nov Web Service

**Tvoje akcije:**
1. **Klikni:** Plavo dugme **"New +"** (gore desno)
2. **Izaberi:** "Web Service"
3. **Connect GitHub:**
   - Klikni "Connect GitHub" (ili "Configure account" ako je prvi put)
   - Autorizuj Render da pristupa GitHub account-u
   - Izaberi repository: `019-solutions-platform` (ili kako si ga nazvao)
4. **Klikni:** "Connect" na tvom repository

---

### 2.3 - Konfiguriši Web Service

**Popuni sledeća polja:**

```
Name: 019-solutions-backend
Region: Frankfurt (EU Central)
Branch: main
Root Directory: backend
Runtime: Python 3
```

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
uvicorn server:app --host 0.0.0.0 --port $PORT
```

**Instance Type:**
- Free (za testiranje)

---

### 2.4 - Dodaj Environment Variables

**JAKO VAŽNO!** Klikni "Advanced" i dodaj ove environment variables:

**OBAVEZNE:**
```
MONGO_URL = mongodb+srv://019solutions:EjXHoowNCbV03ZdH@cluster0.fwwuoif.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0

DB_NAME = 019solutions_production

SECRET_KEY = xYetO1tpa_1dPXsA9cEU3XXtu9QE9tooHdj8_AxTNq4

JWT_SECRET = xYetO1tpa_1dPXsA9cEU3XXtu9QE9tooHdj8_AxTNq4

CORS_ORIGINS = http://localhost:3000

ALLOWED_ORIGINS = http://localhost:3000

FROM_NAME = 019 Solutions
```

**OPCIONE (možeš dodati kasnije):**
```
SMTP_HOST = smtp.gmail.com
SMTP_PORT = 587
SMTP_USER = your_email@gmail.com
SMTP_PASSWORD = your_app_password
FROM_EMAIL = your_email@gmail.com
FRONTEND_URL = http://localhost:3000

TWITCH_CLIENT_ID = 8s92f8bkxx1g9mapxbinfclba6prdt
TWITCH_CLIENT_SECRET = dp0kyqlimve2k4cg12a7a2ekyv8g8y

YOUTUBE_API_KEY = (tvoj API key)
YOUTUBE_CHANNEL_ID = UC-remza019

EMERGENT_LLM_KEY = (dobij iz emergent_integrations_manager)
```

---

### 2.5 - Kreiraj Service

**Tvoje akcije:**
1. **Klikni:** Zeleno dugme **"Create Web Service"** (na dnu)
2. **Čekaj:** 5-10 minuta da se build završi
3. **Gledaj logs** u real-time - trebalo bi da vidiš:
   ```
   Build successful
   Starting server...
   Uvicorn running on http://0.0.0.0:8001
   ```

---

### 2.6 - Kopiraj Backend URL

**Nakon uspešnog deploya:**
1. **Kopiraj URL** koji Render kreira (npr: `https://019-solutions-backend.onrender.com`)
2. **Sačuvaj ovaj URL** - trebamo ga za frontend!

---

### 2.7 - Testiraj Backend

**U browseru, otvori:**
```
https://TVOJ-BACKEND-URL.onrender.com/api/schedule
```

**Trebalo bi da vidiš JSON response sa schedule podacima!**

Ako vidiš JSON, backend radi! ✅

---

## 🎯 KORAK 3: Frontend Deployment na Netlify

### 3.1 - Ažuriraj Backend URL u Kodu

**Ja ću ažurirati ove fajlove sa tvojim backend URL-om:**
- `/app/frontend/netlify.toml`
- `/app/frontend/public/_redirects`

**Daću ti da commit-uješ i push-uješ promene na GitHub.**

---

### 3.2 - Idi na Netlify Dashboard

**Tvoje akcije:**
1. Otvori: **https://app.netlify.com**
2. Login (ako već imaš account)
3. **Klikni:** "Add new site" → "Import an existing project"

---

### 3.3 - Connect GitHub

**Tvoje akcije:**
1. **Izaberi:** GitHub
2. **Autorizuj** Netlify (ako je prvi put)
3. **Izaberi repository:** `019-solutions-platform`
4. **Klikni:** "Deploy site"

---

### 3.4 - Konfiguriši Build Settings

**U Netlify UI:**

**VAŽNO:** Ostavi Base directory **PRAZNO** (jer netlify.toml je već u frontend/ folderu)

```
Base directory: (PRAZNO!)
Build command: yarn build
Publish directory: frontend/build
```

---

### 3.5 - Dodaj Environment Variable

**Klikni:** "Add environment variables"

**Dodaj:**
```
Key: REACT_APP_BACKEND_URL
Value: https://TVOJ-BACKEND-URL.onrender.com
```

(Zameni sa pravim backend URL-om iz koraka 2.6)

---

### 3.6 - Deploy!

**Tvoje akcije:**
1. **Klikni:** "Deploy site"
2. **Čekaj:** 2-3 minuta
3. **Gledaj build log** - trebalo bi da vidiš:
   ```
   Build successful
   Site is live!
   ```

---

### 3.7 - Ažuriraj Backend CORS

**JAKO VAŽNO!** Sada kada imaš Netlify URL, vrati se na Render:

1. **Idi na:** Render Dashboard → Tvoj backend service
2. **Klikni:** "Environment" (levo meni)
3. **Ažuriraj:**
   ```
   CORS_ORIGINS = https://tvoj-site.netlify.app,http://localhost:3000
   ALLOWED_ORIGINS = https://tvoj-site.netlify.app,http://localhost:3000
   ```
4. **Sačuvaj** i backend će se automatski restart-ovati

---

## 🎉 GOTOVO!

### Test URLs:

**Frontend:**
```
https://tvoj-site.netlify.app
```

**Backend:**
```
https://tvoj-backend.onrender.com/api/schedule
```

### Test Flow:
1. Otvori frontend URL
2. Trebalo bi da vidiš homepage sa schedule-om
3. Testiraj login/register
4. Testiraj admin panel

---

## 🐛 Troubleshooting

### Backend ne radi:
1. Proveri Render logs
2. Proveri da su environment variables pravilno postavljene
3. Proveri MongoDB connection string

### Frontend ne dobija podatke od backend-a:
1. Proveri CORS settings u backend-u
2. Proveri da je `REACT_APP_BACKEND_URL` pravilno postavljen
3. Otvori browser Console (F12) i gledaj Network tab

### Database prazan:
- Normalno! Nova baza je prazna
- Admin account će biti kreiran na prvom pokretanju
- Schedule će biti inicijalizovan automatski

---

## 📞 Sledeći Koraci

Nakon uspešnog deploya:
1. Kreiraj admin account
2. Dodaj schedule data
3. Konfiguriši email (SMTP)
4. Dodaj custom domain (opciono)
5. Monitor performance

---

**Sve je spremno! Idemo na Render deployment! 🚀**
