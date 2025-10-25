#!/usr/bin/env python3
"""
Render-specific startup script for Chatify Chatbot
This ensures proper port binding for Render deployment
"""

import os
import uvicorn
from app.main import app

def main():
    """Start the application with proper port binding for Render"""
    # Get port from environment variable (Render sets this)
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Chatify Chatbot on {host}:{port}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    
    # Start the server with proper configuration
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
