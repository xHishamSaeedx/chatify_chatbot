"""
Redis service for user session tracking and AI chatbot fallback
"""

import redis
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.core.config import settings


class RedisService:
    """Service for managing Redis connections and operations"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.is_connected = False
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            # Check for Redis URL first (for cloud deployments)
            redis_url = getattr(settings, 'REDIS_URL', None)
            
            if redis_url:
                # Use Redis URL for cloud deployments
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                print(f"[REDIS] Using Redis URL: {redis_url}")
            else:
                # Fallback to individual settings for local development
                redis_host = getattr(settings, 'REDIS_HOST', 'localhost')
                redis_port = getattr(settings, 'REDIS_PORT', 6379)
                redis_db = getattr(settings, 'REDIS_DB', 0)
                redis_password = getattr(settings, 'REDIS_PASSWORD', None)
                
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    password=redis_password,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                print(f"[REDIS] Using Redis host: {redis_host}:{redis_port}")
            
            # Test connection
            await self._test_connection()
            self.is_connected = True
            print(f"[REDIS] Connected successfully to {redis_host}:{redis_port}")
            
        except Exception as e:
            print(f"[REDIS] Failed to connect: {e}")
            self.is_connected = False
            # Fallback to in-memory storage if Redis is not available
            self._fallback_storage = {}
    
    async def _test_connection(self):
        """Test Redis connection"""
        if self.redis_client:
            # Run Redis ping in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.redis_client.ping)
    
    async def set_user_matching_state(self, user_id: str, state: Dict[str, Any], ttl: int = 300) -> bool:
        """
        Set user matching state in Redis
        
        Args:
            user_id: User identifier
            state: Matching state data
            ttl: Time to live in seconds (default 5 minutes)
            
        Returns:
            Success status
        """
        try:
            if not self.is_connected or not self.redis_client:
                # Fallback to in-memory storage
                if not hasattr(self, '_fallback_storage'):
                    self._fallback_storage = {}
                self._fallback_storage[f"matching:{user_id}"] = {
                    'data': state,
                    'expires': datetime.utcnow() + timedelta(seconds=ttl)
                }
                print(f"[REDIS] Stored matching state in memory for user {user_id}")
                return True
            
            key = f"matching:{user_id}"
            state_data = json.dumps(state)
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self.redis_client.setex, 
                key, 
                ttl, 
                state_data
            )
            
            print(f"[REDIS] Stored matching state for user {user_id}: {result}")
            return result
            
        except Exception as e:
            print(f"[REDIS] Error setting user matching state: {e}")
            return False
    
    async def get_user_matching_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user matching state from Redis
        
        Args:
            user_id: User identifier
            
        Returns:
            Matching state data or None
        """
        try:
            if not self.is_connected or not self.redis_client:
                # Fallback to in-memory storage
                if not hasattr(self, '_fallback_storage'):
                    return None
                
                key = f"matching:{user_id}"
                if key in self._fallback_storage:
                    entry = self._fallback_storage[key]
                    if datetime.utcnow() < entry['expires']:
                        return entry['data']
                    else:
                        # Expired, remove it
                        del self._fallback_storage[key]
                return None
            
            key = f"matching:{user_id}"
            
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self.redis_client.get, key)
            
            if data:
                state = json.loads(data)
                print(f"[REDIS] Retrieved matching state for user {user_id}")
                return state
            
            return None
            
        except Exception as e:
            print(f"[REDIS] Error getting user matching state: {e}")
            return None
    
    async def delete_user_matching_state(self, user_id: str) -> bool:
        """
        Delete user matching state from Redis
        
        Args:
            user_id: User identifier
            
        Returns:
            Success status
        """
        try:
            if not self.is_connected or not self.redis_client:
                # Fallback to in-memory storage
                if hasattr(self, '_fallback_storage'):
                    key = f"matching:{user_id}"
                    if key in self._fallback_storage:
                        del self._fallback_storage[key]
                        print(f"[REDIS] Deleted matching state from memory for user {user_id}")
                return True
            
            key = f"matching:{user_id}"
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.redis_client.delete, key)
            
            print(f"[REDIS] Deleted matching state for user {user_id}: {result}")
            return bool(result)
            
        except Exception as e:
            print(f"[REDIS] Error deleting user matching state: {e}")
            return False
    
    async def set_ai_chatbot_session(self, user_id: str, session_data: Dict[str, Any], ttl: int = 1800) -> bool:
        """
        Set AI chatbot session data in Redis
        
        Args:
            user_id: User identifier
            session_data: Session data
            ttl: Time to live in seconds (default 30 minutes)
            
        Returns:
            Success status
        """
        try:
            if not self.is_connected or not self.redis_client:
                # Fallback to in-memory storage
                if not hasattr(self, '_fallback_storage'):
                    self._fallback_storage = {}
                self._fallback_storage[f"ai_session:{user_id}"] = {
                    'data': session_data,
                    'expires': datetime.utcnow() + timedelta(seconds=ttl)
                }
                print(f"[REDIS] Stored AI session in memory for user {user_id}")
                return True
            
            key = f"ai_session:{user_id}"
            session_json = json.dumps(session_data)
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self.redis_client.setex, 
                key, 
                ttl, 
                session_json
            )
            
            print(f"[REDIS] Stored AI session for user {user_id}: {result}")
            return result
            
        except Exception as e:
            print(f"[REDIS] Error setting AI chatbot session: {e}")
            return False
    
    async def get_ai_chatbot_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get AI chatbot session data from Redis
        
        Args:
            user_id: User identifier
            
        Returns:
            Session data or None
        """
        try:
            if not self.is_connected or not self.redis_client:
                # Fallback to in-memory storage
                if not hasattr(self, '_fallback_storage'):
                    return None
                
                key = f"ai_session:{user_id}"
                if key in self._fallback_storage:
                    entry = self._fallback_storage[key]
                    if datetime.utcnow() < entry['expires']:
                        return entry['data']
                    else:
                        # Expired, remove it
                        del self._fallback_storage[key]
                return None
            
            key = f"ai_session:{user_id}"
            
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self.redis_client.get, key)
            
            if data:
                session = json.loads(data)
                print(f"[REDIS] Retrieved AI session for user {user_id}")
                return session
            
            return None
            
        except Exception as e:
            print(f"[REDIS] Error getting AI chatbot session: {e}")
            return None
    
    async def delete_ai_chatbot_session(self, user_id: str) -> bool:
        """
        Delete AI chatbot session from Redis
        
        Args:
            user_id: User identifier
            
        Returns:
            Success status
        """
        try:
            if not self.is_connected or not self.redis_client:
                # Fallback to in-memory storage
                if hasattr(self, '_fallback_storage'):
                    key = f"ai_session:{user_id}"
                    if key in self._fallback_storage:
                        del self._fallback_storage[key]
                        print(f"[REDIS] Deleted AI session from memory for user {user_id}")
                return True
            
            key = f"ai_session:{user_id}"
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.redis_client.delete, key)
            
            print(f"[REDIS] Deleted AI session for user {user_id}: {result}")
            return bool(result)
            
        except Exception as e:
            print(f"[REDIS] Error deleting AI chatbot session: {e}")
            return False
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions from Redis
        
        Returns:
            Number of sessions cleaned
        """
        try:
            if not self.is_connected or not self.redis_client:
                # Clean up in-memory storage
                if not hasattr(self, '_fallback_storage'):
                    return 0
                
                current_time = datetime.utcnow()
                expired_keys = []
                
                for key, entry in self._fallback_storage.items():
                    if current_time >= entry['expires']:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self._fallback_storage[key]
                
                if expired_keys:
                    print(f"[REDIS] Cleaned {len(expired_keys)} expired sessions from memory")
                return len(expired_keys)
            
            # Redis automatically handles TTL, but we can clean up any orphaned keys
            loop = asyncio.get_event_loop()
            
            # Get all matching and AI session keys
            matching_keys = await loop.run_in_executor(
                None, 
                lambda: self.redis_client.keys("matching:*")
            )
            ai_session_keys = await loop.run_in_executor(
                None, 
                lambda: self.redis_client.keys("ai_session:*")
            )
            
            # Check TTL for each key and delete expired ones
            expired_count = 0
            for key in matching_keys + ai_session_keys:
                ttl = await loop.run_in_executor(None, self.redis_client.ttl, key)
                if ttl == -1:  # Key exists but has no expiration
                    # Set a default expiration if none exists
                    await loop.run_in_executor(None, self.redis_client.expire, key, 300)
                elif ttl == -2:  # Key doesn't exist
                    expired_count += 1
            
            if expired_count > 0:
                print(f"[REDIS] Cleaned {expired_count} expired sessions")
            
            return expired_count
            
        except Exception as e:
            print(f"[REDIS] Error cleaning up expired sessions: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get Redis service statistics
        
        Returns:
            Service statistics
        """
        try:
            if not self.is_connected or not self.redis_client:
                # Return in-memory stats
                if not hasattr(self, '_fallback_storage'):
                    return {
                        'connected': False,
                        'storage_type': 'memory',
                        'total_keys': 0,
                        'matching_sessions': 0,
                        'ai_sessions': 0
                    }
                
                matching_count = sum(1 for key in self._fallback_storage.keys() if key.startswith('matching:'))
                ai_count = sum(1 for key in self._fallback_storage.keys() if key.startswith('ai_session:'))
                
                return {
                    'connected': False,
                    'storage_type': 'memory',
                    'total_keys': len(self._fallback_storage),
                    'matching_sessions': matching_count,
                    'ai_sessions': ai_count
                }
            
            loop = asyncio.get_event_loop()
            
            # Get key counts
            matching_keys = await loop.run_in_executor(
                None, 
                lambda: self.redis_client.keys("matching:*")
            )
            ai_session_keys = await loop.run_in_executor(
                None, 
                lambda: self.redis_client.keys("ai_session:*")
            )
            
            # Get Redis info
            info = await loop.run_in_executor(None, self.redis_client.info)
            
            return {
                'connected': True,
                'storage_type': 'redis',
                'total_keys': len(matching_keys) + len(ai_session_keys),
                'matching_sessions': len(matching_keys),
                'ai_sessions': len(ai_session_keys),
                'redis_info': {
                    'used_memory': info.get('used_memory_human', 'unknown'),
                    'connected_clients': info.get('connected_clients', 0),
                    'uptime_in_seconds': info.get('uptime_in_seconds', 0)
                }
            }
            
        except Exception as e:
            print(f"[REDIS] Error getting stats: {e}")
            return {
                'connected': False,
                'error': str(e)
            }
    
    async def get_active_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get active random chat session for user"""
        try:
            # Check for AI session first
            ai_session = await self.get_ai_chatbot_session(user_id)
            if ai_session:
                return {
                    "sessionId": f"ai_session_{user_id}",
                    "type": "ai",
                    "status": "active",
                    "createdAt": ai_session.get("createdAt"),
                    "personality": ai_session.get("personality")
                }
            
            # Check for matching state
            matching_state = await self.get_user_matching_state(user_id)
            if matching_state and matching_state.get("status") == "matched":
                return {
                    "sessionId": f"human_session_{user_id}",
                    "type": "human",
                    "status": "active",
                    "createdAt": matching_state.get("createdAt"),
                    "partnerId": matching_state.get("partnerId")
                }
            
            return None
            
        except Exception as e:
            print(f"[REDIS] Error getting active session: {e}")
            return None
    
    async def clear_active_session(self, user_id: str) -> bool:
        """Clear active session for user"""
        try:
            # Clear both AI session and matching state
            ai_cleared = await self.delete_ai_chatbot_session(user_id)
            matching_cleared = await self.delete_user_matching_state(user_id)
            
            print(f"[REDIS] Cleared active session for user {user_id}")
            return ai_cleared or matching_cleared
            
        except Exception as e:
            print(f"[REDIS] Error clearing active session: {e}")
            return False
    
    async def end_session(self, session_id: str, reason: str, user_id: str) -> bool:
        """End a session"""
        try:
            if session_id.startswith("ai_session_"):
                return await self.delete_ai_chatbot_session(user_id)
            elif session_id.startswith("human_session_"):
                return await self.delete_user_matching_state(user_id)
            
            return False
            
        except Exception as e:
            print(f"[REDIS] Error ending session: {e}")
            return False


# Global Redis service instance
redis_service = RedisService()
