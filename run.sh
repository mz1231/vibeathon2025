#!/bin/bash

# Vibe Check - Run Script
# This script starts both the backend API and frontend dev server

echo "================================"
echo "    Vibe Check - Starting Up    "
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
    exit 1
fi

# Check for Node
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is required but not installed.${NC}"
    exit 1
fi

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip3 install -r requirements.txt --quiet

# Install Node dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing Node dependencies...${NC}"
    npm install
fi

# Create databases directory
mkdir -p databases

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}Warning: OPENAI_API_KEY not set. Conversations will use fallback mode.${NC}"
    echo "Set it with: export OPENAI_API_KEY='your-key-here'"
    echo ""
fi

# Start the backend API server
echo -e "${GREEN}Starting backend API server on http://localhost:8000...${NC}"
python3 api/main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

# Start the frontend dev server
echo -e "${GREEN}Starting frontend on http://localhost:3000...${NC}"
npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}   Servers are running!         ${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
