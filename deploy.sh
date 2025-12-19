#!/bin/bash

# ML Hackathon Platform - Backend Deployment Script for Intel Server
# This script helps deploy the backend to your Intel server

set -e

echo "============================================================"
echo "ML Hackathon Platform - Backend Deployment"
echo "============================================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create .env file with Firebase credentials"
    echo "Run: ./setup_env.sh"
    exit 1
fi

echo -e "${GREEN}✓${NC} .env file found"

# Check if venv exists
if [ ! -d venv ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

echo -e "${GREEN}✓${NC} Virtual environment ready"

# Activate venv and install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

echo -e "${GREEN}✓${NC} Dependencies installed"

# Check if running on server or local
if [ "$1" == "production" ]; then
    echo -e "${YELLOW}Starting in production mode...${NC}"
    echo ""
    echo "To run as a service, create systemd service file:"
    echo "sudo nano /etc/systemd/system/ml-hackathon.service"
    echo ""
    echo "For now, starting with uvicorn..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
else
    echo -e "${YELLOW}Starting in development mode...${NC}"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi
