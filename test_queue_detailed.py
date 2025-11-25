"""
Detailed test script for queue system
Tests queue status and timeout behavior
"""

import asyncio
import aiohttp
import socketio
import json
from datetime import datetime


BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"
SOCKET_URL = BASE_URL


async def test_queue_detailed():
    """Detailed test of queue system"""
    print("="*80)
    print("DETAILED QUEUE SYSTEM TEST")
    print("="*80)
    print()
    
    # Create Socket.IO client
    sio = socketio.AsyncClient()
    events_received = []
    
    @sio.event
    async def connect():
        print("✓ Socket.IO connected")
        events_received.append("connect")
    
    @sio.event
    async def disconnect():
        print("✓ Socket.IO disconnected")
        events_received.append("disconnect")
    
    @sio.on("*")
    async def catch_all(event, data):
        print(f"  → Event: {event}")
        if data:
            print(f"    Data: {json.dumps(data, indent=4)}")
        events_received.append((event, data))
    
    try:
        # Connect
        print("[1] Connecting to Socket.IO...")
        await sio.connect(SOCKET_URL, wait_timeout=10)
        await asyncio.sleep(2)  # Wait longer for connection to stabilize
        socket_id = sio.sid
        print(f"    Socket ID: {socket_id}")
        
        if not socket_id:
            print("    ✗ Failed to get socket ID!")
            await sio.disconnect()
            return
        
        print()
        
        # Test user
        test_user_id = f"test_user_{int(datetime.now().timestamp())}"
        print(f"[2] Test User ID: {test_user_id}")
        print()
        
        # Join queue
        print("[3] Joining queue...")
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": "Bearer test_token"}
            payload = {"userId": test_user_id, "socketId": socket_id}
            
            async with session.post(f"{API_URL}/queue/join", json=payload, headers=headers) as response:
                result = await response.json()
                print(f"    Response: {json.dumps(result, indent=2)}")
                
                if result.get("success") and result.get("data", {}).get("success"):
                    print("    ✓ Successfully joined queue!")
                else:
                    print("    ✗ Failed to join queue")
                    await sio.disconnect()
                    return
        print()
        
        # Check queue status every 2 seconds
        print("[4] Monitoring queue status (checking every 2s for 20s)...")
        for i in range(10):
            await asyncio.sleep(2)
            
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": "Bearer test_token"}
                async with session.get(f"{API_URL}/queue/status", headers=headers) as response:
                    if response.status == 200:
                        status = await response.json()
                        queue_state = status.get("data", {}).get("state", "unknown")
                        wait_time = status.get("data", {}).get("wait_time_seconds", 0)
                        position = status.get("data", {}).get("position")
                        
                        print(f"    [{i*2+2}s] State: {queue_state}, Wait: {wait_time:.1f}s, Position: {position}")
                        
                        if queue_state == "ai_chat":
                            print(f"    ✓ AI chat started!")
                            ai_exchanges = status.get("data", {}).get("ai_chat_exchanges", 0)
                            session_id = status.get("data", {}).get("session_id")
                            print(f"       Exchanges: {ai_exchanges}, Session: {session_id}")
                            
                            # Try to send a message
                            if session_id:
                                print()
                                print("[5] Sending message to AI...")
                                payload = {
                                    "session_id": session_id,
                                    "message": "Hello! How are you?"
                                }
                                async with session.post(f"{API_URL}/chatbot/send-message", json=payload) as msg_response:
                                    if msg_response.status == 200:
                                        msg_result = await msg_response.json()
                                        print(f"    ✓ AI Response: {json.dumps(msg_result, indent=2)}")
                                    else:
                                        error = await msg_response.text()
                                        print(f"    ✗ Error: {msg_response.status} - {error}")
                            break
                    else:
                        print(f"    [{i*2+2}s] Status check failed: {response.status}")
        
        print()
        print("[6] Final status check...")
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": "Bearer test_token"}
            async with session.get(f"{API_URL}/queue/status", headers=headers) as response:
                if response.status == 200:
                    status = await response.json()
                    print(f"    Final status: {json.dumps(status, indent=2)}")
                else:
                    print(f"    Status check failed: {response.status}")
        
        print()
        print(f"[7] Total events received: {len(events_received)}")
        print("    Events:", [e[0] if isinstance(e, tuple) else e for e in events_received])
        
        await sio.disconnect()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            await sio.disconnect()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(test_queue_detailed())

