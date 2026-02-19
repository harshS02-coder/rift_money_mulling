#!/bin/bash

# RIFT 2026 - Money Muling Detection Engine
# Script to start both backend and frontend

echo "🚀 Starting RIFT 2026 Money Muling Detection Engine..."
echo ""

# Check if we're in the right directory
if [ ! -f "run.sh" ]; then
    echo "❌ Error: Script must be run from the project root directory"
    exit 1
fi

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Start Backend
echo -e "${BLUE}📦 Starting Backend (FastAPI)...${NC}"
cd backend

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
fi

# Start FastAPI server in background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
echo "   📍 Available at: http://localhost:8000"
echo "   📚 API docs at: http://localhost:8000/docs"
echo ""

# Wait a bit for backend to start
sleep 3

# Start Frontend
echo -e "${BLUE}⚛️  Starting Frontend (React + Vite)...${NC}"
cd ../frontend

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+"
    kill $BACKEND_PID
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install --silent
fi

# Start Vite dev server in background
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
echo "   📍 Available at: http://localhost:5173"
echo ""

# Display summary
echo -e "${YELLOW}===========================================${NC}"
echo -e "${GREEN}✨ RIFT 2026 is now running!${NC}"
echo -e "${YELLOW}===========================================${NC}"
echo ""
echo "🌐 Frontend:  http://localhost:5173"
echo "🔧 Backend:   http://localhost:8000"
echo "📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Handle cleanup
trap cleanup INT TERM
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ Services stopped${NC}"
    exit 0
}

# Keep the script running
wait
