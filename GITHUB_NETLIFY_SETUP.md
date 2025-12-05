# 🔗 GitHub → Netlify Deployment Setup
## 019 Solutions Platform

**Step-by-Step Guide to Connect Your Repo with Netlify**

---

## 📋 PRE-REQUISITES

- [ ] GitHub account
- [ ] Netlify account (free tier works)
- [ ] Backend deployed somewhere (Render/Railway/Emergent)
- [ ] Backend URL ready

---

## 🚀 STEP-BY-STEP PROCESS

### Step 1: Push Code to GitHub

**Option A: Via Emergent Platform (Easiest)**
1. In Emergent chat interface, look for "Save to GitHub" button
2. Click and follow prompts to connect GitHub
3. Repository will be created automatically

**Option B: Manual GitHub Push (If Option A not available)**

```bash
# 1. Create new repo on GitHub (https://github.com/new)
#    Name: 019-solutions-platform
#    Don't initialize with README

# 2. Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/019-solutions-platform.git

# 3. Commit current changes
git add .
git commit -m "Prepare for Netlify deployment"

# 4. Push to GitHub
git branch -M main
git push -u origin main
```

---

### Step 2: Connect GitHub to Netlify

1. **Go to Netlify:** https://app.netlify.com
2. **Click:** "Add new site" → "Import an existing project"
3. **Choose:** GitHub (authorize if needed)
4. **Select:** Your repository (019-solutions-platform)

---

### Step 3: Configure Build Settings

In Netlify, configure these settings:

```
Base directory: frontend
Build command: yarn build
Publish directory: frontend/build
```

**Important:** 
- Base directory must be `frontend` (not empty!)
- This tells Netlify where your React app is

---

### Step 4: Add Environment Variables

In Netlify Dashboard → Site Settings → Environment Variables, add:

**Required:**
```
REACT_APP_BACKEND_URL = https://your-backend-url.onrender.com
```

**Optional (if you have):**
```
REACT_APP_GA_ID = G-XXXXXXXXXX
```

**Important Notes:**
- Only `REACT_APP_*` variables are exposed to browser
- Never put backend secrets here!
- Backend secrets go in backend hosting (Render/Railway)

---

### Step 5: Update netlify.toml (IMPORTANT!)

Before deploying, you MUST update the backend URL in `/app/frontend/netlify.toml`:

**Find line 29:**
```toml
to = "https://YOUR_BACKEND_URL.onrender.com/api/:splat"
```

**Replace with your actual backend URL:**
```toml
to = "https://019-solutions-backend.onrender.com/api/:splat"
```

**Commit and push this change:**
```bash
git add frontend/netlify.toml
git commit -m "Update backend URL for production"
git push
```

---

### Step 6: Deploy!

1. **Click:** "Deploy site" in Netlify
2. **Wait:** ~2-3 minutes for build to complete
3. **Get URL:** Netlify provides a random URL like `random-name-123.netlify.app`

---

### Step 7: Update Backend CORS

**CRITICAL:** Your backend needs to allow requests from Netlify!

In your backend hosting (Render/Railway), update environment variables:

```bash
CORS_ORIGINS=https://your-site.netlify.app
ALLOWED_ORIGINS=https://your-site.netlify.app
```

**After updating, restart backend service!**

---

### Step 8: Verify Deployment

Test these:

1. **Frontend loads:** Visit your Netlify URL
2. **Homepage works:** Should see schedule, features, etc.
3. **API calls work:** Check browser console (F12) for errors
4. **No CORS errors:** If you see CORS errors, check Step 7

**Common test URLs:**
```
https://your-site.netlify.app/
https://your-site.netlify.app/admin
https://your-site.netlify.app/member/login
```

---

## 🎨 OPTIONAL: Custom Domain

### Add Your Own Domain

1. **Buy domain:** (e.g., from Namecheap, GoDaddy)
2. **In Netlify:** Site Settings → Domain Management → Add custom domain
3. **Follow DNS instructions:** Netlify provides nameservers or CNAME records
4. **Wait:** 24-48 hours for DNS propagation
5. **SSL:** Netlify automatically provisions SSL certificate (free!)

**Example DNS Setup (Namecheap):**
```
Type: CNAME
Host: www
Value: your-site.netlify.app
```

---

## 🔧 TROUBLESHOOTING

### Issue 1: Build Fails - "Command not found: yarn"
**Solution:** Netlify should detect yarn automatically, but if not:
- In Build settings, change to: `npm install && npm run build`

### Issue 2: Blank White Page
**Solutions:**
1. Check browser console for errors (F12)
2. Verify `REACT_APP_BACKEND_URL` is set in Netlify env vars
3. Check Network tab - are API calls failing?

### Issue 3: API Calls Return 404
**Solutions:**
1. Verify backend is running (visit backend URL directly)
2. Check `netlify.toml` has correct backend URL
3. Check `_redirects` file has correct backend URL

### Issue 4: CORS Error
**Solutions:**
1. Update backend `CORS_ORIGINS` with Netlify URL
2. Restart backend after env change
3. Clear browser cache and reload

### Issue 5: "Cannot GET /admin" after reload
**Solution:** This is normal! The `netlify.toml` redirects handle this.
- If still failing, check `[[redirects]]` section in netlify.toml

---

## 📊 DEPLOYMENT CHECKLIST

Before going live:

**Backend:**
- [ ] Backend deployed and running
- [ ] Backend URL obtained
- [ ] CORS configured with Netlify URL
- [ ] All environment variables set
- [ ] Database accessible

**Frontend:**
- [ ] Code pushed to GitHub
- [ ] `netlify.toml` updated with backend URL
- [ ] `_redirects` updated with backend URL
- [ ] Netlify env vars set (`REACT_APP_BACKEND_URL`)
- [ ] Build successful on Netlify

**Testing:**
- [ ] Homepage loads
- [ ] Schedule displays correctly
- [ ] Admin login works
- [ ] No console errors
- [ ] API calls working

---

## 🔄 CONTINUOUS DEPLOYMENT

**Auto-Deploy Setup:**

Once connected, every Git push triggers auto-deploy:

```bash
# Make changes
git add .
git commit -m "Updated feature X"
git push

# Netlify automatically builds and deploys!
```

**Deploy Previews:**
- Every Pull Request gets preview URL
- Test before merging to main
- Perfect for team collaboration

---

## 💰 COST

**Netlify Free Tier:**
- ✅ 100 GB bandwidth/month
- ✅ 300 build minutes/month
- ✅ Unlimited sites
- ✅ SSL certificates (free)
- ✅ Deploy previews

**When to Upgrade ($19/month Pro):**
- Need >100 GB bandwidth
- Want background functions
- Need team collaboration features

---

## 🆘 STILL STUCK?

**Check Logs:**
1. Netlify Dashboard → Deploys → Click failed deploy → "View log"
2. Look for error messages
3. Common errors are usually env vars or build command issues

**Test Backend Separately:**
```bash
# Test backend is responding
curl https://your-backend.onrender.com/api/schedule

# Should return JSON schedule data
```

**Test Frontend Build Locally:**
```bash
cd frontend
yarn build
npx serve -s build

# Open http://localhost:3000
```

---

## 📝 QUICK REFERENCE

**Netlify Dashboard URLs:**
- Sites: https://app.netlify.com/sites
- Deploys: https://app.netlify.com/sites/YOUR-SITE/deploys
- Settings: https://app.netlify.com/sites/YOUR-SITE/settings

**Important Files:**
- `/app/frontend/netlify.toml` - Main config
- `/app/frontend/public/_redirects` - Redirect rules
- `/app/frontend/.env.example` - Env var template
- `/app/backend/.env.example` - Backend env template

---

## ✅ NEXT STEPS

1. **Deploy Backend First:**
   - Choose: Render.com, Railway.app, or use Emergent deployment
   - Get the backend URL

2. **Update Configs:**
   - Update `netlify.toml` line 29
   - Update `_redirects` line 5
   - Commit changes

3. **Push to GitHub:**
   - Use "Save to GitHub" in Emergent, OR
   - Manual git push

4. **Connect Netlify:**
   - Import from GitHub
   - Set base directory: `frontend`
   - Add env vars
   - Deploy!

5. **Update Backend CORS:**
   - Add Netlify URL to CORS_ORIGINS
   - Restart backend

6. **Test Everything:**
   - Visit Netlify URL
   - Check all pages
   - Verify API calls work

---

**Ready to deploy?** Follow steps above and you'll be live in minutes! 🚀
