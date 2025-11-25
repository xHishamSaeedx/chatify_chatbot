"""
Simple queue test with consistent user ID
"""

import asyncio
import aiohttp
import json
from datetime import datetime


BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"


async def test_simple():
    """Simple test"""
    test_user_id = "test_user_12345"  # Fixed user ID
    socket_id = "test_socket_12345"
    headers = {"Authorization": "Bearer test_token"}
    
    print("="*80)
    print("SIMPLE QUEUE TEST")
    print("="*80)
    print(f"User ID: {test_user_id}")
    print(f"Socket ID: {socket_id}")
    print()
    
    async with aiohttp.ClientSession() as session:
        # Join
        print("[1] Joining queue...")
        payload = {"userId": test_user_id, "socketId": socket_id}
        async with session.post(f"{API_URL}/queue/join", json=payload, headers=headers) as r:
            result = await r.json()
            print(f"    Join result: {result.get('success')}")
            if result.get("data", {}).get("success"):
                print(f"    Position: {result.get('data', {}).get('position')}")
        print()
        
        # Check status every second for 18 seconds
        print("[2] Monitoring (checking every 1s for 18s)...")
        for i in range(18):
            await asyncio.sleep(1)
            
            async with session.get(f"{API_URL}/queue/status?userId={test_user_id}", headers=headers) as r:
                if r.status == 200:
                    status = await r.json()
                    data = status.get("data", {})
                    
                    if data.get("success"):
                        state = data.get("state")
                        wait = data.get("wait_time_seconds", 0)
                        pos = data.get("position")
                        ai_ex = data.get("ai_chat_exchanges", 0)
                        sess_id = data.get("session_id")
                        
                        print(f"    [{i+1}s] State: {state:10s} | Wait: {wait:5.1f}s | Pos: {pos} | AI Ex: {ai_ex} | Session: {sess_id[:20] if sess_id else 'None'}")
                        
                        if state == "ai_chat" and sess_id:
                            print()
                            print("[3] AI chat started! Sending message...")
                            
                            # Try to send message via chatbot endpoint
                            # First, we need to get the chatbot session ID from the AI fallback
                            # The session_id in queue is the AI session, we need the chatbot session
                            
                            # Check if there's a chatbot endpoint that accepts the AI session
                            msg_payload = {
                                "message": "Hello! How are you?",
                                "system_prompt": None
                            }
                            
                            async with session.post(f"{API_URL}/chat/simple", json=msg_payload) as msg_r:
                                if msg_r.status == 200:
                                    msg_result = await msg_r.json()
                                    if msg_result.get("success"):
                                        print(f"    ✓ AI Response: {msg_result.get('content', 'No content')[:100]}")
                                    else:
                                        print(f"    ✗ AI Error: {msg_result.get('error')}")
                                else:
                                    print(f"    ✗ HTTP Error: {msg_r.status}")
                            
                            break
                    else:
                        print(f"    [{i+1}s] User not in queue: {data.get('error')}")
                        break
        
        print()
        print("[4] Final check...")
        async with session.get(f"{API_URL}/queue/active-count") as r:
            count_data = await r.json()
            print(f"    Active count: {count_data.get('data', {}).get('active_count', 0)}")
            print(f"    Queue size: {count_data.get('data', {}).get('stats', {}).get('queue_size', 0)}")
        
        print()
        print("="*80)


if __name__ == "__main__":
    asyncio.run(test_simple())

