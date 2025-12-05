# 🚀 STELLAR HOSTING - DEPLOYMENT GUIDE

## 🌐 SERVER DETAILS:
```
Server IP: 67.223.118.177
Primary Domain: 019solutions.shop  
New Domain: 019solutions.com
Home Directory: /home/lhuqpack
cPanel User: lhuqpack
```

## 📋 STEP-BY-STEP DEPLOYMENT:

### STEP 1: DNS CONFIGURATION (Namecheap)
Go to Namecheap → Domain List → 019solutions.com → Advanced DNS:

**DELETE:**
- CNAME Record: www → parkingpage.namecheap.com
- URL Redirect Record: @ → http://www.019solutions.com/

**ADD:**
- A Record: @ → 67.223.118.177 (TTL: Automatic)
- A Record: www → 67.223.118.177 (TTL: Automatic)

### STEP 2: ADD DOMAIN IN CPANEL
1. Login to cPanel
2. Find "Addon Domains" or "Subdomains" 
3. Add New Domain: `019solutions.com`
4. Document Root: `/public_html/019solutions` 
5. Create subdomain: Will be created automatically

### STEP 3: UPLOAD WEBSITE FILES
Using File Manager in cPanel:
1. Navigate to `/public_html/019solutions/` 
2. Upload all files from your website build
3. Extract if uploaded as ZIP

### STEP 4: CREATE .HTACCESS FOR REACT
Create `.htaccess` file in `/public_html/019solutions/`:
```apache
Options -MultiViews
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^ index.html [QSA,L]
```

### STEP 5: SSL CERTIFICATE
1. In cPanel find "SSL/TLS"
2. Select "Let's Encrypt SSL" 
3. Add certificate for 019solutions.com and www.019solutions.com

## 📁 FILE STRUCTURE AFTER UPLOAD:
```
/home/lhuqpack/public_html/019solutions/
├── index.html
├── static/
│   ├── css/
│   └── js/
├── .htaccess
└── other files...
```

## ✅ VERIFICATION CHECKLIST:
- [ ] DNS A Records configured (67.223.118.177)
- [ ] Addon domain created in cPanel
- [ ] Website files uploaded
- [ ] .htaccess file created for React routing
- [ ] SSL certificate installed
- [ ] Test: http://019solutions.com loads website
- [ ] Test: https://019solutions.com (SSL working)
- [ ] Test: www.019solutions.com redirects properly

## 🔧 TROUBLESHOOTING:
- DNS propagation: 24-48 hours max
- If site doesn't load: Check file permissions (755 for folders, 644 for files)  
- SSL issues: Try "Force HTTPS Redirect" in cPanel

---
© 2025 019 Solutions - Deployment Ready!