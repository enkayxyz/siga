#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== Siga Backend Deployment Helper ===${NC}"

# Check for npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed. Please install Node.js/npm first.${NC}"
    exit 1
fi

# Install wrangler locally if not present
if ! command -v wrangler &> /dev/null; then
    echo -e "${BLUE}Installing wrangler locally...${NC}"
    npm install wrangler --save-dev
    WRANGLER="npx wrangler"
else
    WRANGLER="wrangler"
fi

# Login check
echo -e "${BLUE}Checking Cloudflare login status...${NC}"
LOGIN_STATUS=$($WRANGLER whoami 2>&1)
if [[ $LOGIN_STATUS == *"not authenticated"* ]] || [[ $? -ne 0 ]]; then
    echo -e "${RED}You are not logged in.${NC}"
    echo -e "Please log in via the browser window that opens..."
    $WRANGLER login
fi

# Prepare requirements.txt for Workers
echo -e "${BLUE}Preparing requirements.txt for Cloudflare...${NC}"
cd backend
cp requirements.txt requirements.txt.bak
cp requirements-worker.txt requirements.txt

# Deploy
echo -e "${GREEN}Deploying to Cloudflare Workers...${NC}"
DEPLOY_OUTPUT=$($WRANGLER deploy 2>&1)
echo "$DEPLOY_OUTPUT"

# Extract URL
WORKER_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[a-zA-Z0-9.-]*\.workers\.dev')
echo -e "${BLUE}Deployed to: $WORKER_URL${NC}"

# Save URL for Frontend
if [ -n "$WORKER_URL" ]; then
    echo "VITE_API_URL=$WORKER_URL" > ../frontend/.env.production
    echo -e "${BLUE}Saved Backend URL to frontend/.env.production${NC}"
fi

# Restore requirements.txt
mv requirements.txt.bak requirements.txt
cd ..

# Set Secrets from .env
echo -e "${BLUE}Setting secrets from backend/.env...${NC}"
if [ -f "backend/.env" ]; then
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ $key =~ ^#.*$ ]] && continue
        [[ -z $key ]] && continue
        
        # Only set specific API keys
        if [[ $key == *"API_KEY"* ]]; then
            # Remove quotes if present
            value=$(echo "$value" | tr -d '"' | tr -d "'")
            echo -e "Setting $key..."
            echo "$value" | $WRANGLER secret put "$key" --cwd backend > /dev/null
        fi
    done < "backend/.env"
else
    echo -e "${RED}Warning: backend/.env not found. Secrets not set.${NC}"
fi

# Verify Deployment
echo -e "${BLUE}Verifying deployment...${NC}"
if [ -n "$WORKER_URL" ]; then
    echo "Waiting for propagation (5s)..."
    sleep 5
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$WORKER_URL/")
    if [ "$HTTP_STATUS" == "200" ]; then
        echo -e "${GREEN}Success! Backend is reachable at $WORKER_URL${NC}"
    else
        echo -e "${RED}Warning: Backend returned status $HTTP_STATUS at $WORKER_URL${NC}"
    fi
else
    echo -e "${RED}Could not determine Worker URL to verify.${NC}"
fi

echo -e "${GREEN}Deployment process finished!${NC}"
