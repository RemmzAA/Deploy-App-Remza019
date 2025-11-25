# 🚀 REMZA019 Gaming - Deployment Guide

Kompletan vodič za deployment aplikacije na Netlify (Frontend) i Render.com (Backend).

---

## 📋 Pre-Deployment Checklist

- [ ] GitHub/GitLab repository kreiran
- [ ] Netlify account kreiran (https://netlify.com)
- [ ] Render.com account kreiran (https://render.com)
- [ ] MongoDB Atlas account kreiran (https://mongodb.com/cloud/atlas)
- [ ] Spremni API keys i credentials

---

## 🗄️ KORAK 1: MongoDB Atlas Setup

### 1.1 Kreiranje Cluster-a

1. Idite na https://mongodb.com/cloud/atlas
2. Kreirajte besplatni M0 Cluster
3. Izaberite region (preporučeno: Frankfurt ili najbliži)
4. Kliknite "Create Cluster"

### 1.2 Database Access

1. Security → Database Access
2. Add New Database User
   - Username: `remza019_admin`
   - Password: (generiši jak password)
   - Database User Privileges: "Atlas Admin"
3. Sačuvajte kredencijale!

### 1.3 Network Access

1. Security → Network Access
2. Add IP Address
3. Izaberite "Allow Access from Anywhere" (0.0.0.0/0)
   - Za production, ograničite na Render.com IP-ove

### 1.4 Connection String

1. Databases → Connect → Connect your application
2. Kopirajte Connection String:
   ```
   mongodb+srv://remza019_admin:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
3. Zamenite `<password>` sa vašim passwordom
4. Dodajte database name: `/remza019_gaming`

**Final Connection String:**
```
mongodb+srv://remza019_admin:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/remza019_gaming?retryWrites=true&w=majority
```

---

## 🖥️ KORAK 2: Backend Deployment (Render.com)

### 2.1 Kreiranje Web Service

1. Idite na https://render.com
2. New → Web Service
3. Connect GitHub/GitLab repository
4. Konfiguracija:
   - **Name**: `remza019-gaming-backend`
   - **Environment**: `Python 3`
   - **Region**: `Frankfurt` (ili najbliži)
   - **Branch**: `main`
   - **Build Command**: 
     ```bash
     cd backend && pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Free

### 2.2 Environment Variables

Dodajte sledeće environment variables u Render.com:

```env
# MongoDB
MONGO_URL=mongodb+srv://remza019_admin:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/remza019_gaming

# Email (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=vladicaristic19@gmail.com
SMTP_PASSWORD=ksin ybiw kakx udij
FROM_EMAIL=vladicaristic19@gmail.com
FROM_NAME=REMZA019 Gaming

# YouTube API
YOUTUBE_API_KEY=AIzaSyC-xuYH0JmmfnCx7ZuwTprZcyj3lk7wkS0
YOUTUBE_CHANNEL_ID=@remza019

# Discord
DISCORD_BOT_TOKEN=
DISCORD_NOTIFICATION_CHANNEL=

# OBS WebSocket (optional)
OBS_HOST=localhost
OBS_PORT=4455
OBS_PASSWORD=

# Twitch (optional)
TWITCH_CLIENT_ID=
TWITCH_CLIENT_SECRET=

# Frontend URL (update after Netlify deployment)
FRONTEND_URL=https://YOUR_NETLIFY_SITE.netlify.app

# Security
SECRET_KEY=generate-a-long-random-secret-key-here-minimum-32-chars

# CORS Origins (add Netlify URL)
ALLOWED_ORIGINS=https://YOUR_NETLIFY_SITE.netlify.app,http://localhost:3000
```

### 2.3 Deploy

1. Kliknite "Create Web Service"
2. Sačekajte deployment (3-5 minuta)
3. **Kopirajte Backend URL**: `https://remza019-gaming-backend.onrender.com`

---

## 🌐 KORAK 3: Frontend Deployment (Netlify)

### 3.1 Priprema Projekta

1. Ažurirajte `/app/frontend/.env.production`:
   ```env
   REACT_APP_BACKEND_URL=https://remza019-gaming-backend.onrender.com
   GENERATE_SOURCEMAP=false
   ```

2. Ažurirajte `/app/frontend/netlify.toml`:
   ```toml
   [[redirects]]
     from = "/api/*"
     to = "https://remza019-gaming-backend.onrender.com/api/:splat"
     status = 200
     force = true
   ```

### 3.2 Deploy na Netlify

**Opcija A: Git-based Deployment (Preporučeno)**

1. Push kod na GitHub/GitLab
2. Idite na https://netlify.com
3. New site from Git
4. Connect repository
5. Configure:
   - **Base directory**: `frontend`
   - **Build command**: `yarn build`
   - **Publish directory**: `frontend/build`
6. Environment variables:
   ```
   REACT_APP_BACKEND_URL=https://remza019-gaming-backend.onrender.com
   NODE_VERSION=18
   CI=false
   ```
7. Deploy site

**Opcija B: Manual Deployment**

1. Lokalno build:
   ```bash
   cd /app/frontend
   yarn build
   ```

2. Drag & Drop `build` folder na Netlify

### 3.3 Custom Domain (Opciono)

1. Domain settings → Add custom domain
2. Unesite domain (npr. `remza019gaming.com`)
3. Konfigurirajte DNS:
   - A Record: `75.2.60.5`
   - CNAME: `YOUR_SITE.netlify.app`
4. SSL certificate se auto-generiše

---

## 🔧 KORAK 4: Post-Deployment Configuration

### 4.1 Ažuriranje Backend FRONTEND_URL

1. U Render.com environment variables:
   ```
   FRONTEND_URL=https://YOUR_SITE.netlify.app
   ```

2. Ažuriranje ALLOWED_ORIGINS:
   ```
   ALLOWED_ORIGINS=https://YOUR_SITE.netlify.app,http://localhost:3000
   ```

3. Redeploy backend

### 4.2 Testiranje

**Backend Health Check:**
```bash
curl https://remza019-gaming-backend.onrender.com/api/version/current
```

**Frontend:**
1. Otvorite `https://YOUR_SITE.netlify.app`
2. Testirajte:
   - YouTube integration
   - Admin login (admin/remza019admin)
   - License activation
   - Email registration

### 4.3 MongoDB Data Migration

Ako želite migrovati postojeće podatke:

```bash
# Export from local
mongodump --uri="mongodb://localhost:27017/remza019_gaming" --out=./dump

# Import to Atlas
mongorestore --uri="mongodb+srv://user:pass@cluster0.xxxxx.mongodb.net/remza019_gaming" ./dump/remza019_gaming
```

---

## 📊 KORAK 5: Monitoring & Maintenance

### 5.1 Render.com Monitoring

- Dashboard → Metrics (CPU, Memory, Response Time)
- Logs → Real-time logs
- Uptime checks

### 5.2 Netlify Monitoring

- Site overview → Analytics
- Deploy log
- Function logs

### 5.3 MongoDB Atlas Monitoring

- Metrics → Performance
- Real-time performance panel
- Alerts setup

---

## 🔒 Security Best Practices

1. **Environment Variables**: Nikada ne commit-ujte .env fajlove
2. **CORS**: Ograničite ALLOWED_ORIGINS samo na production domene
3. **MongoDB**: Ograničite Network Access na Render.com IP-ove
4. **API Keys**: Rotirajte keys periodično
5. **SSL/TLS**: Netlify i Render auto-enable HTTPS

---

## 💰 Cost Estimate

| Service | Plan | Cost |
|---------|------|------|
| Netlify | Starter | **FREE** (100GB bandwidth) |
| Render.com | Free | **FREE** (750 hours/month) |
| MongoDB Atlas | M0 | **FREE** (512MB storage) |
| **TOTAL** | | **$0/month** |

**Upgrade kada treba:**
- Netlify Pro: $19/month (više bandwidth)
- Render Starter: $7/month (always-on, više resources)
- MongoDB M10: $9/month (2GB RAM, više storage)

---

## 🐛 Troubleshooting

### Backend ne startuje
- Proverite environment variables
- Proverite MongoDB connection string
- Proverite logs u Render.com

### Frontend ne može da komunicira sa Backend-om
- Proverite REACT_APP_BACKEND_URL
- Proverite CORS settings u backend-u
- Proverite Network tab u DevTools

### MongoDB connection timeout
- Proverite Network Access (0.0.0.0/0)
- Proverite Database User credentials
- Proverite connection string format

---

## 📞 Support

Za pomoć:
- Render.com Docs: https://render.com/docs
- Netlify Docs: https://docs.netlify.com
- MongoDB Atlas Docs: https://docs.atlas.mongodb.com

---

**🎉 Čestitamo! Vaša aplikacija je sada live!** 🚀
