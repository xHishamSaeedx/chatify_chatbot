#!/usr/bin/env python3
"""
Simple test script to verify the Chatify Chatbot API is working
"""

import requests
import json
import time

def test_api():
    base_url = "http://localhost:8000"
    
    print("Testing Chatify Chatbot API...")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("Health check passed")
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Health check failed: {e}")
        return False
    
    # Test 2: AI Fallback stats
    print("\n2. Testing AI fallback stats...")
    try:
        response = requests.get(f"{base_url}/api/v1/ai-fallback/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print("AI fallback stats retrieved")
            print(f"   Timeout: {stats.get('fallback_service', {}).get('matching_timeout', 'N/A')} seconds")
            print(f"   Active sessions: {stats.get('fallback_service', {}).get('active_sessions', 0)}")
        else:
            print(f"AI fallback stats failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"AI fallback stats failed: {e}")
    
    # Test 3: Set matching state
    print("\n3. Testing set matching state...")
    try:
        test_user_id = "test_user_123"
        payload = {
            "user_id": test_user_id,
            "preferences": {
                "gender": "any",
                "interests": ["chatting", "meeting new people"]
            }
        }
        response = requests.post(
            f"{base_url}/api/v1/ai-fallback/set-matching-state",
            json=payload,
            timeout=5
        )
        if response.status_code == 200:
            print("Matching state set successfully")
        else:
            print(f"Set matching state failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Set matching state failed: {e}")
    
    # Test 4: Check AI fallback (should trigger after timeout)
    print("\n4. Testing AI fallback check...")
    try:
        payload = {"user_id": test_user_id}
        response = requests.post(
            f"{base_url}/api/v1/ai-fallback/check-ai-fallback",
            json=payload,
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            print("AI fallback check completed")
            print(f"   Success: {result.get('success', False)}")
            print(f"   AI Match: {result.get('is_ai_match', False)}")
            if result.get('is_ai_match'):
                print("AI fallback triggered successfully!")
        else:
            print(f"AI fallback check failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"AI fallback check failed: {e}")
    
    print("\nAPI testing completed!")
    return True

if __name__ == "__main__":
    test_api()
