#!/bin/bash

echo "🚀 Starting TalentFitAI Backend Server..."
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate  # Linux/Mac"
    echo "   venv\\Scripts\\activate     # Windows"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ Dependencies not installed. Installing..."
    pip install -r requirements.txt
fi

echo "🔧 Starting FastAPI server..."
echo "📚 API Documentation: http://localhost:9142/docs"
echo "🔍 Alternative Docs: http://localhost:9142/redoc"
echo "❤️  Health Check: http://localhost:9142/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 9142
