#!/bin/bash
# Helper script to run Vouch application locally

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default port
PORT=${1:-8000}

echo -e "${GREEN}Starting Vouch Application${NC}"
echo "================================"

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}Warning: Virtual environment not activated${NC}"
    if [ -d "venv" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    else
        echo -e "${RED}Error: venv directory not found${NC}"
        echo "Please create it with: python -m venv venv"
        exit 1
    fi
fi

# Check if port is in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}Port $PORT is already in use${NC}"
    PID=$(lsof -ti :$PORT)
    echo "Process using port: $PID"
    read -p "Kill process and continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Killing process $PID..."
        kill -9 $PID 2>/dev/null || true
        sleep 1
    else
        echo "Please use a different port: ./run.sh 8080"
        exit 1
    fi
fi

# Check if required services are running
echo ""
echo "Checking services..."

# MongoDB
if ! nc -z localhost 27017 2>/dev/null; then
    echo -e "${YELLOW}⚠ MongoDB not detected on port 27017${NC}"
    echo "  Start with: brew services start mongodb-community"
fi

# Elasticsearch
if ! curl -s http://localhost:9200 >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Elasticsearch not detected on port 9200${NC}"
    echo "  Start with: brew services start elasticsearch"
fi

# Ollama
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Ollama not detected on port 11434${NC}"
    echo "  Start with: ollama serve"
fi

echo ""
echo -e "${GREEN}Starting application on port $PORT...${NC}"
echo "Access at: http://localhost:$PORT"
echo "API docs at: http://localhost:$PORT/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the application
uvicorn app.main:app --reload --host 0.0.0.0 --port $PORT
