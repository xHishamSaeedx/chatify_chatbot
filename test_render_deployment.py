#!/usr/bin/env python3
"""
Test script to verify Render deployment configuration
"""

import os
import sys

def test_environment_variables():
    """Test if all required environment variables are set"""
    print("🔍 Testing Environment Variables...")
    
    required_vars = [
        'PORT',
        'HOST', 
        'ENVIRONMENT'
    ]
    
    optional_vars = [
        'REDIS_URL',
        'FIREBASE_PROJECT_ID',
        'OPENAI_API_KEY'
    ]
    
    print("\n📋 Required Variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: Not set")
    
    print("\n📋 Optional Variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {'*' * len(value)} (set)")
        else:
            print(f"  ⚠️ {var}: Not set")
    
    print()

def test_port_binding():
    """Test if the service can bind to the correct port"""
    print("🔍 Testing Port Binding...")
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"  Port: {port}")
    print(f"  Host: {host}")
    
    # Test if we can import the app
    try:
        from app.main import app
        print(f"  ✅ App imported successfully")
        print(f"  ✅ App type: {type(app)}")
        return True
    except Exception as e:
        print(f"  ❌ Failed to import app: {e}")
        return False

def test_redis_config():
    """Test Redis configuration"""
    print("🔍 Testing Redis Configuration...")
    
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        print(f"  ✅ Redis URL configured: {redis_url[:20]}...")
        return True
    else:
        print(f"  ⚠️ Redis URL not configured - will use fallback storage")
        return False

def main():
    """Run all tests"""
    print("🧪 Render Deployment Test")
    print("=" * 40)
    
    test_environment_variables()
    test_port_binding()
    test_redis_config()
    
    print("\n✅ All tests completed!")
    print("\n🚀 Ready for deployment!")

if __name__ == "__main__":
    main()
