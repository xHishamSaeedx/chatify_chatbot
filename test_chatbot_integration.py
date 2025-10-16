"""
Test Chatbot Integration with Complex Messages
Tests the complete flow from backend to chatbot to OpenAI and back
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
BACKEND_URL = "http://localhost:3000"
CHATBOT_URL = "http://localhost:8000"
TEST_USER_ID = "test_user_123"
TEST_TOKEN = "fake_token_for_testing"  # Replace with real Firebase token in production

class ChatbotIntegrationTest:
    def __init__(self):
        self.session_id = None
        self.message_count = 0
        
    async def test_session_creation(self, personality="flirty-romantic"):
        """Test creating a chatbot session"""
        print("\n" + "="*80)
        print("🧪 TEST 1: Creating Chatbot Session")
        print("="*80)
        
        url = f"{CHATBOT_URL}/api/v1/chatbot/session"
        data = {
            "user_id": TEST_USER_ID,
            "template_id": personality
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=data, timeout=10) as response:
                    result = await response.json()
                    
                    if result.get("success"):
                        self.session_id = result.get("session_id")
                        print(f"✅ Session Created: {self.session_id}")
                        print(f"🎭 Personality: {personality}")
                        print(f"🐛 Debug Info: {result.get('debug_info')}")
                        return True
                    else:
                        print(f"❌ Failed: {result.get('error')}")
                        return False
            except Exception as e:
                print(f"❌ Error: {e}")
                return False
    
    async def test_send_message(self, message):
        """Test sending a message to the chatbot"""
        if not self.session_id:
            print("❌ No active session. Create a session first.")
            return False
        
        self.message_count += 1
        print("\n" + "="*80)
        print(f"🧪 TEST {self.message_count + 1}: Sending Message")
        print("="*80)
        print(f"📨 User Message: {message}")
        
        url = f"{CHATBOT_URL}/api/v1/chatbot/session/{self.session_id}/message"
        data = {"message": message}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=data, timeout=20) as response:
                    print(f"🔍 Response Status: {response.status}")
                    response_text = await response.text()
                    print(f"🔍 Response Text: {response_text[:200]}...")
                    
                    try:
                        result = json.loads(response_text)
                    except json.JSONDecodeError as je:
                        print(f"❌ JSON Decode Error: {je}")
                        print(f"❌ Raw Response: {response_text}")
                        return False
                    
                    if result.get("success"):
                        print(f"💬 AI Response: {result.get('response')}")
                        print(f"📊 Message Count: {result.get('message_count')}")
                        print(f"💖 Enthusiasm: {result.get('debug_info', {}).get('enthusiasm', 'N/A')}")
                        print(f"🔄 Exchange: {result.get('debug_info', {}).get('exchange_count', 'N/A')}/{result.get('debug_info', {}).get('response_limit', 'N/A')}")
                        
                        if result.get('terminated'):
                            print(f"🚪 Session Terminated: {result.get('termination_reason')}")
                            return 'terminated'
                        
                        if result.get('on_seen'):
                            print(f"👁️  On Seen: No response (user left on read)")
                        
                        return True
                    else:
                        print(f"❌ Failed: {result.get('error')}")
                        print(f"❌ Full Response: {result}")
                        return False
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
                return False
    
    async def test_complex_conversation(self):
        """Test a full conversation with complex messages"""
        print("\n" + "🌟"*40)
        print("CHATBOT INTEGRATION TEST - COMPLEX CONVERSATION")
        print("🌟"*40)
        
        # Create session
        if not await self.test_session_creation("flirty-romantic"):
            return
        
        # Test messages - from simple to complex
        test_messages = [
            # Greeting
            "Hey there! How's it going?",
            
            # Follow-up
            "What kind of stuff are you into?",
            
            # Complex/Flirty
            "You seem really interesting... I'm curious, what made you want to chat with someone tonight?",
            
            # Deep question
            "If you could go anywhere in the world right now, where would you go and what would you do there?",
            
            # Playful/Teasing
            "Wow, that's actually pretty cool. I have to say, you're not like the usual people I chat with. You're definitely keeping me interested 😏",
            
            # Intimate/Forward
            "So... are you the type who takes things slow or do you like to dive right in when you meet someone you vibe with?",
            
            # NSFW/Testing boundaries
            "You know what? I'm really enjoying this conversation. You're making me smile. Maybe even making me think about you a little more than I should... 😉",
            
            # Emotional/Personal
            "I've had a really rough day honestly. Just needed someone cool to talk to. Thanks for being here.",
            
            # Random/Testing adaptability
            "Random question - if you were a pizza topping, what would you be and why? 😂",
            
            # Philosophical
            "Do you think people can really change, or are we all just who we've always been deep down?",
            
            # Relationship focused
            "What's your ideal relationship like? Are you more of a hopeless romantic or do you keep things casual?",
            
            # Testing humor
            "Okay but real talk - pineapple on pizza. Yes or absolutely not? This might be a dealbreaker lol",
            
            # Flirty escalation
            "You know... I keep thinking about what you said earlier. You're really good at keeping someone's attention. I bet you're trouble in the best way 😘",
            
            # Deep/Vulnerable
            "Can I be honest? I don't usually open up like this, but there's something about you that makes it easy to talk. Like I can just be myself.",
            
            # Testing short responses
            "Nice",
            
            # Recovery from short response
            "Sorry, I mean that's actually really cool. Tell me more about that!",
            
            # Future planning
            "If we were hanging out in person right now, what would we be doing? Coffee? Adventure? Netflix? 👀",
            
            # Compliment
            "I have to say, you're really attractive. Like not just looks, but the way you talk and carry yourself. It's magnetic.",
            
            # Closing/Connection
            "I'm really glad I got to chat with you tonight. This was... different. In a good way. Would you want to keep talking sometime?"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n📍 Message {i}/{len(test_messages)}")
            result = await self.test_send_message(message)
            
            if result == 'terminated':
                print("\n⚠️  Session terminated by AI")
                break
            elif not result:
                print("\n❌ Test failed")
                break
            
            # Small delay between messages to simulate real conversation
            await asyncio.sleep(2)
        
        print("\n" + "🌟"*40)
        print("TEST COMPLETED")
        print("🌟"*40)

async def main():
    """Run the integration tests"""
    test = ChatbotIntegrationTest()
    
    # Test different personalities
    personalities = ["flirty-romantic", "energetic-fun", "anime-kawaii", "supportive-caring"]
    
    print("\n🚀 Starting Chatbot Integration Tests")
    print(f"⏰ Time: {datetime.now().isoformat()}")
    print(f"🔗 Backend: {BACKEND_URL}")
    print(f"🤖 Chatbot: {CHATBOT_URL}")
    
    # Run full conversation test
    await test.test_complex_conversation()
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED")
    print("="*80)
    print("\nNext Steps:")
    print("1. Review the conversation flow")
    print("2. Check enthusiasm changes")
    print("3. Verify response quality")
    print("4. Test termination conditions")
    print("5. Test 'on seen' behavior")
    print("\nRun this test multiple times to see different AI responses!")

if __name__ == "__main__":
    print("\n" + "🎯"*40)
    print("CHATIFY CHATBOT - INTEGRATION TEST SUITE")
    print("🎯"*40)
    
    asyncio.run(main())

