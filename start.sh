#!/bin/bash

# whAtIs.sh API Startup Script

echo "Starting whAtIs.sh API..."

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found. Please run this script from the /api directory."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set default environment variables if not set
export LLM_BASE_URL=${LLM_BASE_URL:-"http://localhost:11434"}
export LLM_MODEL=${LLM_MODEL:-"whatis.sh"}

echo "Environment variables:"
echo "  LLM_BASE_URL: $LLM_BASE_URL"
echo "  LLM_MODEL: $LLM_MODEL"

# Start the API
echo "Starting FastAPI server on http://localhost:8000"
echo "Available endpoints:"
echo "  - GET /health (health check)"
echo "  - GET /{command} (headless, e.g., /ls, /grep)"
echo "  - GET / (with JSON body)"
echo "  - POST / (with JSON body)"
echo ""
echo "Press Ctrl+C to stop the server"

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
