#!/bin/bash
# Quick start script for local development

echo "======================================"
echo "RAG Production System - Local Setup"
echo "======================================"

cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3.10+ not found${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 18+ not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python and Node.js found${NC}"

# Frontend setup
echo -e "${YELLOW}Setting up Frontend...${NC}"
cd frontend
npm install
cp .env.local.example .env.local
echo -e "${GREEN}✓ Frontend setup complete${NC}"
echo "  Edit frontend/.env.local with Google OAuth credentials"

# API Backend setup
echo -e "${YELLOW}Setting up API Backend...${NC}"
cd ../api-backend
python3 -m venv venv
source venv/bin/activate 2>/dev/null || venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
echo -e "${GREEN}✓ API Backend setup complete${NC}"
echo "  Edit api-backend/.env with Pinecone credentials"

# Inference Backend setup
echo -e "${YELLOW}Setting up Inference Backend...${NC}"
cd ../inference-backend
python3 -m venv venv
source venv/bin/activate 2>/dev/null || venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
echo -e "${GREEN}✓ Inference Backend setup complete${NC}"
echo "  Edit inference-backend/.env with GCP credentials"

echo ""
echo -e "${GREEN}======================================"
echo "Setup Complete!"
echo "=====================================${NC}"

echo ""
echo "Next steps:"
echo "1. Edit environment files with your credentials"
echo "2. Run in separate terminals:"
echo ""
echo "   # Terminal 1: Inference"
echo "   cd inference-backend"
echo "   source venv/bin/activate"
echo "   functions-framework --target colpali_query --debug"
echo ""
echo "   # Terminal 2: API"
echo "   cd api-backend"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "   # Terminal 3: Frontend"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open http://localhost:3000"
