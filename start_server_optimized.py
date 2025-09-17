#!/usr/bin/env python3
"""
Optimized server startup script with better error handling and logging
"""

import uvicorn
import logging
import sys
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('server.log')
    ]
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        import fastapi
        import uvicorn
        import transformers
        import torch
        import sqlalchemy
        logger.info("✅ All core dependencies are available")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        return False

def check_database():
    """Check if database file exists and is accessible"""
    db_path = Path("talentfitai.db")
    if db_path.exists():
        logger.info("✅ Database file found")
        return True
    else:
        logger.warning("⚠️  Database file not found, will be created on first run")
        return True

def start_server():
    """Start the FastAPI server with optimized settings"""
    logger.info("🚀 Starting TalentFitAI Backend Server")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("❌ Dependency check failed. Please install requirements.")
        sys.exit(1)
    
    # Check database
    check_database()
    
    try:
        # Configure uvicorn with optimized settings
        config = uvicorn.Config(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True,
            # Optimize for better performance
            workers=1,  # Single worker for development
            loop="asyncio",
            http="httptools" if sys.platform != "win32" else "h11",  # Use httptools on non-Windows
        )
        
        server = uvicorn.Server(config)
        logger.info("🌐 Server starting on http://0.0.0.0:8000")
        logger.info("📚 API Documentation available at http://0.0.0.0:8000/docs")
        logger.info("🔍 AI Health Check available at http://0.0.0.0:8000/job-post/health/ai")
        
        server.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
