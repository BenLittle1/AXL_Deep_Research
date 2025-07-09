#!/usr/bin/env python3
"""
Startup script for Railway deployment
Ensures proper Python path and starts the FastAPI application
"""
import sys
import os

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 