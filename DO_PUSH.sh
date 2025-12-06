#!/bin/bash

# =============================================================================
# BEZBEDAN GITHUB PUSH SCRIPT - 019 Solutions
# =============================================================================

echo "🚀 Priprema bezbednog GitHub push-a..."
echo ""

# Proveri da li smo u /app direktorijumu
if [ ! -d ".git" ]; then
    echo "❌ ERROR: Nisam u Git direktorijumu!"
    exit 1
fi

echo "📝 Korak 1: Dodavanje SAMO bezbednih fajlova..."
echo ""

# Dodaj samo bezbedne frontend fajlove
git add .gitignore
git add frontend/src/components/GamingDemo.css
git add frontend/src/components/GamingDemo.js  
git add frontend/src/components/Logo3D.css
git add frontend/src/components/Logo3D.js

# Dodaj backend izmene (samo requirements)
git add backend/requirements.txt

echo "✅ Fajlovi dodati"
echo ""

echo "🔍 Korak 2: Provera staged fajlova..."
echo ""
git diff --staged --name-only

echo ""
echo "⚠️  Korak 3: Provera da li ima tajni u staged fajlovima..."
echo ""

# Proveri da li ima passworda, api ključeva, secrets
SECRETS=$(git diff --staged | grep -i "password\|secret\|api.*key\|smtp.*pass\|jwt.*secret\|mongo.*url.*://")

if [ ! -z "$SECRETS" ]; then
    echo "🔴 UPOZORENJE: Pronađene tajne u staged fajlovima!"
    echo "$SECRETS"
    echo ""
    echo "❌ PUSH ZAUSTAVLJEN - Uklonite tajne pre push-a!"
    exit 1
else
    echo "✅ Nema tajni - Bezbedno za push!"
fi

echo ""
echo "📦 Korak 4: Kreiranje commit-a..."
echo ""

git commit -m "Fix: Hero section fonts, logo styling, and admin improvements

- Updated hero section with modern gaming fonts (Orbitron, Rajdhani, Exo 2)
- Fixed logo 3D cube styling and visibility
- Improved admin button logic
- Cleaned up .gitignore
- Added emergentintegrations to requirements.txt"

echo ""
echo "✅ Commit kreiran!"
echo ""

echo "🚀 Korak 5: Push na GitHub..."
echo ""

# Pokušaj push
if git push origin main; then
    echo ""
    echo "✅✅✅ USPEŠNO! Kod je push-ovan na GitHub! ✅✅✅"
    echo ""
    echo "🎉 Netlify će automatski deployovati novu verziju za ~5-10 minuta"
    echo ""
else
    echo ""
    echo "❌ Push neuspešan. Moguće da GitHub još uvek detektuje tajne."
    echo ""
    echo "💡 ALTERNATIVA: Koristite Emergent 'Save to GitHub' feature!"
    echo ""
fi
