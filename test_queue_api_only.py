"""
Test queue API without Socket.IO
Tests the queue system using only HTTP endpoints
"""

import asyncio
import aiohttp
import json
from datetime import datetime


BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"


async def test_queue_api():
    """Test queue API endpoints"""
    print("="*80)
    print("QUEUE API TEST (No Socket.IO)")
    print("="*80)
    print()
    
    test_user_id = f"test_user_{int(datetime.now().timestamp())}"
    headers = {"Authorization": "Bearer test_token"}
    
    async with aiohttp.ClientSession() as session:
        # 1. Join queue (with dummy socket ID)
        print("[1] Joining queue...")
        socket_id = "test_socket_12345"
        payload = {"userId": test_user_id, "socketId": socket_id}
        
        async with session.post(f"{API_URL}/queue/join", json=payload, headers=headers) as response:
            result = await response.json()
            print(f"    Response: {json.dumps(result, indent=2)}")
            
            if not result.get("success"):
                print("    ✗ Failed to join queue")
                return
        
        print()
        
        # 2. Check status immediately
        print("[2] Checking queue status...")
        async with session.get(f"{API_URL}/queue/status", headers=headers) as response:
            status = await response.json()
            print(f"    Status: {json.dumps(status, indent=2)}")
        print()
        
        # 3. Monitor status for 20 seconds
        print("[3] Monitoring queue status (every 2s for 20s)...")
        print("    Waiting for timeout (15s) and AI chat to start...")
        print()
        
        for i in range(10):
            await asyncio.sleep(2)
            
            async with session.get(f"{API_URL}/queue/status", headers=headers) as response:
                if response.status == 200:
                    status = await response.json()
                    data = status.get("data", {})
                    state = data.get("state", "unknown")
                    wait_time = data.get("wait_time_seconds", 0)
                    position = data.get("position")
                    ai_exchanges = data.get("ai_chat_exchanges", 0)
                    session_id = data.get("session_id")
                    
                    print(f"    [{i*2+2}s] State: {state}, Wait: {wait_time:.1f}s, Position: {position}, AI Exchanges: {ai_exchanges}")
                    
                    if state == "ai_chat":
                        print(f"    ✓ AI chat started! Session: {session_id}")
                        
                        # 4. Send message to AI
                        if session_id:
                            print()
                            print("[4] Sending message to AI chatbot...")
                            
                            # First, get the chatbot session ID from the AI fallback service
                            # We need to check the Redis/fallback service for the actual chatbot session
                            
                            # Try sending via chatbot endpoint
                            chatbot_payload = {
                                "message": "Hello! How are you?",
                                "system_prompt": None
                            }
                            
                            async with session.post(f"{API_URL}/chat/simple", json=chatbot_payload) as msg_response:
                                if msg_response.status == 200:
                                    msg_result = await msg_response.json()
                                    print(f"    ✓ AI Response received!")
                                    print(f"    Response: {json.dumps(msg_result, indent=2)}")
                                else:
                                    error = await msg_response.text()
                                    print(f"    ✗ Error sending message: {msg_response.status} - {error}")
                            
                            # Also try the chatbot send-message endpoint if we have session_id
                            if session_id:
                                send_payload = {
                                    "session_id": session_id,
                                    "message": "Hello! How are you?"
                                }
                                async with session.post(f"{API_URL}/chatbot/send-message", json=send_payload) as send_response:
                                    if send_response.status == 200:
                                        send_result = await send_response.json()
                                        print(f"    ✓ Message sent via chatbot endpoint!")
                                        print(f"    Response: {json.dumps(send_result, indent=2)}")
                                    else:
                                        error = await send_response.text()
                                        print(f"    Note: chatbot endpoint returned {send_response.status}: {error}")
                        
                        break
                    elif state == "unknown" or not data.get("success"):
                        print(f"    ⚠ User not found in queue (might have been removed)")
                        break
        
        print()
        
        # 5. Check active count
        print("[5] Checking active count...")
        async with session.get(f"{API_URL}/queue/active-count") as response:
            if response.status == 200:
                count_data = await response.json()
                print(f"    Active count: {json.dumps(count_data, indent=2)}")
        
        print()
        print("="*80)
        print("TEST COMPLETE")
        print("="*80)


if __name__ == "__main__":
    asyncio.run(test_queue_api())

