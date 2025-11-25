"""
Queue Service for User Matching
Handles in-memory queue for matching users in real-time chat
"""

import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from collections import deque
from app.core.config import settings
from app.services.socket_service import socket_service

# Setup logger
logger = logging.getLogger(__name__)


class QueueUser:
    """Represents a user in the matching queue"""
    
    def __init__(self, user_id: str, socket_id: str):
        self.user_id = user_id
        self.socket_id = socket_id
        self.joined_at = datetime.utcnow()
        self.state = "waiting"  # waiting, matched, ai_chat, disconnected
        self.match_partner_id: Optional[str] = None
        self.ai_chat_exchanges = 0
        self.ai_chat_started_at: Optional[datetime] = None
        self.session_id: Optional[str] = None
        self.reconnect_grace_until: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "socket_id": self.socket_id,
            "joined_at": self.joined_at.isoformat(),
            "state": self.state,
            "match_partner_id": self.match_partner_id,
            "ai_chat_exchanges": self.ai_chat_exchanges,
            "ai_chat_started_at": self.ai_chat_started_at.isoformat() if self.ai_chat_started_at else None,
            "session_id": self.session_id,
            "wait_time_seconds": (datetime.utcnow() - self.joined_at).total_seconds()
        }


class QueueService:
    """Service for managing user matching queue"""
    
    def __init__(self):
        self.queue: deque = deque()  # FIFO queue for matching
        self.users: Dict[str, QueueUser] = {}  # user_id -> QueueUser
        self.matched_pairs: Dict[str, str] = {}  # user_id -> partner_id
        self.active_count = 0
        self._matching_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
    
    async def join_queue(self, user_id: str, socket_id: str) -> Dict[str, Any]:
        """
        Add user to matching queue
        
        Args:
            user_id: User identifier
            socket_id: Socket.IO session ID
            
        Returns:
            Queue status
        """
        async with self._lock:
            # Check if user is already in queue
            if user_id in self.users:
                existing_user = self.users[user_id]
                # If reconnecting within grace period, resume
                if existing_user.reconnect_grace_until and datetime.utcnow() < existing_user.reconnect_grace_until:
                    existing_user.socket_id = socket_id
                    existing_user.state = "waiting"
                    existing_user.reconnect_grace_until = None
                    print(f"[QUEUE] User {user_id} reconnected, resuming queue position")
                    return {
                        "success": True,
                        "status": "reconnected",
                        "position": self._get_queue_position(user_id),
                        "wait_time_seconds": (datetime.utcnow() - existing_user.joined_at).total_seconds()
                    }
                else:
                    # Remove old entry
                    await self._remove_user(user_id)
            
            # Create new queue user
            queue_user = QueueUser(user_id, socket_id)
            self.users[user_id] = queue_user
            self.queue.append(user_id)
            
            self.active_count = len(self.queue) + len(self.matched_pairs)
            
            logger.info("User joined queue", extra={
                "user_id": user_id,
                "position": len(self.queue),
                "queue_size": len(self.queue),
                "active_count": self.active_count
            })
            print(f"[QUEUE] User {user_id} joined queue (position: {len(self.queue)})")
            
            return {
                "success": True,
                "status": "joined",
                "position": len(self.queue),
                "wait_time_seconds": 0
            }
    
    async def leave_queue(self, user_id: str) -> Dict[str, Any]:
        """
        Remove user from queue
        
        Args:
            user_id: User identifier
            
        Returns:
            Success status
        """
        async with self._lock:
            return await self._remove_user(user_id)
    
    async def _remove_user(self, user_id: str) -> Dict[str, Any]:
        """Internal method to remove user from queue"""
        if user_id not in self.users:
            return {"success": False, "error": "User not in queue"}
        
        queue_user = self.users[user_id]
        
        # Remove from queue if waiting
        if queue_user.state == "waiting" and user_id in self.queue:
            try:
                self.queue.remove(user_id)
            except ValueError:
                pass
        
        # Remove from matched pairs if matched
        if user_id in self.matched_pairs:
            partner_id = self.matched_pairs[user_id]
            if partner_id in self.matched_pairs:
                del self.matched_pairs[partner_id]
            del self.matched_pairs[user_id]
        
        # Remove from users dict
        del self.users[user_id]
        
        self.active_count = len(self.queue) + len(self.matched_pairs)
        
        logger.info("User removed from queue", extra={
            "user_id": user_id,
            "queue_size": len(self.queue),
            "active_count": self.active_count
        })
        print(f"[QUEUE] User {user_id} removed from queue")
        return {"success": True}
    
    async def get_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get queue status for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Queue status
        """
        if user_id not in self.users:
            return {
                "success": False,
                "error": "User not in queue"
            }
        
        queue_user = self.users[user_id]
        position = self._get_queue_position(user_id) if queue_user.state == "waiting" else None
        
        return {
            "success": True,
            "state": queue_user.state,
            "position": position,
            "wait_time_seconds": (datetime.utcnow() - queue_user.joined_at).total_seconds(),
            "ai_chat_exchanges": queue_user.ai_chat_exchanges,
            "match_partner_id": queue_user.match_partner_id,
            "session_id": queue_user.session_id
        }
    
    def _get_queue_position(self, user_id: str) -> int:
        """Get user's position in queue"""
        try:
            return list(self.queue).index(user_id) + 1
        except ValueError:
            return 0
    
    async def match_users(self) -> Optional[Dict[str, Any]]:
        """
        Try to match two users from queue
        
        Returns:
            Match result or None
        """
        async with self._lock:
            if len(self.queue) < 2:
                return None
            
            # Get two users from queue
            user1_id = self.queue.popleft()
            user2_id = self.queue.popleft()
            
            if user1_id not in self.users or user2_id not in self.users:
                # Put back if users no longer exist
                if user1_id in self.users:
                    self.queue.appendleft(user1_id)
                if user2_id in self.users:
                    self.queue.appendleft(user2_id)
                return None
            
            user1 = self.users[user1_id]
            user2 = self.users[user2_id]
            
            # Create match
            session_id = str(uuid.uuid4())
            user1.state = "matched"
            user2.state = "matched"
            user1.match_partner_id = user2_id
            user2.match_partner_id = user1_id
            user1.session_id = session_id
            user2.session_id = session_id
            
            self.matched_pairs[user1_id] = user2_id
            self.matched_pairs[user2_id] = user1_id
            
            self.active_count = len(self.queue) + len(self.matched_pairs)
            
            wait_time_1 = (datetime.utcnow() - user1.joined_at).total_seconds()
            wait_time_2 = (datetime.utcnow() - user2.joined_at).total_seconds()
            
            logger.info("Users matched", extra={
                "user1_id": user1_id,
                "user2_id": user2_id,
                "session_id": session_id,
                "user1_wait_time": wait_time_1,
                "user2_wait_time": wait_time_2,
                "queue_size": len(self.queue),
                "active_count": self.active_count
            })
            print(f"[QUEUE] Matched users {user1_id} and {user2_id} (session: {session_id})")
            
            return {
                "user1_id": user1_id,
                "user2_id": user2_id,
                "session_id": session_id,
                "matched_at": datetime.utcnow().isoformat()
            }
    
    async def check_timeout(self, user_id: str) -> bool:
        """
        Check if user has exceeded timeout
        
        Args:
            user_id: User identifier
            
        Returns:
            True if timeout exceeded
        """
        if user_id not in self.users:
            return False
        
        queue_user = self.users[user_id]
        if queue_user.state != "waiting":
            return False
        
        wait_time = (datetime.utcnow() - queue_user.joined_at).total_seconds()
        return wait_time >= settings.QUEUE_TIMEOUT_SECONDS
    
    async def start_ai_chat(self, user_id: str) -> Dict[str, Any]:
        """
        Start AI chat for user (timeout reached)
        
        Args:
            user_id: User identifier
            
        Returns:
            AI chat status
        """
        async with self._lock:
            if user_id not in self.users:
                return {"success": False, "error": "User not in queue"}
            
            queue_user = self.users[user_id]
            if queue_user.state != "waiting":
                return {"success": False, "error": "User not waiting"}
            
            # Remove from queue
            if user_id in self.queue:
                try:
                    self.queue.remove(user_id)
                except ValueError:
                    pass
            
            # Update state
            queue_user.state = "ai_chat"
            queue_user.ai_chat_started_at = datetime.utcnow()
            queue_user.ai_chat_exchanges = 0
            
            self.active_count = len(self.queue) + len(self.matched_pairs)
            
            wait_time = (datetime.utcnow() - queue_user.joined_at).total_seconds()
            
            logger.info("AI chat started (timeout)", extra={
                "user_id": user_id,
                "wait_time_seconds": wait_time,
                "timeout_seconds": settings.QUEUE_TIMEOUT_SECONDS,
                "queue_size": len(self.queue),
                "active_count": self.active_count
            })
            print(f"[QUEUE] Started AI chat for user {user_id}")
            
            return {
                "success": True,
                "user_id": user_id,
                "ai_chat_started_at": queue_user.ai_chat_started_at.isoformat()
            }
    
    async def increment_ai_exchanges(self, user_id: str) -> Dict[str, Any]:
        """
        Increment AI chat exchange count
        
        Args:
            user_id: User identifier
            
        Returns:
            Updated status
        """
        if user_id not in self.users:
            return {"success": False, "error": "User not found"}
        
        queue_user = self.users[user_id]
        queue_user.ai_chat_exchanges += 1
        
        return {
            "success": True,
            "exchanges": queue_user.ai_chat_exchanges,
            "max_exchanges": settings.AI_CHAT_MAX_EXCHANGES
        }
    
    async def should_end_ai_chat(self, user_id: str) -> bool:
        """
        Check if AI chat should end (max exchanges or time limit)
        
        Args:
            user_id: User identifier
            
        Returns:
            True if should end
        """
        if user_id not in self.users:
            return False
        
        queue_user = self.users[user_id]
        if queue_user.state != "ai_chat":
            return False
        
        # Check exchange limit
        if queue_user.ai_chat_exchanges >= settings.AI_CHAT_MAX_EXCHANGES:
            return True
        
        # Check time limit
        if queue_user.ai_chat_started_at:
            duration = (datetime.utcnow() - queue_user.ai_chat_started_at).total_seconds()
            if duration >= settings.AI_CHAT_MAX_DURATION_SECONDS:
                return True
        
        return False
    
    async def end_ai_chat_and_requeue(self, user_id: str) -> Dict[str, Any]:
        """
        End AI chat and requeue user
        
        Args:
            user_id: User identifier
            
        Returns:
            Requeue status
        """
        async with self._lock:
            if user_id not in self.users:
                return {"success": False, "error": "User not found"}
            
            queue_user = self.users[user_id]
            if queue_user.state != "ai_chat":
                return {"success": False, "error": "User not in AI chat"}
            
            # Reset for requeue
            queue_user.state = "waiting"
            queue_user.ai_chat_exchanges = 0
            queue_user.ai_chat_started_at = None
            queue_user.joined_at = datetime.utcnow()  # Reset join time
            
            # Add back to queue
            self.queue.append(user_id)
            
            self.active_count = len(self.queue) + len(self.matched_pairs)
            
            logger.info("User requeued after AI chat", extra={
                "user_id": user_id,
                "ai_chat_exchanges": queue_user.ai_chat_exchanges,
                "position": len(self.queue),
                "queue_size": len(self.queue),
                "active_count": self.active_count
            })
            print(f"[QUEUE] User {user_id} requeued after AI chat")
            
            return {
                "success": True,
                "position": len(self.queue),
                "wait_time_seconds": 0
            }
    
    async def handle_disconnect(self, user_id: str) -> Dict[str, Any]:
        """
        Handle user disconnection (set grace period for reconnect)
        
        Args:
            user_id: User identifier
            
        Returns:
            Disconnect status
        """
        async with self._lock:
            if user_id not in self.users:
                return {"success": False, "error": "User not found"}
            
            queue_user = self.users[user_id]
            
            # Set reconnect grace period
            queue_user.reconnect_grace_until = datetime.utcnow() + timedelta(
                seconds=settings.RECONNECT_GRACE_PERIOD_SECONDS
            )
            queue_user.state = "disconnected"
            
            # Remove from queue but keep in users dict
            if user_id in self.queue:
                try:
                    self.queue.remove(user_id)
                except ValueError:
                    pass
            
            # If matched, notify partner
            if user_id in self.matched_pairs:
                partner_id = self.matched_pairs[user_id]
                if partner_id in self.users:
                    # Partner can continue or be notified
                    pass
            
            self.active_count = len(self.queue) + len(self.matched_pairs)
            
            logger.info("User disconnected", extra={
                "user_id": user_id,
                "grace_period_seconds": settings.RECONNECT_GRACE_PERIOD_SECONDS,
                "queue_size": len(self.queue),
                "active_count": self.active_count
            })
            print(f"[QUEUE] User {user_id} disconnected (grace period: {settings.RECONNECT_GRACE_PERIOD_SECONDS}s)")
            
            return {"success": True}
    
    async def cleanup_stale_reconnects(self) -> int:
        """
        Clean up users who didn't reconnect within grace period
        
        Returns:
            Number of users cleaned up
        """
        async with self._lock:
            current_time = datetime.utcnow()
            stale_users = []
            
            for user_id, queue_user in self.users.items():
                if (queue_user.state == "disconnected" and 
                    queue_user.reconnect_grace_until and 
                    current_time >= queue_user.reconnect_grace_until):
                    stale_users.append(user_id)
            
            for user_id in stale_users:
                await self._remove_user(user_id)
                logger.info("Cleaned up stale reconnect", extra={
                    "user_id": user_id,
                    "grace_period_seconds": settings.RECONNECT_GRACE_PERIOD_SECONDS
                })
                print(f"[QUEUE] Cleaned up stale reconnect for user {user_id}")
            
            if stale_users:
                logger.info("Stale reconnects cleanup completed", extra={
                    "cleaned_count": len(stale_users),
                    "remaining_users": len(self.users)
                })
            
            return len(stale_users)
    
    def get_active_count(self) -> int:
        """Get active user count (in queue + matched)"""
        return self.active_count
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return len(self.queue)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            "queue_size": len(self.queue),
            "active_count": self.active_count,
            "matched_pairs": len(self.matched_pairs) // 2,
            "total_users": len(self.users),
            "waiting": sum(1 for u in self.users.values() if u.state == "waiting"),
            "matched": sum(1 for u in self.users.values() if u.state == "matched"),
            "ai_chat": sum(1 for u in self.users.values() if u.state == "ai_chat"),
            "disconnected": sum(1 for u in self.users.values() if u.state == "disconnected")
        }


# Global queue service instance
queue_service = QueueService()

