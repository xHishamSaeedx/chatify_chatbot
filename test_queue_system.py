"""
Test script for queue system
Tests: queue joining, AI pairing after timeout, and message exchange
"""

import asyncio
import aiohttp
import socketio
import json
from datetime import datetime


# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"
SOCKET_URL = BASE_URL


async def test_queue_system():
    """Test the complete queue system flow"""
    print("="*80)
    print("QUEUE SYSTEM TEST")
    print("="*80)
    print(f"Testing: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*80 + "\n")
    
    # Test 1: Check if server is running
    print("[TEST 1] Checking if server is running...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ Server is running: {data}")
                else:
                    print(f"✗ Server returned status {response.status}")
                    return
    except Exception as e:
        print(f"✗ Cannot connect to server: {e}")
        print("   Make sure the server is running on http://localhost:8000")
        return
    
    print()
    
    # Test 2: Check active count endpoint
    print("[TEST 2] Checking active count endpoint...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/queue/active-count") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ Active count endpoint works: {data}")
                else:
                    print(f"✗ Active count endpoint returned status {response.status}")
    except Exception as e:
        print(f"✗ Error checking active count: {e}")
    
    print()
    
    # Test 3: Test queue flow with Socket.IO
    print("[TEST 3] Testing queue flow with Socket.IO...")
    print("   This will:")
    print("   1. Connect via Socket.IO")
    print("   2. Join the queue")
    print("   3. Wait for timeout (15s) or AI pairing")
    print("   4. Send a message to AI")
    print("   5. Verify AI response")
    print()
    
    # Create Socket.IO client
    sio = socketio.AsyncClient()
    events_received = []
    ai_session_data = None
    
    @sio.event
    async def connect():
        print("✓ Connected to Socket.IO server")
        events_received.append("connect")
    
    @sio.event
    async def disconnect():
        print("✓ Disconnected from Socket.IO server")
        events_received.append("disconnect")
    
    @sio.event
    async def queue_joined(data):
        print(f"✓ Received queue_joined event: {json.dumps(data, indent=2)}")
        events_received.append(("queue_joined", data))
    
    @sio.event
    async def queue_matched(data):
        print(f"✓ Received queue_matched event: {json.dumps(data, indent=2)}")
        events_received.append(("queue_matched", data))
    
    @sio.event
    async def queue_timeout(data):
        print(f"✓ Received queue_timeout event: {json.dumps(data, indent=2)}")
        events_received.append(("queue_timeout", data))
    
    @sio.event
    async def ai_chat_started(data):
        print(f"✓ Received ai_chat_started event: {json.dumps(data, indent=2)}")
        events_received.append(("ai_chat_started", data))
        nonlocal ai_session_data
        ai_session_data = data
    
    @sio.event
    async def ai_chat_ended(data):
        print(f"✓ Received ai_chat_ended event: {json.dumps(data, indent=2)}")
        events_received.append(("ai_chat_ended", data))
    
    @sio.event
    async def queue_ad(data):
        print(f"✓ Received queue_ad event: {json.dumps(data, indent=2)}")
        events_received.append(("queue_ad", data))
    
    @sio.event
    async def active_count_update(data):
        print(f"✓ Received active_count_update event: {json.dumps(data, indent=2)}")
        events_received.append(("active_count_update", data))
    
    @sio.event
    async def new_message(data):
        print(f"✓ Received new_message event: {json.dumps(data, indent=2)}")
        events_received.append(("new_message", data))
    
    try:
        # Connect to Socket.IO
        print("   Connecting to Socket.IO server...")
        await sio.connect(SOCKET_URL, wait_timeout=10)
        await asyncio.sleep(1)  # Wait for connection to stabilize
        
        # Get socket ID
        socket_id = sio.sid
        print(f"   Socket ID: {socket_id}")
        
        # Test user ID
        test_user_id = f"test_user_{datetime.now().timestamp()}"
        print(f"   Test User ID: {test_user_id}")
        print()
        
        # Join queue via API
        print("[TEST 3.1] Joining queue via API...")
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": "Bearer test_token"}
            payload = {
                "userId": test_user_id,
                "socketId": socket_id
            }
            
            async with session.post(
                f"{API_URL}/queue/join",
                json=payload,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ Joined queue successfully: {json.dumps(data, indent=2)}")
                else:
                    error_text = await response.text()
                    print(f"✗ Failed to join queue: {response.status} - {error_text}")
                    await sio.disconnect()
                    return
        
        # Wait for events
        print()
        print("[TEST 3.2] Waiting for queue events (timeout: 20s)...")
        print("   Expected events:")
        print("   - queue_joined")
        print("   - queue_ad (every 10s)")
        print("   - queue_timeout (after 15s)")
        print("   - ai_chat_started")
        print()
        
        # Wait up to 20 seconds for timeout and AI chat
        for i in range(20):
            await asyncio.sleep(1)
            
            # Check if we got AI chat started
            if ai_session_data:
                print(f"\n✓ AI chat started after {i+1} seconds!")
                break
            
            if i % 5 == 0 and i > 0:
                print(f"   ... waiting ({i}s / 20s)")
        
        if not ai_session_data:
            print("\n✗ AI chat did not start within 20 seconds")
            print("   This might be expected if timeout is longer or matching is working")
            await sio.disconnect()
            return
        
        # Test 4: Send message to AI
        print()
        print("[TEST 4] Sending message to AI chatbot...")
        
        if ai_session_data:
            session_id = ai_session_data.get("session_id")
            print(f"   AI Session ID: {session_id}")
            
            # Send message via chatbot endpoint
            test_message = "Hello! How are you?"
            print(f"   Sending message: '{test_message}'")
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "session_id": session_id,
                    "message": test_message
                }
                
                async with session.post(
                    f"{API_URL}/chatbot/send-message",
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✓ AI responded: {json.dumps(data, indent=2)}")
                        
                        if data.get("success") and data.get("response"):
                            print(f"\n✓ SUCCESS! AI message received: '{data.get('response')}'")
                        else:
                            print(f"\n✗ AI response missing or failed: {data}")
                    else:
                        error_text = await response.text()
                        print(f"✗ Failed to send message: {response.status} - {error_text}")
        
        # Wait a bit more for any additional events
        print()
        print("[TEST 5] Waiting for additional events (5s)...")
        await asyncio.sleep(5)
        
        # Summary
        print()
        print("="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total events received: {len(events_received)}")
        print("\nEvents breakdown:")
        event_types = {}
        for event in events_received:
            if isinstance(event, tuple):
                event_type = event[0]
            else:
                event_type = event
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        for event_type, count in event_types.items():
            print(f"  - {event_type}: {count}")
        
        print()
        print("Expected events:")
        print("  ✓ queue_joined - User joined queue")
        print("  ✓ queue_ad - Ad displayed during wait")
        print("  ✓ queue_timeout - Timeout reached")
        print("  ✓ ai_chat_started - AI chat began")
        print("  ✓ new_message - AI message received (if using socket)")
        
        # Check if we got the key events
        event_names = [e[0] if isinstance(e, tuple) else e for e in events_received]
        key_events = ["queue_joined", "queue_timeout", "ai_chat_started"]
        missing_events = [e for e in key_events if e not in event_names]
        
        if missing_events:
            print(f"\n⚠ Missing events: {missing_events}")
        else:
            print("\n✓ All key events received!")
        
        print("="*80)
        
        # Disconnect
        await sio.disconnect()
        
    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        try:
            await sio.disconnect()
        except:
            pass


if __name__ == "__main__":
    print("\nStarting queue system test...\n")
    asyncio.run(test_queue_system())

