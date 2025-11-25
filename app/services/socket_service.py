"""
Socket.IO service for real-time communication
"""

import socketio
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.config import settings

class SocketService:
    def __init__(self):
        self.sio = socketio.AsyncServer(
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True,
            async_mode='asgi'
        )
        self.app = socketio.ASGIApp(self.sio)
        self.connected_users: Dict[str, str] = {}  # user_id -> session_id mapping
        self.user_sessions: Dict[str, str] = {}  # session_id -> user_id mapping
        
    async def initialize(self):
        """Initialize Socket.IO event handlers"""
        print("[SOCKET] Initializing Socket.IO service...")
        
        @self.sio.event
        async def connect(sid, environ, auth):
            """Handle client connection"""
            print(f"[SOCKET] Client connected: {sid}")
            return True
        
        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection"""
            print(f"[SOCKET] Client disconnected: {sid}")
            
            # Clean up user mapping if exists
            if sid in self.user_sessions:
                user_id = self.user_sessions[sid]
                del self.user_sessions[sid]
                if user_id in self.connected_users:
                    del self.connected_users[user_id]
                
                # Handle queue disconnection
                try:
                    from app.services.queue_service import queue_service
                    await queue_service.handle_disconnect(user_id)
                except Exception as e:
                    print(f"[SOCKET] Error handling queue disconnect: {e}")
                
                print(f"[SOCKET] Cleaned up user mapping for {user_id}")
        
        @self.sio.event
        async def join_chat(sid, data):
            """Handle joining a chat room"""
            try:
                chat_room_id = data.get('chatRoomId')
                user_id = data.get('userId')
                
                if not chat_room_id:
                    await self.sio.emit('error', {'message': 'Chat room ID required'}, room=sid)
                    return
                
                # Join the room
                await self.sio.enter_room(sid, chat_room_id)
                
                # Store user mapping
                if user_id:
                    self.connected_users[user_id] = sid
                    self.user_sessions[sid] = user_id
                
                print(f"[SOCKET] User {user_id} joined chat room: {chat_room_id}")
                await self.sio.emit('joined_chat', {'chatRoomId': chat_room_id}, room=sid)
                
            except Exception as e:
                print(f"[SOCKET] Error in join_chat: {e}")
                await self.sio.emit('error', {'message': str(e)}, room=sid)
        
        @self.sio.event
        async def leave_chat(sid, data):
            """Handle leaving a chat room"""
            try:
                chat_room_id = data.get('chatRoomId')
                if chat_room_id:
                    await self.sio.leave_room(sid, chat_room_id)
                    print(f"[SOCKET] User left chat room: {chat_room_id}")
                    await self.sio.emit('left_chat', {'chatRoomId': chat_room_id}, room=sid)
            except Exception as e:
                print(f"[SOCKET] Error in leave_chat: {e}")
                await self.sio.emit('error', {'message': str(e)}, room=sid)
        
        @self.sio.event
        async def send_message(sid, data):
            """Handle sending a message"""
            try:
                chat_room_id = data.get('chatRoomId')
                message = data.get('message')
                user_id = data.get('userId')
                
                if not all([chat_room_id, message, user_id]):
                    await self.sio.emit('error', {'message': 'Missing required fields'}, room=sid)
                    return
                
                # Create message object
                message_data = {
                    'id': f'msg_{datetime.now().timestamp()}',
                    'content': message,
                    'senderId': user_id,
                    'timestamp': datetime.now().isoformat(),
                    'chatRoomId': chat_room_id
                }
                
                # Broadcast to room
                await self.sio.emit('new_message', message_data, room=chat_room_id)
                print(f"[SOCKET] Message sent in room {chat_room_id} by user {user_id}")
                
            except Exception as e:
                print(f"[SOCKET] Error in send_message: {e}")
                await self.sio.emit('error', {'message': str(e)}, room=sid)
        
        @self.sio.event
        async def start_random_connection(sid, data):
            """Handle starting random connection"""
            try:
                user_id = data.get('userId')
                if user_id:
                    self.connected_users[user_id] = sid
                    self.user_sessions[sid] = user_id
                    print(f"[SOCKET] User {user_id} started random connection")
                    await self.sio.emit('random_connection_started', {'userId': user_id}, room=sid)
            except Exception as e:
                print(f"[SOCKET] Error in start_random_connection: {e}")
                await self.sio.emit('error', {'message': str(e)}, room=sid)
        
        @self.sio.event
        async def stop_random_connection(sid, data):
            """Handle stopping random connection"""
            try:
                user_id = data.get('userId')
                if user_id and user_id in self.connected_users:
                    del self.connected_users[user_id]
                if sid in self.user_sessions:
                    del self.user_sessions[sid]
                print(f"[SOCKET] User {user_id} stopped random connection")
                await self.sio.emit('random_connection_stopped', {'userId': user_id}, room=sid)
            except Exception as e:
                print(f"[SOCKET] Error in stop_random_connection: {e}")
                await self.sio.emit('error', {'message': str(e)}, room=sid)
        
        @self.sio.event
        async def end_random_chat_session(sid, data):
            """Handle ending random chat session"""
            try:
                session_id = data.get('sessionId')
                reason = data.get('reason', 'User ended session')
                user_id = data.get('userId')
                
                if session_id:
                    # Broadcast session end to all clients in the session
                    await self.sio.emit('random_chat_session_ended', {
                        'sessionId': session_id,
                        'reason': reason,
                        'endedBy': user_id
                    }, room=f'session_{session_id}')
                    print(f"[SOCKET] Random chat session ended: {session_id}")
            except Exception as e:
                print(f"[SOCKET] Error in end_random_chat_session: {e}")
                await self.sio.emit('error', {'message': str(e)}, room=sid)
        
        # Queue-related socket events are handled by queue service and background tasks
        # Events emitted: queue_joined, queue_matched, queue_timeout, queue_ad, 
        # queue_status, ai_chat_started, ai_chat_ended, active_count_update
        
        print("[SOCKET] Socket.IO service initialized successfully")
    
    async def send_to_user(self, user_id: str, event: str, data: Any):
        """Send data to a specific user"""
        if user_id in self.connected_users:
            session_id = self.connected_users[user_id]
            await self.sio.emit(event, data, room=session_id)
            return True
        return False
    
    async def send_to_room(self, room_id: str, event: str, data: Any):
        """Send data to all users in a room"""
        await self.sio.emit(event, data, room=room_id)
    
    def get_connected_users_count(self) -> int:
        """Get count of connected users"""
        return len(self.connected_users)
    
    def is_user_connected(self, user_id: str) -> bool:
        """Check if a user is connected"""
        return user_id in self.connected_users

# Global socket service instance
socket_service = SocketService()
