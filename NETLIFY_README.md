# 🌐 Netlify Deployment - REMZA019 Gaming

Quick reference za Netlify deployment.

---

## 📂 Files Created:

- ✅ `netlify.toml` - Build configuration
- ✅ `public/_redirects` - Routing rules
- ✅ `.env.production.example` - Environment template
- ✅ `pre-deploy.sh` - Pre-deployment validation script

---

## ⚡ Quick Deploy Commands:

```bash
# 1. Pripremi production config
cd /app/frontend
cp .env.production.example .env.production

# 2. Ažuriraj backend URL u .env.production
nano .env.production
# Postavi: REACT_APP_BACKEND_URL=https://YOUR_BACKEND.onrender.com

# 3. Ažuriraj netlify.toml (linija 24)
nano netlify.toml
# Zameni: YOUR_BACKEND_URL sa tvojim backend URL

# 4. Run pre-deployment check
./pre-deploy.sh

# 5. Test build lokalno
yarn build

# 6. Deploy
# - Manual: Drag & drop build/ folder na netlify.com
# - Auto: Connect GitHub repo na Netlify
```

---

## 🔧 Netlify Environment Variables:

U Netlify UI dodaj:

```
REACT_APP_BACKEND_URL=https://YOUR_BACKEND.onrender.com
NODE_VERSION=18
CI=false
GENERATE_SOURCEMAP=false
```

---

## 🚀 Build Settings:

```
Base directory: frontend
Build command: yarn build
Publish directory: frontend/build
```

---

## 🔀 Redirect Rules:

Redirects su konfigurisani u:
1. `netlify.toml` (primary)
2. `public/_redirects` (backup)

**API Proxy:**
- Frontend `/api/*` → Backend `https://YOUR_BACKEND.onrender.com/api/*`

**React Router:**
- All routes → `index.html` (SPA routing)

---

## 🧪 Testing Deployment:

```bash
# Test backend connection
curl https://YOUR_BACKEND.onrender.com/api/version/current

# Test frontend
open https://YOUR_SITE.netlify.app

# Test API proxy
curl https://YOUR_SITE.netlify.app/api/version/current
```

---

## 🐛 Common Issues:

**1. API calls failing (404/CORS)**
- Check `REACT_APP_BACKEND_URL` in environment variables
- Check `netlify.toml` redirect rules
- Check backend `ALLOWED_ORIGINS`

**2. Build fails**
- Check `NODE_VERSION=18` in environment
- Check `CI=false` (disables treating warnings as errors)
- Check build logs for specific errors

**3. Routes not working (404 on refresh)**
- Check `public/_redirects` file exists
- Check `netlify.toml` has `[[redirects]]` section

**4. Slow cold starts**
- Render.com free tier spins down after 15 min inactivity
- First request takes 30-60s to wake up
- Solution: Upgrade to Render Starter ($7/month) for always-on

---

## 💡 Performance Tips:

1. **Enable Netlify CDN:**
   - Automatic with Netlify

2. **Optimize Images:**
   - Use WebP format
   - Compress before upload
   - Lazy loading implemented

3. **Code Splitting:**
   - React.lazy() for route-based splitting
   - Reduces initial bundle size

4. **Service Worker:**
   - PWA features enabled
   - Offline caching

---

## 📊 Netlify Dashboard:

- **Site Overview:** Build status, deploy history
- **Analytics:** Pageviews, bandwidth usage
- **Domain Management:** Custom domain, SSL
- **Environment Variables:** Secrets management
- **Deploy Previews:** Test before merge

---

## 🔒 Security Headers:

Configured in `netlify.toml`:
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: enabled
- Referrer-Policy: strict-origin
- Permissions-Policy: restricted

---

## 📈 Monitoring:

**Netlify Analytics:**
- Site → Analytics tab
- Pageviews, unique visitors
- Top pages, referrers

**Uptime Monitoring:**
- Use UptimeRobot.com (free)
- Monitor: `https://YOUR_SITE.netlify.app`

---

## 🎯 Post-Deployment Checklist:

- [ ] Site loads correctly
- [ ] Admin login works
- [ ] YouTube videos display
- [ ] License activation works
- [ ] Email registration works
- [ ] All themes work
- [ ] Mobile responsive
- [ ] PWA install works

---

## 🆘 Need Help?

- Netlify Docs: https://docs.netlify.com
- Netlify Support: https://answers.netlify.com
- Community Discord: https://netlifycommunity.slack.com

---

**🎉 Happy Deploying!** 🚀
