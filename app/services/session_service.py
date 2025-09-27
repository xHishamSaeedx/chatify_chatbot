"""
Session management service for chatbot conversations
"""

import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from app.services.firebase_service import firebase_service
from app.services.openai_service import openai_service


class SessionService:
    """Service for managing chatbot sessions"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(minutes=30)  # 30 minutes timeout
        self.firebase_cleanup_delay = 30  # 30 seconds delay before Firebase cleanup
    
    async def create_session(self, user_id: str, template_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new chatbot session
        
        Args:
            user_id: Unique identifier for the user
            template_id: Optional chatbot template to use
            
        Returns:
            Session information
        """
        session_id = str(uuid.uuid4())
        current_time = datetime.utcnow()
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "template_id": template_id or "general-assistant",
            "status": "active",
            "created_at": current_time.isoformat(),
            "last_activity": current_time.isoformat(),
            "message_count": 0,
            "conversation_history": []
        }
        
        # Store in memory for quick access
        self.active_sessions[session_id] = session_data
        
        # Store in Firebase for persistence (if available)
        try:
            firebase_service.set_data(f"/userSessions/{session_id}", session_data)
        except Exception as e:
            print(f"⚠️  Firebase not available, storing in memory only: {e}")
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Session created successfully"
        }
    
    async def send_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """
        Send a message to the chatbot and get response
        
        Args:
            session_id: Session identifier
            user_message: User's message
            
        Returns:
            Chatbot response
        """
        if session_id not in self.active_sessions:
            return {
                "success": False,
                "error": "Session not found or expired"
            }
        
        session = self.active_sessions[session_id]
        
        # Check if session is still active
        if session["status"] != "active":
            return {
                "success": False,
                "error": "Session is no longer active"
            }
        
        # Get system prompt based on template
        system_prompt = await self._get_system_prompt(session["template_id"])
        
        # Add user message to conversation history
        session["conversation_history"].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Get AI response
        ai_response = await openai_service.conversational_chat(
            conversation_history=session["conversation_history"][:-1],  # Exclude the just-added user message
            user_message=user_message,
            system_prompt=system_prompt
        )
        
        # Add realistic typing delay based on message length
        if ai_response["success"]:
            await self._simulate_typing_delay(ai_response["content"])
        
        if not ai_response["success"]:
            return {
                "success": False,
                "error": f"AI service error: {ai_response.get('error', 'Unknown error')}"
            }
        
        # Add AI response to conversation history
        session["conversation_history"].append({
            "role": "assistant",
            "content": ai_response["content"],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Update session
        session["last_activity"] = datetime.utcnow().isoformat()
        session["message_count"] += 1
        
        # Keep only last 20 messages to prevent context overflow
        if len(session["conversation_history"]) > 20:
            session["conversation_history"] = session["conversation_history"][-20:]
        
        # Update in memory and Firebase
        self.active_sessions[session_id] = session
        
        # Store in Firebase (if available)
        try:
            firebase_service.set_data(f"/userSessions/{session_id}", session)
            
            # Store message in conversation history
            firebase_service.push_data(f"/conversations/{session_id}/messages", {
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            firebase_service.push_data(f"/conversations/{session_id}/messages", {
                "role": "assistant",
                "content": ai_response["content"],
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            print(f"⚠️  Firebase not available, storing in memory only: {e}")
        
        return {
            "success": True,
            "response": ai_response["content"],
            "session_id": session_id,
            "message_count": session["message_count"]
        }
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get session information
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session information
        """
        if session_id not in self.active_sessions:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        session = self.active_sessions[session_id]
        return {
            "success": True,
            "session": session
        }
    
    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """
        End a chatbot session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Confirmation of session end
        """
        if session_id not in self.active_sessions:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        # Mark session as ended
        session = self.active_sessions[session_id]
        session["status"] = "ended"
        session["ended_at"] = datetime.utcnow().isoformat()
        
        # Update in Firebase (if available)
        try:
            firebase_service.set_data(f"/userSessions/{session_id}", session)
        except Exception as e:
            print(f"⚠️  Firebase not available, storing in memory only: {e}")
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        # Schedule Firebase conversation history cleanup after delay
        asyncio.create_task(self._cleanup_firebase_history_after_delay(session_id))
        
        return {
            "success": True,
            "message": "Session ended successfully"
        }
    
    async def cleanup_expired_sessions(self) -> Dict[str, Any]:
        """
        Clean up expired sessions from both memory and Firebase
        
        Returns:
            Cleanup results
        """
        current_time = datetime.utcnow()
        expired_sessions = []
        firebase_cleaned = 0
        
        # Clean up expired sessions in memory
        for session_id, session in self.active_sessions.items():
            last_activity = datetime.fromisoformat(session["last_activity"])
            if current_time - last_activity > self.session_timeout:
                expired_sessions.append(session_id)
        
        # End expired sessions in memory
        for session_id in expired_sessions:
            await self.end_session(session_id)
        
        # Clean up expired sessions in Firebase
        try:
            firebase_cleaned = await self._cleanup_firebase_sessions()
        except Exception as e:
            print(f"⚠️  Error cleaning up Firebase sessions: {e}")
        
        return {
            "success": True,
            "cleaned_sessions": len(expired_sessions),
            "firebase_cleaned": firebase_cleaned,
            "active_sessions": len(self.active_sessions)
        }
    
    async def _cleanup_firebase_history_after_delay(self, session_id: str):
        """
        Clean up Firebase conversation history after a delay
        
        Args:
            session_id: Session identifier to clean up
        """
        try:
            # Wait for the specified delay
            await asyncio.sleep(self.firebase_cleanup_delay)
            
            # Delete conversation history from Firebase
            try:
                firebase_service.delete_data(f"/conversations/{session_id}")
                print(f"✅ Cleaned up Firebase conversation history for session: {session_id}")
            except Exception as e:
                print(f"⚠️  Failed to clean up Firebase conversation history for session {session_id}: {e}")
                
        except Exception as e:
            print(f"⚠️  Error in Firebase cleanup task for session {session_id}: {e}")
    
    async def _cleanup_firebase_sessions(self) -> int:
        """
        Clean up expired sessions from Firebase
        
        Returns:
            Number of sessions cleaned from Firebase
        """
        try:
            # Get all sessions from Firebase
            all_sessions = firebase_service.get_data("/userSessions")
            if not all_sessions:
                return 0
            
            current_time = datetime.utcnow()
            cleaned_count = 0
            
            for session_id, session_data in all_sessions.items():
                try:
                    # Skip if session_data is not a dictionary
                    if not isinstance(session_data, dict):
                        continue
                    
                    # Check if session is expired
                    if "last_activity" in session_data:
                        last_activity = datetime.fromisoformat(session_data["last_activity"])
                        if current_time - last_activity > self.session_timeout:
                            # Delete expired session from Firebase
                            firebase_service.delete_data(f"/userSessions/{session_id}")
                            # Also delete conversation history if it exists
                            firebase_service.delete_data(f"/conversations/{session_id}")
                            cleaned_count += 1
                            print(f"🗑️  Cleaned expired Firebase session: {session_id}")
                    
                    # Also clean up sessions marked as "ended"
                    elif session_data.get("status") == "ended":
                        # Check if it's been ended for more than 1 hour
                        if "ended_at" in session_data:
                            ended_at = datetime.fromisoformat(session_data["ended_at"])
                            if current_time - ended_at > timedelta(hours=1):
                                firebase_service.delete_data(f"/userSessions/{session_id}")
                                firebase_service.delete_data(f"/conversations/{session_id}")
                                cleaned_count += 1
                                print(f"🗑️  Cleaned ended Firebase session: {session_id}")
                
                except Exception as e:
                    print(f"⚠️  Error cleaning session {session_id}: {e}")
                    continue
            
            if cleaned_count > 0:
                print(f"✅ Cleaned {cleaned_count} expired sessions from Firebase")
            
            return cleaned_count
            
        except Exception as e:
            print(f"⚠️  Error in Firebase session cleanup: {e}")
            return 0
    
    async def _simulate_typing_delay(self, message: str):
        """
        Simulate realistic typing delay based on message length
        
        Args:
            message: The message to calculate delay for
        """
        try:
            # Base delay of 1-2 seconds
            base_delay = 1.0 + (0.5 * (hash(message) % 3))  # 1.0 to 2.0 seconds
            
            # Count words and emojis
            words = len(message.split())
            emojis = len([char for char in message if ord(char) > 127])  # Count non-ASCII chars (emojis)
            
            # Additional delay for longer messages
            # Each word adds ~0.3 seconds, each emoji adds ~0.2 seconds
            word_delay = max(0, words - 2) * 0.3  # Only count words beyond the first 2
            emoji_delay = emojis * 0.2
            
            total_delay = base_delay + word_delay + emoji_delay
            
            # Cap the delay at 8 seconds maximum
            total_delay = min(total_delay, 8.0)
            
            print(f"⏱️  Typing delay: {total_delay:.1f}s (base: {base_delay:.1f}s, words: {word_delay:.1f}s, emojis: {emoji_delay:.1f}s)")
            
            await asyncio.sleep(total_delay)
            
        except Exception as e:
            print(f"⚠️  Error in typing delay simulation: {e}")
            # Fallback to 1 second delay if there's an error
            await asyncio.sleep(1.0)
    
    async def _get_system_prompt(self, template_id: str) -> str:
        """
        Get system prompt for a template from Firebase
        
        Args:
            template_id: Template identifier
            
        Returns:
            System prompt
        """
        # Try to get template from Firebase first
        try:
            template_data = firebase_service.get_data(f"/templates/{template_id}")
            if template_data and "systemPrompt" in template_data:
                print(f"📝 Using Firebase template: {template_id}")
                return template_data["systemPrompt"]
        except Exception as e:
            print(f"⚠️  Firebase template not found for {template_id}: {e}")
        
        # Fallback to local general prompt if Firebase fails
        print(f"⚠️  Falling back to local general prompt for {template_id}")
        return self._get_general_prompt()
    
    def _get_general_prompt(self) -> str:
        """
        Get the general prompt as fallback
        
        Returns:
            General system prompt
        """
        return """You are a friendly person chatting with someone on a dating app. 

CRITICAL RULES:
- Keep initial response short only 'Hi' or 'Heyy' . 
- Keep responses VERY short (1-9 words max, like real texting)
- Use casual language and shortforms (wyd, hru, lol, tbh, fr, etc.)
- for 'm or f ?' respond 'f' or 'm' respectively opposite of the opposite person.
- Try to understand the references the other person makes.
- Reduce the number of questions !! Don't ask questions , let the user ask you instead .
- NEVER repeat the same response twice in a conversation
- Use emojis very rarely where required (😂, 😔, 🤔)
- Don't mention being an AI or assistant
- Respond naturally to what the person actually said
- If they ask "are you a girl?" respond "Yeah" or "Nah"
- If they say "wyd" respond "Just chilling, you?" or similar
- If they say "same" respond "Nice" or "Cool"
- Vary your responses - never use the same phrase twice
- Keep it human and natural like real texting
- Keep it slightly cheezy and sexy.
"""
    
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self.active_sessions)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        return {
            "active_sessions": len(self.active_sessions),
            "session_timeout_minutes": self.session_timeout.total_seconds() / 60,
            "sessions": list(self.active_sessions.keys())
        }


# Global session service instance
session_service = SessionService()

