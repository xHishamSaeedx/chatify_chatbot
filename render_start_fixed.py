#!/usr/bin/env python3
"""
Fixed startup script for Render deployment
This ensures proper port binding and handles all edge cases
"""

import os
import sys

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
    
    # Import here to avoid build-time import errors
    try:
        import uvicorn
        from app.main import app
        
        # Start the server with proper configuration
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            loop="asyncio"
        )
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
