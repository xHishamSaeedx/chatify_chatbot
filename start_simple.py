#!/usr/bin/env python3
"""
Simple startup script for Chatify Chatbot Service
This version works without Redis for basic testing
"""

import os
import sys
import uvicorn
from app.main import app

# Set environment variables for basic operation
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault("AI_FALLBACK_TIMEOUT", "10")
os.environ.setdefault("AI_FALLBACK_ENABLED", "true")
os.environ.setdefault("LOG_LEVEL", "INFO")

def main():
    print("🚀 Starting Chatify Chatbot Service (Simple Mode)")
    print("📍 Service will be available at: http://localhost:8000")
    print("🤖 AI Fallback API: http://localhost:8000/api/v1/ai-fallback/")
    print("📊 Health check: http://localhost:8000/api/v1/health")
    print("⚠️  Note: This is a simplified version without Redis")
    print("   For full functionality, use Docker setup with Redis")
    print()
    
    try:
        # Start the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

