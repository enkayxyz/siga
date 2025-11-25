#!/bin/bash

# Siga Management Script

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PID_FILE=".siga_pids"
ENV_FILE="backend/.env"

function print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}       Siga Agent Management CLI        ${NC}"
    echo -e "${BLUE}========================================${NC}"
}

function check_conda() {
    if ! command -v conda &> /dev/null; then
        echo -e "${RED}Error: Conda is not installed or not in PATH.${NC}"
        exit 1
    fi
}

function start_app() {
    echo -e "${GREEN}Starting Siga App...${NC}"
    
    # Check if already running
    if [ -f "$PID_FILE" ]; then
        echo -e "${RED}App seems to be running (PID file exists). Stop it first.${NC}"
        return
    fi

    # Activate Conda
    # We need to source conda.sh to use 'conda activate' in script
    # Try standard locations
    CONDA_BASE=$(conda info --base)
    source "$CONDA_BASE/etc/profile.d/conda.sh"
    conda activate siga

    # Start Backend
    echo "Starting Backend..."
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend started (PID: $BACKEND_PID)"

    # Start Frontend
    echo "Starting Frontend..."
    cd frontend
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    echo "Frontend started (PID: $FRONTEND_PID)"

    # Save PIDs
    echo "$BACKEND_PID $FRONTEND_PID" > "$PID_FILE"
    
    echo -e "${GREEN}Siga is running!${NC}"
    echo -e "Backend: http://localhost:8000"
    echo -e "Frontend: http://localhost:5173"
    echo -e "Logs are being written to backend.log and frontend.log"
}

function stop_app() {
    echo -e "${RED}Stopping Siga App...${NC}"
    
    if [ ! -f "$PID_FILE" ]; then
        echo "No PID file found. Is the app running?"
        return
    fi

    read BACKEND_PID FRONTEND_PID < "$PID_FILE"
    
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "Stopped Backend ($BACKEND_PID)"
    fi
    
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "Stopped Frontend ($FRONTEND_PID)"
    fi

    rm "$PID_FILE"
    echo -e "${GREEN}App stopped successfully.${NC}"
}

function mask_key() {
    local key=$1
    if [ -z "$key" ]; then
        echo ""
    else
        echo "...${key: -4}"
    fi
}

function setup_ai() {
    # Activate Conda if not already
    CONDA_BASE=$(conda info --base)
    source "$CONDA_BASE/etc/profile.d/conda.sh"
    conda activate siga
    
    python backend/setup_ai.py
    
    echo -e "\nPress Enter to continue..."
    read
}

function verify_ai() {
    echo -e "${BLUE}Verifying AI Connectivity...${NC}"
    
    # Activate Conda if not already
    CONDA_BASE=$(conda info --base)
    source "$CONDA_BASE/etc/profile.d/conda.sh"
    conda activate siga
    
    python backend/verify_ai.py
    
    echo -e "\nPress Enter to continue..."
    read
}

function deploy_app() {
    echo -e "${BLUE}Starting Deployment...${NC}"
    ./deploy_backend.sh
    echo -e "\nPress Enter to continue..."
    read
}

# Main Menu
check_conda

if [ "$1" ]; then
    case "$1" in
        start) start_app ;;
        stop) stop_app ;;
        setup) setup_ai ;;
        verify) verify_ai ;;
        deploy) deploy_app ;;
        *) echo "Usage: $0 {start|stop|setup|verify|deploy}" ;;
    esac
    exit 0
fi

while true; do
    print_header
    echo "1. Start App"
    echo "2. Stop App"
    echo "3. Setup AI"
    echo "4. Verify AI Connectivity"
    echo "5. Deploy Backend (Cloudflare Workers)"
    echo "6. Deploy Frontend (Cloudflare Pages)"
    echo "7. Exit"
    echo -n "Choose an option: "
    read choice

    case $choice in
        1) start_app ;;
        2) stop_app ;;
        3) setup_ai ;;
        4) verify_ai ;;
        5) deploy_app ;;
        6) ./deploy_frontend.sh; echo -e "\nPress Enter..."; read ;;
        7) exit 0 ;;
        *) echo -e "${RED}Invalid option${NC}" ;;
    esac
    echo ""
done
