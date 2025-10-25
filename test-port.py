#!/usr/bin/env python3
"""
Simple port test script to verify the service can bind to the correct port
"""

import os
import sys
from app.main import app

def test_port_binding():
    """Test if the service can bind to the correct port"""
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Testing port binding on {host}:{port}")
    print(f"Environment variables:")
    print(f"  PORT: {os.getenv('PORT', 'Not set')}")
    print(f"  HOST: {os.getenv('HOST', 'Not set')}")
    print(f"  ENVIRONMENT: {os.getenv('ENVIRONMENT', 'Not set')}")
    
    try:
        import uvicorn
        print(f"Starting server on {host}:{port}")
        uvicorn.run(app, host=host, port=port, log_level="info")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_port_binding()
