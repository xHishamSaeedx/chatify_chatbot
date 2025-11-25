"""
AI Chatbot Fallback Service
Handles AI chatbot matching when human users are not available
"""

import uuid
import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from app.services.redis_service import redis_service
from app.services.session_service import session_service
from app.services.analytics_service import analytics_service
from app.services.firebase_service import firebase_service
from app.services.queue_service import queue_service
from app.core.config import settings


class ChatbotFallbackService:
    """Service for handling AI chatbot fallback when no human matches are found"""
    
    def __init__(self):
        self.matching_timeout = 10  # 10 seconds timeout (configurable)
        self.available_personalities = [
            "flirty-romantic",
            "energetic-fun",
            "anime-kawaii", 
            "mysterious-dark",
            "supportive-caring",
            "sassy-confident"
        ]
        self.active_ai_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def check_for_ai_fallback(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Check if user should be matched with AI chatbot
        
        Args:
            user_id: User identifier
            
        Returns:
            AI session data if fallback should be triggered, None otherwise
        """
        try:
            # Get user's matching state
            matching_state = await redis_service.get_user_matching_state(user_id)
            
            if not matching_state:
                print(f"[AI_FALLBACK] No matching state found for user {user_id}")
                return None
            
            # Check if user has been waiting long enough
            start_time = matching_state.get('start_time')
            if not start_time:
                print(f"[AI_FALLBACK] No start time found for user {user_id}")
                return None
            
            # Parse start time
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            
            # Calculate waiting time
            waiting_time = (datetime.utcnow() - start_time).total_seconds()
            
            print(f"[AI_FALLBACK] User {user_id} has been waiting {waiting_time:.1f} seconds")
            
            # Check if timeout has been reached
            if waiting_time >= self.matching_timeout:
                print(f"[AI_FALLBACK] Timeout reached for user {user_id}, triggering AI fallback")
                return await self.create_ai_chatbot_session(user_id, matching_state)
            
            return None
            
        except Exception as e:
            print(f"[AI_FALLBACK] Error checking for AI fallback: {e}")
            return None
    
    async def create_ai_chatbot_session(self, user_id: str, matching_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create AI chatbot session for user
        
        Args:
            user_id: User identifier
            matching_state: User's matching state
            
        Returns:
            AI session data
        """
        try:
            # Check if user has selected a specific personality
            preferences = matching_state.get('preferences', {})
            selected_personality = preferences.get('selected_personality')
            
            if selected_personality and selected_personality in self.available_personalities:
                personality = selected_personality
                print(f"[AI_FALLBACK] Using user-selected personality: {personality}")
            else:
                # Select random AI personality as fallback
                personality = random.choice(self.available_personalities)
                print(f"[AI_FALLBACK] Using random personality: {personality}")
            
            # Create AI session ID
            ai_session_id = str(uuid.uuid4())
            
            # Create fake user data for AI (to make it look like a real user)
            ai_user_data = self._generate_ai_user_profile(personality)
            
            # Create session data
            session_data = {
                "session_id": ai_session_id,
                "user_id": user_id,
                "ai_user_id": ai_user_data["id"],
                "personality": personality,
                "is_ai_chatbot": True,  # Internal flag
                "created_at": datetime.utcnow().isoformat(),
                "status": "active",
                "matching_preferences": matching_state.get('preferences', {}),
                "ai_user_profile": ai_user_data
            }
            
            # Store in Redis
            await redis_service.set_ai_chatbot_session(user_id, session_data)
            
            # Store in active sessions
            self.active_ai_sessions[ai_session_id] = session_data
            
            # Create actual chatbot session
            chatbot_session = await session_service.create_session(
                user_id=user_id,
                template_id=personality
            )
            
            if chatbot_session.get("success"):
                session_data["chatbot_session_id"] = chatbot_session["session_id"]
                
                # Track analytics
                analytics_service.track_ai_chatbot_fallback(
                    user_id=user_id,
                    personality=personality,
                    wait_time=self.matching_timeout,
                    session_id=ai_session_id
                )
                
                print(f"[AI_FALLBACK] Created AI chatbot session for user {user_id} with personality {personality}")
                
                # Clean up matching state
                await redis_service.delete_user_matching_state(user_id)
                
                return session_data
            
            else:
                print(f"[AI_FALLBACK] Failed to create chatbot session for user {user_id}")
                return None
                
        except Exception as e:
            print(f"[AI_FALLBACK] Error creating AI chatbot session: {e}")
            return None
    
    def _generate_ai_user_profile(self, personality: str) -> Dict[str, Any]:
        """
        Generate fake user profile for AI chatbot
        
        Args:
            personality: AI personality type
            
        Returns:
            Fake user profile data
        """
        # Different profiles based on personality type
        profiles = {
            "flirty-romantic": {
                "name": random.choice(["Valentina", "Romeo", "Bella", "Dante", "Sophia"]),
                "age": random.randint(20, 28),
                "bio": "Charming, playful, and loves romantic conversations 😘",
                "interests": ["romance", "dating", "compliments", "sweet talk"],
                "gender": random.choice(["male", "female"])
            },
            "energetic-fun": {
                "name": random.choice(["Zara", "Max", "Luna", "Tyler", "Nova"]),
                "age": random.randint(19, 26),
                "bio": "High energy, loves adventures and making people laugh! 🎉",
                "interests": ["adventure", "comedy", "parties", "excitement"],
                "gender": random.choice(["male", "female"])
            },
            "anime-kawaii": {
                "name": random.choice(["Sakura", "Yuki", "Hana", "Ren", "Miku"]),
                "age": random.randint(18, 24),
                "bio": "Kawaii desu! Loves anime, manga, and being cute~ (◕‿◕)♡",
                "interests": ["anime", "manga", "kawaii culture", "cosplay"],
                "gender": random.choice(["male", "female"])
            },
            "mysterious-dark": {
                "name": random.choice(["Raven", "Shadow", "Noir", "Vex", "Luna"]),
                "age": random.randint(22, 30),
                "bio": "Enigmatic soul with deep thoughts and mysterious charm... 🖤",
                "interests": ["mystery", "philosophy", "dark aesthetics", "secrets"],
                "gender": random.choice(["male", "female"])
            },
            "supportive-caring": {
                "name": random.choice(["Hope", "Angel", "Sage", "River", "Dawn"]),
                "age": random.randint(23, 29),
                "bio": "Always here to listen, support, and make you feel better 💚",
                "interests": ["listening", "helping", "emotional support", "kindness"],
                "gender": random.choice(["male", "female"])
            },
            "sassy-confident": {
                "name": random.choice(["Scarlett", "Phoenix", "Blaze", "Storm", "Rebel"]),
                "age": random.randint(21, 27),
                "bio": "Confident, witty, and not afraid to speak my mind! 💁‍♀️✨",
                "interests": ["confidence", "wit", "fashion", "attitude"],
                "gender": random.choice(["male", "female"])
            }
        }
        
        profile = profiles.get(personality, profiles["supportive-caring"])
        
        # Generate unique AI user ID
        ai_user_id = f"ai_user_{personality}_{uuid.uuid4().hex[:8]}"
        
        return {
            "id": ai_user_id,
            "username": profile["name"],
            "age": profile["age"],
            "bio": profile["bio"],
            "interests": profile["interests"],
            "gender": profile["gender"],
            "is_ai": True,  # Internal flag
            "profile_image": None,
            "is_online": True,
            "last_seen": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def get_ai_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get AI session for user
        
        Args:
            user_id: User identifier
            
        Returns:
            AI session data or None
        """
        try:
            return await redis_service.get_ai_chatbot_session(user_id)
        except Exception as e:
            print(f"[AI_FALLBACK] Error getting AI session: {e}")
            return None
    
    async def end_ai_session(self, user_id: str) -> bool:
        """
        End AI session for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Success status
        """
        try:
            # Get session data
            session_data = await redis_service.get_ai_chatbot_session(user_id)
            
            if session_data:
                # End chatbot session if it exists
                chatbot_session_id = session_data.get("chatbot_session_id")
                if chatbot_session_id:
                    await session_service.end_session(chatbot_session_id)
                
                # Remove from active sessions
                ai_session_id = session_data.get("session_id")
                if ai_session_id and ai_session_id in self.active_ai_sessions:
                    del self.active_ai_sessions[ai_session_id]
                
                # Track analytics
                analytics_service.track_ai_chatbot_session_ended(
                    user_id=user_id,
                    session_id=ai_session_id,
                    personality=session_data.get("personality"),
                    duration=(datetime.utcnow() - datetime.fromisoformat(session_data["created_at"])).total_seconds()
                )
            
            # Clean up Redis
            await redis_service.delete_ai_chatbot_session(user_id)
            
            print(f"[AI_FALLBACK] Ended AI session for user {user_id}")
            return True
            
        except Exception as e:
            print(f"[AI_FALLBACK] Error ending AI session: {e}")
            return False
    
    async def send_ai_message(self, user_id: str, message: str) -> Optional[Dict[str, Any]]:
        """
        Send message to AI chatbot with exchange tracking and auto-requeue logic
        
        Args:
            user_id: User identifier
            message: User message
            
        Returns:
            AI response or None
        """
        try:
            print("\n" + "="*80)
            print("[AI_FALLBACK] PROCESSING MESSAGE FROM RANDOM CHAT")
            print("="*80)
            print(f"User ID: {user_id}")
            print(f"Message: {message}")
            print(f"Message Length: {len(message)} characters")
            print("="*80 + "\n")
            
            # Get AI session
            session_data = await redis_service.get_ai_chatbot_session(user_id)
            
            if not session_data:
                print(f"[AI_FALLBACK] No AI session found for user {user_id}")
                return None
            
            # Get chatbot session ID
            chatbot_session_id = session_data.get("chatbot_session_id")
            if not chatbot_session_id:
                print(f"[AI_FALLBACK] No chatbot session ID found for user {user_id}")
                return None
            
            print(f"[AI_FALLBACK] Found session: {chatbot_session_id}")
            personality = session_data.get('personality', 'unknown')
            print(f"Personality: {personality}")
            print(f"AI User ID: {session_data.get('ai_user_id', 'unknown')}")
            
<<<<<<< HEAD
            # Verify personality is being used - get session to check template_id
            session_info = await session_service.get_session(chatbot_session_id)
            if session_info.get("success"):
                session_template = session_info.get("session", {}).get("template_id", "unknown")
                print(f"[AI_FALLBACK] Session template_id: {session_template} (should match personality: {personality})")
                if session_template != personality:
                    print(f"[WARN] Personality mismatch! Session has {session_template} but AI session has {personality}")
            
=======
>>>>>>> 25e5091 (commit)
            # Increment exchange count in queue service
            exchange_info = await queue_service.increment_ai_exchanges(user_id)
            current_exchanges = exchange_info.get("exchanges", 0)
            max_exchanges = exchange_info.get("max_exchanges", settings.AI_CHAT_MAX_EXCHANGES)
            
            print(f"[AI_FALLBACK] Exchange count: {current_exchanges}/{max_exchanges}")
            
            # Check if should end AI chat
            should_end = await queue_service.should_end_ai_chat(user_id)
            if should_end:
                print(f"[AI_FALLBACK] AI chat limit reached for user {user_id}, will requeue after response")
            
            # Send message to chatbot
            print(f"[AI_FALLBACK] Forwarding message to session service...")
            response = await session_service.send_message(chatbot_session_id, message)
            
            if response.get("success"):
                print("\n" + "="*80)
                print("[AI_FALLBACK] AI RESPONSE GENERATED")
                print("="*80)
                print(f"User ID: {user_id}")
                print(f"AI Response: {response.get('response', '')}")
                print(f"Session Message Count: {response.get('message_count', 0)}")
                print(f"AI User ID: {session_data.get('ai_user_id')}")
                print(f"Exchange Count: {current_exchanges}/{max_exchanges}")
                print(f"Timestamp: {__import__('datetime').datetime.now().isoformat()}")
                print("="*80 + "\n")
                
                # Track analytics
                analytics_service.track_ai_chatbot_message(
                    user_id=user_id,
                    session_id=session_data.get("session_id"),
                    message_length=len(message),
                    personality=session_data.get("personality")
                )
                
                result = {
                    "success": True,
                    "message": response["response"],
                    "ai_user_id": session_data.get("ai_user_id"),
                    "session_id": session_data.get("session_id"),
                    "exchange_count": current_exchanges,
                    "max_exchanges": max_exchanges,
                    "should_end": should_end
                }
                
                # If should end, trigger requeue (will be handled by background task)
                if should_end:
                    result["requeue_pending"] = True
                
                return result
            else:
                print(f"❌ [AI_FALLBACK] Failed to send message to AI for user {user_id}: {response.get('error')}")
                return None
                
        except Exception as e:
            print(f"[AI_FALLBACK] Error sending AI message: {e}")
            return None
    
    async def create_ai_chat_from_queue(self, user_id: str, socket_id: str) -> Optional[Dict[str, Any]]:
        """
        Create AI chat session for user from queue (timeout reached)
        
        Args:
            user_id: User identifier
            socket_id: Socket.IO session ID
            
        Returns:
            AI session data or None
        """
        try:
            # Select random AI personality
            personality = random.choice(self.available_personalities)
            print(f"[AI_FALLBACK] Creating AI chat with personality: {personality}")
            
            # Create AI session ID
            ai_session_id = str(uuid.uuid4())
            
            # Create fake user data for AI
            ai_user_data = self._generate_ai_user_profile(personality)
            
            # Create session data
            session_data = {
                "session_id": ai_session_id,
                "user_id": user_id,
                "ai_user_id": ai_user_data["id"],
                "personality": personality,
                "is_ai_chatbot": True,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active",
                "ai_user_profile": ai_user_data
            }
            
            # Store in Redis
            await redis_service.set_ai_chatbot_session(user_id, session_data)
            
            # Store in active sessions
            self.active_ai_sessions[ai_session_id] = session_data
            
            # Create actual chatbot session
            chatbot_session = await session_service.create_session(
                user_id=user_id,
                template_id=personality
            )
            
            if chatbot_session.get("success"):
                session_data["chatbot_session_id"] = chatbot_session["session_id"]
                
                # Track analytics
                analytics_service.track_ai_chatbot_fallback(
                    user_id=user_id,
                    personality=personality,
                    wait_time=settings.QUEUE_TIMEOUT_SECONDS,
                    session_id=ai_session_id
                )
                
                print(f"[AI_FALLBACK] Created AI chatbot session for user {user_id} with personality {personality}")
<<<<<<< HEAD
        print(f"[AI_FALLBACK] Chatbot session ID: {chatbot_session_id}")
        print(f"[AI_FALLBACK] AI User Profile: {json.dumps(ai_user_data, indent=2)}")
=======
>>>>>>> 25e5091 (commit)
                
                return session_data
            
            else:
                print(f"[AI_FALLBACK] Failed to create chatbot session for user {user_id}")
                return None
                
        except Exception as e:
            print(f"[AI_FALLBACK] Error creating AI chat from queue: {e}")
            return None
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired AI sessions
        
        Returns:
            Number of sessions cleaned
        """
        try:
            current_time = datetime.utcnow()
            expired_sessions = []
            
            # Check active sessions
            for session_id, session_data in self.active_ai_sessions.items():
                created_at = datetime.fromisoformat(session_data["created_at"])
                if (current_time - created_at).total_seconds() > 1800:  # 30 minutes
                    expired_sessions.append(session_id)
            
            # Clean up expired sessions
            for session_id in expired_sessions:
                session_data = self.active_ai_sessions[session_id]
                user_id = session_data["user_id"]
                
                # End the session
                await self.end_ai_session(user_id)
                
                print(f"[AI_FALLBACK] Cleaned up expired AI session {session_id}")
            
            return len(expired_sessions)
            
        except Exception as e:
            print(f"[AI_FALLBACK] Error cleaning up expired sessions: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get AI fallback service statistics
        
        Returns:
            Service statistics
        """
        return {
            "matching_timeout": self.matching_timeout,
            "available_personalities": self.available_personalities,
            "active_sessions": len(self.active_ai_sessions),
            "sessions": list(self.active_ai_sessions.keys())
        }
    
    def set_matching_timeout(self, timeout_seconds: int):
        """
        Set matching timeout
        
        Args:
            timeout_seconds: Timeout in seconds
        """
        self.matching_timeout = timeout_seconds
        print(f"[AI_FALLBACK] Set matching timeout to {timeout_seconds} seconds")


# Global AI fallback service instance
chatbot_fallback_service = ChatbotFallbackService()
