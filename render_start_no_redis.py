#!/usr/bin/env python3
"""
Startup script for Render deployment without Redis dependency
This will work even if Redis is not configured
"""

import os
import sys
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
    
    # Print all environment variables for debugging
    print(f"Environment variables:")
    print(f"  PORT: {os.getenv('PORT')}")
    print(f"  HOST: {os.getenv('HOST')}")
    print(f"  ENVIRONMENT: {os.getenv('ENVIRONMENT')}")
    print(f"  REDIS_URL: {'Set' if os.getenv('REDIS_URL') else 'Not set'}")
    
    # Start the server with proper configuration
    try:
        print(f"Starting server on {host}:{port}...")
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            loop="asyncio"
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

