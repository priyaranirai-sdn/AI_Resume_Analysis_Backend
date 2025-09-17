#!/usr/bin/env python3
"""
Startup script for TalentFitAI
This script starts the FastAPI server with proper configuration.
"""

import uvicorn
import os
import sys

def start_server():
    """Start the TalentFitAI FastAPI server"""
    
    print("🚀 Starting TalentFitAI Backend Server...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app/main.py"):
        print("❌ Error: Please run this script from the project root directory")
        print("   Make sure you're in the directory containing the 'app' folder")
        sys.exit(1)
    
    print("📦 Loading application...")
    
    try:
        # Import the app to check for any import errors
        from app.main import app
        print("✅ Application loaded successfully!")
        
        print("\n🔧 Starting server...")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🔍 Alternative Docs: http://localhost:8000/redoc")
        print("❤️  Health Check: http://localhost:8000/health")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start the server
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
