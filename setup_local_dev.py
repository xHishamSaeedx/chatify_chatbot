#!/usr/bin/env python3
"""
Local Development Setup Script for Chatify Backend
This script helps set up the local development environment
"""

import os
import subprocess
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from env.example if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    # Copy env.example to .env
    with open(env_example, 'r') as src, open(env_file, 'w') as dst:
        dst.write(src.read())
    
    print("✓ Created .env file from env.example")
    print("⚠️  Please update .env file with your actual API keys and Firebase credentials")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_backend():
    """Run the backend server"""
    print("Starting backend server...")
    try:
        subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"], check=True)
    except KeyboardInterrupt:
        print("\n✓ Server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")

def main():
    """Main setup function"""
    print("Setting up Chatify Backend for Local Development")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app").exists() or not Path("requirements.txt").exists():
        print("❌ Please run this script from the chatify_chatbot root directory")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Update .env file with your actual API keys")
    print("2. Run: python setup_local_dev.py --run")
    print("3. Backend will be available at http://127.0.0.1:8000")
    print("4. API documentation at http://127.0.0.1:8000/docs")
    
    # If --run flag is provided, start the server
    if "--run" in sys.argv:
        print("\n🏃 Starting backend server...")
        run_backend()

if __name__ == "__main__":
    main()
