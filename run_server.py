#!/usr/bin/env python3
"""
Server startup script for Truth Finder AI
This script properly sets up the Python path and starts the FastAPI server
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Now we can import our app
from app.main import app

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Truth Finder AI Server...")
    print(f"📁 Working directory: {current_dir}")
    print(f"🐍 Python path: {sys.path[0]}")
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(current_dir / "app")]
    ) 