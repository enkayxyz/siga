#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== Siga Frontend Deployment Helper ===${NC}"

# Check for npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed.${NC}"
    exit 1
fi

cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}Installing frontend dependencies...${NC}"
    npm install
fi

# Check for Backend URL
if [ -f ".env.production" ]; then
    source .env.production
fi

if [ -z "$VITE_API_URL" ]; then
    echo -e "${RED}Backend URL not found.${NC}"
    echo -n "Please enter your deployed Backend URL (e.g., https://siga-backend.xyz.workers.dev): "
    read VITE_API_URL
fi

echo -e "${BLUE}Using Backend URL: $VITE_API_URL${NC}"

# Build
echo -e "${BLUE}Building Frontend...${NC}"
# We explicitly pass the env var to the build command
VITE_API_URL=$VITE_API_URL npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}Build failed.${NC}"
    exit 1
fi

# Deploy to Cloudflare Pages
echo -e "${GREEN}Deploying to Cloudflare Pages...${NC}"
# Use npx to ensure we have the tool
npx wrangler pages deploy dist --project-name siga-frontend

echo -e "${GREEN}Frontend Deployment Complete!${NC}"
cd ..
