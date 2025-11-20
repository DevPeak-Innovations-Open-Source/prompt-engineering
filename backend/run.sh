#!/bin/bash
# Quick start script for mini_n8n

echo "🚀 Starting mini_n8n..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Please create one based on .env.example"
    echo "You can copy .env.example to .env and update the values"
fi

# Run the application
echo "✨ Starting FastAPI application..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

