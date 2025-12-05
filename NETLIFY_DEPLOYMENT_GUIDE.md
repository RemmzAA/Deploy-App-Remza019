# 🚀 Netlify Deployment Guide
## 019 Solutions Platform

**Last Updated:** December 2024
**Status:** Ready for deployment

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### ✅ Completed
- [x] Frontend build configured (`yarn build`)
- [x] `netlify.toml` configuration exists
- [x] `_redirects` file for React Router
- [x] Security headers configured
- [x] Environment variables identified
- [x] Rebranding to "019 Solutions" completed
- [x] Twitch API integration tested and working

### ⚠️ Required Before Deployment
- [ ] Backend deployed to Render.com (or similar)
- [ ] Backend URL obtained
- [ ] Environment variables set in Netlify

---

## 🎯 DEPLOYMENT STEPS

### Step 1: Deploy Backend First (Render.com or Railway)

**Why Backend First?**
- Frontend needs backend API URL
- Cannot test frontend properly without backend

**Backend Deployment Options:**

#### Option A: Render.com (Recommended)
1. Go to https://render.com
2. Create new "Web Service"
3. Connect GitHub repo
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Root Directory:** `backend`
5. Add Environment Variables (see section below)
6. Deploy!
7. **Copy the URL** (e.g., `https://019-solutions.onrender.com`)

#### Option B: Railway.app
1. Go to https://railway.app
2. Create new project from GitHub
3. Similar configuration as Render
4. Copy deployment URL

---

### Step 2: Configure Netlify Environment Variables

Once backend is deployed, configure these in **Netlify Dashboard → Site Settings → Environment Variables:**

```bash
# Backend URL (from Render/Railway)
REACT_APP_BACKEND_URL=https://YOUR_BACKEND_URL.onrender.com

# Optional: Analytics
REACT_APP_GA_ID=your_google_analytics_id
```

**Important:** 
- Only variables prefixed with `REACT_APP_` are exposed to browser
- Sensitive backend keys should NEVER be in frontend env vars

---

### Step 3: Update netlify.toml

Update line 29 in `/app/frontend/netlify.toml`:

```toml
# Before:
to = "https://YOUR_BACKEND_URL.onrender.com/api/:splat"

# After (replace with your actual backend URL):
to = "https://019-solutions.onrender.com/api/:splat"
```

Also update `/app/frontend/public/_redirects` line 5:
```
/api/*  https://019-solutions.onrender.com/api/:splat  200
```

---

### Step 4: Deploy to Netlify

#### Method 1: Netlify CLI (Recommended)

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Navigate to frontend
cd /app/frontend

# Initialize Netlify site
netlify init

# Deploy
netlify deploy --prod
```

#### Method 2: Netlify UI (Easier)

1. Go to https://app.netlify.com
2. Click "Add new site" → "Import an existing project"
3. Connect to your Git provider (GitHub/GitLab/Bitbucket)
4. Select repository
5. Configure build settings:
   - **Base directory:** `frontend`
   - **Build command:** `yarn build`
   - **Publish directory:** `frontend/build`
6. Add environment variables (from Step 2)
7. Click "Deploy site"

#### Method 3: Drag & Drop (Quick Test)

```bash
# Build locally
cd /app/frontend
yarn build

# Drag the 'build' folder to Netlify dashboard
```

---

## 🔐 ENVIRONMENT VARIABLES REFERENCE

### Frontend (.env)
These should be set in **Netlify Dashboard:**

```bash
# Backend API URL
REACT_APP_BACKEND_URL=https://your-backend.onrender.com

# Optional Analytics
REACT_APP_GA_ID=G-XXXXXXXXXX
```

### Backend (Render.com/Railway)
These should be set in **Render/Railway Dashboard:**

```bash
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=production_database

# CORS
CORS_ORIGINS=https://your-netlify-site.netlify.app
ALLOWED_ORIGINS=https://your-netlify-site.netlify.app

# YouTube
YOUTUBE_API_KEY=your_youtube_key
YOUTUBE_CHANNEL_ID=UC-remza019

# Twitch (NEW - Working!)
TWITCH_CLIENT_ID=8s92f8bkxx1g9mapxbinfclba6prdt
TWITCH_CLIENT_SECRET=dp0kyqlimve2k4cg12a7a2ekyv8g8y

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your_email@gmail.com
FROM_NAME=019 Solutions

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here

# Discord (Optional)
DISCORD_BOT_TOKEN=your_discord_token
```

---

## 📊 POST-DEPLOYMENT VERIFICATION

After deployment, test these:

### 1. Frontend Tests
- [ ] Site loads correctly
- [ ] All pages accessible (/, /admin, /member)
- [ ] Assets loading (images, CSS, JS)
- [ ] No console errors

### 2. API Connection Tests
```bash
# Test backend health
curl https://your-backend.onrender.com/api/schedule

# Test Twitch integration
curl https://your-backend.onrender.com/api/twitch/health
```

### 3. Frontend API Calls
- [ ] Schedule loads on homepage
- [ ] Twitch status updates (if streaming)
- [ ] Admin login works
- [ ] Member registration works

---

## 🚨 COMMON ISSUES & SOLUTIONS

### Issue 1: "Failed to fetch" errors
**Cause:** CORS not configured properly
**Solution:** 
1. Check `CORS_ORIGINS` in backend .env
2. Must include your Netlify URL (without trailing slash)
3. Restart backend after env change

### Issue 2: Blank page after deployment
**Cause:** Environment variable not set
**Solution:**
1. Check Netlify env vars include `REACT_APP_BACKEND_URL`
2. Redeploy after adding

### Issue 3: API calls return 404
**Cause:** Backend not deployed or wrong URL
**Solution:**
1. Verify backend is running
2. Check `netlify.toml` redirect URL is correct
3. Check `_redirects` file

### Issue 4: Build fails on Netlify
**Cause:** Missing dependencies or Node version
**Solution:**
1. Check `netlify.toml` has `NODE_VERSION = "18"`
2. Ensure all dependencies in `package.json`
3. Check build logs for specific errors

---

## 🔄 CONTINUOUS DEPLOYMENT

Once set up, automatic deployment works like this:

1. **Push to main branch** → Netlify auto-deploys frontend
2. **Push to main branch** → Render auto-deploys backend
3. No manual intervention needed!

**Branch Deploy Previews:**
- Netlify creates preview for each Pull Request
- Test changes before merging to main

---

## 📈 MONITORING & PERFORMANCE

### Netlify Analytics
- Enable in Netlify Dashboard
- Track visitors, bandwidth, performance

### Backend Monitoring (Render)
- View logs in Render Dashboard
- Set up health check endpoint
- Configure auto-scaling if needed

### Uptime Monitoring
Recommended services:
- UptimeRobot (free)
- Pingdom
- Better Uptime

---

## 💰 COST ESTIMATE

### Free Tier (Perfect for starting)
- **Netlify:** 100GB bandwidth/month (Free)
- **Render:** 750 hours/month (Free)
- **MongoDB Atlas:** 512MB storage (Free)

### Paid Tier (For production)
- **Netlify Pro:** $19/month (1TB bandwidth)
- **Render Starter:** $7/month (Always on)
- **MongoDB Atlas:** $9/month (2GB storage)

**Total:** ~$35/month for full production setup

---

## 📝 DEPLOYMENT CHECKLIST SUMMARY

Before clicking deploy:

1. ✅ Backend deployed and URL obtained
2. ✅ `netlify.toml` updated with backend URL
3. ✅ `_redirects` updated with backend URL
4. ✅ Environment variables set in Netlify
5. ✅ CORS configured in backend
6. ✅ Database accessible from backend
7. ✅ All API keys added to backend env

After deployment:

1. ✅ Test homepage loads
2. ✅ Test API endpoints
3. ✅ Test admin login
4. ✅ Test member features
5. ✅ Check console for errors
6. ✅ Test on mobile device

---

## 🎯 NEXT STEPS

1. **Deploy Backend:** Choose Render.com or Railway
2. **Get Backend URL:** Copy from deployment
3. **Update Configs:** Modify `netlify.toml` and `_redirects`
4. **Set Env Vars:** Add in Netlify dashboard
5. **Deploy Frontend:** Push to Netlify
6. **Test Everything:** Verify all features work
7. **Monitor:** Set up uptime monitoring

---

## 🆘 NEED HELP?

If you encounter issues:
1. Check deployment logs (Netlify Dashboard → Deploys → View Log)
2. Check backend logs (Render Dashboard → Logs)
3. Use browser DevTools Console for frontend errors
4. Check Network tab for failed API calls

**Common Commands:**
```bash
# Test build locally
yarn build

# View build output
ls -la build/

# Test production build locally
npx serve -s build

# Clear Netlify cache and redeploy
netlify deploy --prod --clear-cache
```

---

**Deployment Status:** ⏳ Ready to Deploy
**Next Action:** Deploy backend to Render.com
