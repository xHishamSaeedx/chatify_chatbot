#!/usr/bin/env python3
"""
Test script to verify port binding works correctly
"""

import os
import sys
import socket
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
    
    # Test if port is available
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            print(f"✅ Port {port} is available for binding")
    except OSError as e:
        print(f"❌ Port {port} is not available: {e}")
        return False
    
    # Test if we can import the app
    try:
        print(f"✅ App imported successfully")
        print(f"✅ App type: {type(app)}")
        return True
    except Exception as e:
        print(f"❌ Failed to import app: {e}")
        return False

if __name__ == "__main__":
    success = test_port_binding()
    sys.exit(0 if success else 1)
