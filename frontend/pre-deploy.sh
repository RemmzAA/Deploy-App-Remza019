#!/bin/bash

# REMZA019 Gaming - Pre-Deployment Script
# Run this before deploying to production

echo "🚀 REMZA019 Gaming - Pre-Deployment Check"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Node version
echo -e "\n${YELLOW}📦 Checking Node.js version...${NC}"
node -v
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Node.js installed${NC}"
else
    echo -e "${RED}❌ Node.js not found! Install Node.js 18+${NC}"
    exit 1
fi

# Check Yarn
echo -e "\n${YELLOW}📦 Checking Yarn...${NC}"
yarn -v
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Yarn installed${NC}"
else
    echo -e "${RED}❌ Yarn not found! Run: npm install -g yarn${NC}"
    exit 1
fi

# Check if .env.production exists
echo -e "\n${YELLOW}🔐 Checking environment variables...${NC}"
if [ -f ".env.production" ]; then
    echo -e "${GREEN}✅ .env.production exists${NC}"
    
    # Check if REACT_APP_BACKEND_URL is set
    if grep -q "REACT_APP_BACKEND_URL" .env.production; then
        BACKEND_URL=$(grep "REACT_APP_BACKEND_URL" .env.production | cut -d '=' -f2)
        echo -e "${GREEN}   Backend URL: ${BACKEND_URL}${NC}"
    else
        echo -e "${RED}❌ REACT_APP_BACKEND_URL not set in .env.production${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ .env.production not found!${NC}"
    echo -e "${YELLOW}   Creating from template...${NC}"
    
    if [ -f ".env.production.example" ]; then
        cp .env.production.example .env.production
        echo -e "${YELLOW}⚠️  Please edit .env.production with your backend URL${NC}"
        exit 1
    else
        echo -e "${RED}❌ .env.production.example not found!${NC}"
        exit 1
    fi
fi

# Install dependencies
echo -e "\n${YELLOW}📦 Installing dependencies...${NC}"
yarn install --frozen-lockfile
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

# Run linter (if configured)
echo -e "\n${YELLOW}🔍 Running linter...${NC}"
# yarn lint 2>/dev/null
# if [ $? -eq 0 ]; then
#     echo -e "${GREEN}✅ Linter passed${NC}"
# else
#     echo -e "${YELLOW}⚠️  Linter warnings (non-critical)${NC}"
# fi

# Build for production
echo -e "\n${YELLOW}🏗️  Building for production...${NC}"
yarn build
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build successful${NC}"
    
    # Check build size
    BUILD_SIZE=$(du -sh build | cut -f1)
    echo -e "${GREEN}   Build size: ${BUILD_SIZE}${NC}"
else
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

# Check if netlify.toml exists
echo -e "\n${YELLOW}🌐 Checking Netlify configuration...${NC}"
if [ -f "netlify.toml" ]; then
    echo -e "${GREEN}✅ netlify.toml exists${NC}"
    
    # Check if backend URL is updated
    if grep -q "YOUR_BACKEND_URL" netlify.toml; then
        echo -e "${RED}❌ Please update YOUR_BACKEND_URL in netlify.toml${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ netlify.toml configured${NC}"
    fi
else
    echo -e "${RED}❌ netlify.toml not found!${NC}"
    exit 1
fi

# Check _redirects file
echo -e "\n${YELLOW}🔀 Checking redirects...${NC}"
if [ -f "public/_redirects" ]; then
    echo -e "${GREEN}✅ _redirects file exists${NC}"
    
    if grep -q "YOUR_BACKEND_URL" public/_redirects; then
        echo -e "${RED}❌ Please update YOUR_BACKEND_URL in public/_redirects${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ _redirects configured${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  _redirects file not found (using netlify.toml)${NC}"
fi

# Summary
echo -e "\n${GREEN}=========================================="
echo -e "✅ ALL CHECKS PASSED!"
echo -e "==========================================${NC}"
echo -e "\n${YELLOW}📋 Next Steps:${NC}"
echo -e "1. Push code to GitHub"
echo -e "2. Connect repository to Netlify"
echo -e "3. Deploy!"
echo -e "\n${GREEN}🚀 Ready for deployment!${NC}\n"
