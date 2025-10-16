"""
Simple Chatbot Test - Direct API Testing
"""
import requests
import json
import time
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CHATBOT_URL = "http://localhost:8000"

print("="*80)
print("SIMPLE CHATBOT TEST")
print("="*80)

# Test 1: Health check
print("\n1. Health Check...")
try:
    response = requests.get(f"{CHATBOT_URL}/health", timeout=5)
    print(f"✅ Chatbot is running: {response.json()}")
except Exception as e:
    print(f"❌ Chatbot not responding: {e}")
    exit(1)

# Test 2: Create session
print("\n2. Creating Session...")
try:
    response = requests.post(
        f"{CHATBOT_URL}/api/v1/chatbot/session",
        json={
            "user_id": "test_user_123",
            "template_id": "flirty-romantic"
        },
        timeout=10
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get("success"):
        session_id = result["session_id"]
        print(f"\n✅ Session created: {session_id}")
        
        # Wait a moment
        print("\n⏳ Waiting 2 seconds...")
        time.sleep(2)
        
        # Test 3: Send message
        print("\n3. Sending Message...")
        response = requests.post(
            f"{CHATBOT_URL}/api/v1/chatbot/session/{session_id}/message",
            json={"message": "Hey! How are you?"},
            timeout=15
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get("success"):
            print(f"\n✅ AI Response: {result['response']}")
            print(f"📊 Message Count: {result.get('message_count')}")
            if result.get('debug_info'):
                print(f"🐛 Debug: {result['debug_info']}")
        else:
            print(f"\n❌ Message failed: {result.get('error')}")
    else:
        print(f"\n❌ Session creation failed: {result.get('error')}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("TEST COMPLETED")
print("="*80)

