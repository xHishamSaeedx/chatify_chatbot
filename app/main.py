"""
Chatify Chatbot
Main application entry point
"""

import socketio
import asyncio
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.api.v1.api import api_router
from app.services.firebase_service import firebase_service
from app.services.session_service import session_service
from app.services.redis_service import redis_service
from app.services.chatbot_fallback_service import chatbot_fallback_service
from app.services.socket_service import socket_service
from app.services.queue_service import queue_service
from app.services.ad_service import ad_service
from app.core.config import settings


def create_fastapi_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    fastapi_app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    # Set up CORS
    if settings.BACKEND_CORS_ORIGINS:
        fastapi_app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Initialize Firebase
    try:
        firebase_service.initialize()
        print("Firebase service initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Firebase: {str(e)}")
    
    # Include API router
    fastapi_app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Mount static files
    fastapi_app.mount("/static", StaticFiles(directory="app/static"), name="static")
    
    # Setup background cleanup scheduler
    setup_background_jobs(fastapi_app)
    
    # Setup startup event for async initialization
    @fastapi_app.on_event("startup")
    async def startup_event():
        """Initialize services on startup"""
        try:
            await redis_service.initialize()
            print("Redis service initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Redis: {str(e)}")
        
        try:
            await socket_service.initialize()
            print("Socket.IO service initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Socket.IO: {str(e)}")
    
    return fastapi_app


async def queue_matching_loop():
    """Continuous loop for matching users in queue"""
    print("[QUEUE] Starting queue matching loop...")
    while True:
        try:
            # Batch matching every 0.5-1s
            await asyncio.sleep(settings.QUEUE_BATCH_INTERVAL_SECONDS)
            
            # Try to match users
            match_result = await queue_service.match_users()
            
            if match_result:
                user1_id = match_result["user1_id"]
                user2_id = match_result["user2_id"]
                session_id = match_result["session_id"]
                
                # Get socket IDs
                user1_socket = queue_service.users[user1_id].socket_id if user1_id in queue_service.users else None
                user2_socket = queue_service.users[user2_id].socket_id if user2_id in queue_service.users else None
                
                # Emit match events
                if user1_socket:
                    await socket_service.sio.emit("queue_matched", {
                        "session_id": session_id,
                        "partner_id": user2_id,
                        "matched_at": match_result["matched_at"]
                    }, room=user1_socket)
                
                if user2_socket:
                    await socket_service.sio.emit("queue_matched", {
                        "session_id": session_id,
                        "partner_id": user1_id,
                        "matched_at": match_result["matched_at"]
                    }, room=user2_socket)
                
                print(f"[QUEUE] Matched {user1_id} and {user2_id} (session: {session_id})")
                
        except Exception as e:
            print(f"[QUEUE] Error in matching loop: {e}")
            await asyncio.sleep(1)


async def ad_rotation_task():
    """Send ads to waiting users every 10s"""
    print("[AD] Starting ad rotation task...")
    while True:
        try:
            await asyncio.sleep(settings.AD_ROTATION_INTERVAL_SECONDS)
            
            # Get waiting users
            waiting_users = [
                (user_id, queue_user.socket_id)
                for user_id, queue_user in queue_service.users.items()
                if queue_user.state == "waiting"
            ]
            
            if waiting_users:
                ad = ad_service.get_next_ad()
                
                # Send ad to all waiting users
                for user_id, socket_id in waiting_users:
                    try:
                        await socket_service.sio.emit("queue_ad", ad, room=socket_id)
                    except Exception as e:
                        print(f"[AD] Error sending ad to {user_id}: {e}")
                
                print(f"[AD] Sent ad to {len(waiting_users)} waiting users")
                
        except Exception as e:
            print(f"[AD] Error in ad rotation task: {e}")
            await asyncio.sleep(1)


async def active_count_update_task():
    """Broadcast active count updates every 5s"""
    print("[QUEUE] Starting active count update task...")
    last_count = 0
    
    while True:
        try:
            await asyncio.sleep(settings.ACTIVE_COUNT_UPDATE_INTERVAL_SECONDS)
            
            current_count = queue_service.get_active_count()
            
            # Only broadcast if count changed
            if current_count != last_count:
                await socket_service.sio.emit("active_count_update", {
                    "active_count": current_count,
                    "timestamp": datetime.utcnow().isoformat()
                })
                last_count = current_count
                print(f"[QUEUE] Active count updated: {current_count}")
                
        except Exception as e:
            print(f"[QUEUE] Error in active count update task: {e}")
            await asyncio.sleep(1)


async def timeout_check_task():
    """Check for users who exceeded timeout and trigger AI fallback, and check AI chats that should end"""
    print("[QUEUE] Starting timeout check task...")
    while True:
        try:
            await asyncio.sleep(1)  # Check every second
            
            # Check all users
            for user_id, queue_user in list(queue_service.users.items()):
                if queue_user.state == "waiting":
                    # Check timeout
                    if await queue_service.check_timeout(user_id):
                        print(f"[QUEUE] Timeout reached for user {user_id}, starting AI chat")
                        
                        # Start AI chat
                        ai_start_result = await queue_service.start_ai_chat(user_id)
                        
                        if ai_start_result.get("success"):
                            # Create AI session
                            socket_id = queue_user.socket_id
                            ai_session = await chatbot_fallback_service.create_ai_chat_from_queue(
                                user_id, socket_id
                            )
                            
                            if ai_session:
                                # Update queue user with session ID
                                if user_id in queue_service.users:
                                    queue_service.users[user_id].session_id = ai_session["session_id"]
                                
                                # Emit timeout and AI chat started events
                                await socket_service.sio.emit("queue_timeout", {
                                    "message": "No match found, switching to AI chat",
                                    "timeout_seconds": settings.QUEUE_TIMEOUT_SECONDS
                                }, room=socket_id)
                                
                                await socket_service.sio.emit("ai_chat_started", {
                                    "session_id": ai_session["session_id"],
                                    "ai_user_id": ai_session["ai_user_id"],
                                    "personality": ai_session["personality"],
                                    "ai_user_profile": ai_session.get("ai_user_profile", {}),
                                    "chatbot_session_id": ai_session.get("chatbot_session_id")
                                }, room=socket_id)
                                
                                print(f"[QUEUE] AI chat started for user {user_id}, session: {ai_session['session_id']}")
                
                elif queue_user.state == "ai_chat":
                    # Check if AI chat should end
                    if await queue_service.should_end_ai_chat(user_id):
                        print(f"[QUEUE] AI chat limit reached for user {user_id}, requeuing")
                        
                        # End AI session and requeue
                        await chatbot_fallback_service.end_ai_session(user_id)
                        requeue_result = await queue_service.end_ai_chat_and_requeue(user_id)
                        
                        if requeue_result.get("success"):
                            socket_id = queue_user.socket_id
                            
                            await socket_service.sio.emit("ai_chat_ended", {
                                "requeued": True,
                                "position": requeue_result.get("position"),
                                "wait_time_seconds": requeue_result.get("wait_time_seconds", 0)
                            }, room=socket_id)
                            
                            await socket_service.sio.emit("queue_joined", {
                                "status": "requeued",
                                "position": requeue_result.get("position"),
                                "wait_time_seconds": requeue_result.get("wait_time_seconds", 0)
                            }, room=socket_id)
                            
                            print(f"[QUEUE] User {user_id} requeued after AI chat")
                
        except Exception as e:
            print(f"[QUEUE] Error in timeout check task: {e}")
            await asyncio.sleep(1)


def setup_background_jobs(app: FastAPI):
    """Setup background jobs for automatic cleanup"""
    scheduler = AsyncIOScheduler()
    
    @app.on_event("startup")
    async def start_scheduler():
        """Start background cleanup job when application starts"""
        print("[SETUP] Setting up background cleanup jobs...")
        
        # Schedule session cleanup every 10 minutes
        scheduler.add_job(
            session_service.cleanup_expired_sessions,
            'interval',
            minutes=10,
            id='cleanup_expired_sessions',
            name='Cleanup expired chatbot sessions',
            replace_existing=True
        )
        
        # Schedule Redis cleanup every 5 minutes
        scheduler.add_job(
            redis_service.cleanup_expired_sessions,
            'interval',
            minutes=5,
            id='cleanup_redis_sessions',
            name='Cleanup expired Redis sessions',
            replace_existing=True
        )
        
        # Schedule AI fallback cleanup every 15 minutes
        scheduler.add_job(
            chatbot_fallback_service.cleanup_expired_sessions,
            'interval',
            minutes=15,
            id='cleanup_ai_sessions',
            name='Cleanup expired AI sessions',
            replace_existing=True
        )
        
        # Schedule queue cleanup (stale reconnects) every minute
        scheduler.add_job(
            queue_service.cleanup_stale_reconnects,
            'interval',
            minutes=1,
            id='cleanup_stale_reconnects',
            name='Cleanup stale queue reconnects',
            replace_existing=True
        )
        
        scheduler.start()
        print("[OK] Background cleanup job started - runs every 10 minutes")
        print(f"   [INFO] Current active sessions: {session_service.get_active_sessions_count()}")
        
        # Start queue background tasks
        asyncio.create_task(queue_matching_loop())
        asyncio.create_task(ad_rotation_task())
        asyncio.create_task(active_count_update_task())
        asyncio.create_task(timeout_check_task())
        print("[OK] Queue background tasks started")
    
    @app.on_event("shutdown")
    async def shutdown_scheduler():
        """Shutdown scheduler gracefully when application stops"""
        print("[SHUTDOWN] Shutting down background jobs...")
        scheduler.shutdown(wait=False)
        print("[OK] Background jobs stopped")


# Create FastAPI app
fastapi_app = create_fastapi_app()


@fastapi_app.get("/")
@fastapi_app.head("/")
async def root():
    """Root endpoint - supports GET and HEAD methods for health checks"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@fastapi_app.get("/health")
@fastapi_app.head("/health")
async def health_check():
    """Health check endpoint - supports GET and HEAD methods"""
    return {"status": "healthy", "service": settings.PROJECT_NAME}


@fastapi_app.websocket("/ws/keepalive")
async def keepalive_websocket(websocket):
    """
    WebSocket endpoint to maintain persistent connection
    Prevents Render from shutting down the service due to inactivity
    """
    from fastapi import WebSocket, WebSocketDisconnect
    import asyncio
    from datetime import datetime
    
    await websocket.accept()
    print("🔌 [KEEP-ALIVE] WebSocket connected - service will stay alive")
    
    try:
        while True:
            # Send ping every 30 seconds to maintain connection
            await websocket.send_json({
                "type": "ping",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "alive",
                "service": settings.PROJECT_NAME
            })
            print("💓 [KEEP-ALIVE] Heartbeat sent")
            await asyncio.sleep(30)
            
            # Try to receive pong (non-blocking)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                print(f"📥 [KEEP-ALIVE] Pong received: {data}")
            except asyncio.TimeoutError:
                pass  # No pong received, continue anyway
                
    except WebSocketDisconnect:
        print("🔌 [KEEP-ALIVE] WebSocket disconnected")
    except Exception as e:
        print(f"❌ [KEEP-ALIVE] WebSocket error: {e}")


# Wrap FastAPI app with Socket.IO for WebSocket support
app = socketio.ASGIApp(socket_service.sio, other_asgi_app=fastapi_app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.get_host,
        port=settings.get_port,
        reload=True
    )
