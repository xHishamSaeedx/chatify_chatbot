"""
Test to verify personality is being used in AI responses
"""

import asyncio
import aiohttp
import json
from datetime import datetime


BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"


async def test_personality():
    """Test that different personalities produce different responses"""
    print("="*80)
    print("PERSONALITY VERIFICATION TEST")
    print("="*80)
    print()
    
    test_user_id = "test_personality_user"
    socket_id = "test_socket_personality"
    headers = {"Authorization": "Bearer test_token"}
    
    async with aiohttp.ClientSession() as session:
        # Join queue
        print("[1] Joining queue...")
        payload = {"userId": test_user_id, "socketId": socket_id}
        async with session.post(f"{API_URL}/queue/join", json=payload, headers=headers) as r:
            result = await r.json()
            print(f"    Joined: {result.get('success')}")
        print()
        
        # Wait for AI chat to start (15s timeout)
        print("[2] Waiting for AI chat to start (15s timeout)...")
        ai_chat_started = False
        for i in range(20):
            await asyncio.sleep(1)
            
            async with session.get(f"{API_URL}/queue/status?userId={test_user_id}", headers=headers) as r:
                if r.status == 200:
                    status = await r.json()
                    data = status.get("data", {})
                    state = data.get("state")
                    session_id = data.get("session_id")
                    
                    if state == "ai_chat" and session_id:
                        print(f"    [OK] AI chat started at {i+1}s with session: {session_id[:20]}...")
                        ai_chat_started = True
                        print()
                        
                        # Get AI session to find chatbot_session_id
                        print("[3] Getting AI session info...")
                        # We need to get the chatbot_session_id from the AI fallback service
                        # The session_id in queue is the AI session ID, we need the chatbot_session_id
                        
                        # Use the chatbot_fallback endpoint to send messages (it will use the correct session)
                        print()
                        print("[4] Testing personality with different messages...")
                        print("    Using chatbot fallback endpoint which uses the personality session")
                        print()
                        
                        test_messages = [
                            "Hello!",
                            "How are you?",
                            "What's your name?",
                            "Tell me about yourself"
                        ]
                        
                        for msg in test_messages:
                            print(f"    Sending: '{msg}'")
                            
                            # Use the AI fallback send message endpoint
                            msg_payload = {
                                "user_id": test_user_id,
                                "message": msg
                            }
                            
                            async with session.post(f"{API_URL}/ai-fallback/send-ai-message", json=msg_payload) as msg_r:
                                if msg_r.status == 200:
                                    msg_result = await msg_r.json()
                                    if msg_result.get("success"):
                                        response = msg_result.get("message", "")
                                        print(f"    Response: {response[:200]}")
                                        
                                        # Check for personality indicators
                                        personality_indicators = {
                                            "flirty": ["cute", "sweet", "flirt", "sexy", "hot", "gorgeous", "babe", "hottie"],
                                            "energetic": ["awesome", "amazing", "exciting", "fun", "cool", "yay", "woo"],
                                            "kawaii": ["kawaii", "desu", "cute", "adorable", "uwu"],
                                            "mysterious": ["interesting", "hmm", "maybe", "perhaps", "sure"],
                                            "caring": ["sweetie", "dear", "hun", "support", "here for you"],
                                            "sassy": ["sure", "whatever", "ok", "if you say so", "right"]
                                        }
                                        
                                        response_lower = response.lower()
                                        detected = []
                                        for pers, indicators in personality_indicators.items():
                                            if any(ind in response_lower for ind in indicators):
                                                detected.append(pers)
                                        
                                        if detected:
                                            print(f"    → Personality indicators: {', '.join(detected)}")
                                        else:
                                            print(f"    → No clear personality indicators (might be general-assistant)")
                                    else:
                                        print(f"    ✗ Error: {msg_result.get('error')}")
                                else:
                                    error_text = await msg_r.text()
                                    print(f"    ✗ HTTP Error: {msg_r.status} - {error_text}")
                            
                            await asyncio.sleep(1)
                        
                        break
        
        if not ai_chat_started:
            print("    ✗ AI chat did not start within 20 seconds")
            print("    This might indicate an issue with the timeout or AI session creation")
        
        print()
        print("="*80)
        print("TEST COMPLETE")
        print("="*80)
        print("\nNote: Check server logs for personality information:")
        print("  - Look for '[SESSION] Created session with personality: ...'")
        print("  - Look for '[AI_FALLBACK] Personality: ...'")
        print("  - Look for '[SESSION] Using personality: ...'")


if __name__ == "__main__":
    asyncio.run(test_personality())

