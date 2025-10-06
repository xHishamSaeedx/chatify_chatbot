#!/usr/bin/env python3
"""
Test script for personality creation
"""

import requests
import json

def test_personality_creation():
    """Test creating a personality"""
    url = "http://localhost:8000/api/v1/personalities/"
    
    personality_data = {
        "name": "test-personality",
        "title": "Test Personality",
        "description": "A test personality",
        "category": "general",
        "personalityPrompt": "You are a test personality",
        "welcomeMessage": "Hello! How can I help you?",
        "model": "gpt-4o-mini",
        "temperature": 0.9,
        "maxTokens": 150,
        "tags": ["test"],
        "isPublic": True,
        "isDefault": False
    }
    
    try:
        response = requests.post(url, json=personality_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Personality created successfully!")
            return True
        else:
            print("❌ Failed to create personality")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_personalities():
    """Test getting all personalities"""
    url = "http://localhost:8000/api/v1/personalities/"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Got personalities successfully!")
            return True
        else:
            print("❌ Failed to get personalities")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Personality API...")
    print()
    
    print("1. Testing GET personalities...")
    test_get_personalities()
    print()
    
    print("2. Testing POST personality creation...")
    test_personality_creation()
    print()
    
    print("3. Testing GET personalities again...")
    test_get_personalities()
