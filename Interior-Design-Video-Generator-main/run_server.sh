#!/bin/bash

# Interior Design API - Server Startup Script

echo "=================================="
echo "Interior Design API Server"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check CUDA availability
echo ""
echo "🖥️  Checking GPU availability..."
python3 -c "import torch; print(f'GPU Available: {torch.cuda.is_available()}'); print(f'GPU Name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"No GPU\"}')"

echo ""
echo "=================================="
echo "🚀 Starting API Server..."
echo "=================================="
echo ""
echo "📍 Server will run on: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
echo ""
echo "Press CTRL+C to stop the server"
echo "=================================="
echo ""

# Start server
python3 main.py
