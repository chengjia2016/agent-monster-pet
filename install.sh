#!/bin/bash
# Agent Monster - Optimized Installation Script
# This script ensures a clean environment and sets up the server-authoritative mode.

set -e

# ANSI Color Codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Agent Monster - Professional Setup${NC}"
echo -e "${BLUE}====================================${NC}"

# 1. Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not found.${NC}"
    exit 1
fi

# 2. Setup Virtual Environment
echo -e "${YELLOW}Step 1: Setting up virtual environment...${NC}"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Try to install venv if missing (Ubuntu/Debian)
    if ! python3 -m venv .venv &> /dev/null; then
        echo -e "${YELLOW}Note: python3-venv might be missing. Attempting to proceed or providing instructions...${NC}"
        # If we are root, we could try to install, but better to just guide
        echo -e "${RED}Please run: sudo apt-get update && sudo apt-get install -y python3-venv${NC}"
        # We continue anyway in case it's just a permission issue or already partially there
    fi
fi

python3 -m venv .venv || { echo -e "${RED}Failed to create venv.${NC}"; exit 1; }
source .venv/bin/activate

# 3. Install/Upgrade Pip and Requirements
echo -e "${YELLOW}Step 2: Installing dependencies...${NC}"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# 4. Check GitHub CLI (Mandatory for Online Mode)
echo -e "${YELLOW}Step 3: Verifying GitHub CLI (gh)...${NC}"
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Warning: GitHub CLI (gh) not found.${NC}"
    echo -e "Agent Monster requires 'gh' for authentication."
    echo -e "Please install it: https://cli.github.com/"
else
    echo -e "${GREEN}✓ GitHub CLI detected.${NC}"
    if ! gh auth status &> /dev/null; then
        echo -e "${YELLOW}Action Required: Please run 'gh auth login' to authenticate.${NC}"
    else
        echo -e "${GREEN}✓ GitHub Authenticated.${NC}"
    fi
fi

# 5. Clean up local test data
echo -e "${YELLOW}Step 4: Preparing clean workspace...${NC}"
rm -rf .monster/users/*.json .monster/accounts/*.json .monster/inventory/*.json .monster/pets/*.json .monster/eggs/owner_eggs/*.json 2>/dev/null || true

echo -e "${BLUE}====================================${NC}"
echo -e "${GREEN}Installation Successful!${NC}"
echo -e ""
echo -e "${BLUE}How to start the game:${NC}"
echo -e "1. ${YELLOW}Natural Language (Recommended):${NC}"
echo -e "   Just talk to your AI agent (Gemini, Claude, OpenCode) and say:"
echo -e "   \"我想玩代码怪兽\" or \"I want to play Agent Monster\""
echo -e ""
echo -e "2. ${YELLOW}Manual Command:${NC}"
echo -e "   python3 mcp_server.py mcp (For Agent integration)"
echo -e ""
echo -e "${YELLOW}Note:${NC} All game logic is now handled by the ${BLUE}Multiplayer Judge Server${NC}."
echo -e "No local initialization is required. The AI will guide you through registration!"
echo -e "${BLUE}====================================${NC}"
