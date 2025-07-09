#!/usr/bin/env python3
"""
Minimal test app for Railway deployment debugging
"""
import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Test app working!", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy", "test": "basic"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 