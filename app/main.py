"""
Chatify Chatbot
Main application entry point
"""

import socketio
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
        
        scheduler.start()
        print("[OK] Background cleanup job started - runs every 10 minutes")
        print(f"   [INFO] Current active sessions: {session_service.get_active_sessions_count()}")
    
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
