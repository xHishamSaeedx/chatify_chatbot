"""
Chatify Chatbot
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.api.v1.api import api_router
from app.services.firebase_service import firebase_service
from app.services.session_service import session_service


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    # Set up CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
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
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    
    # Setup background cleanup scheduler
    setup_background_jobs(app)
    
    return app


def setup_background_jobs(app: FastAPI):
    """Setup background jobs for automatic cleanup"""
    scheduler = AsyncIOScheduler()
    
    @app.on_event("startup")
    async def start_scheduler():
        """Start background cleanup job when application starts"""
        print("🔧 Setting up background cleanup jobs...")
        
        # Schedule session cleanup every 10 minutes
        scheduler.add_job(
            session_service.cleanup_expired_sessions,
            'interval',
            minutes=10,
            id='cleanup_expired_sessions',
            name='Cleanup expired chatbot sessions',
            replace_existing=True
        )
        
        scheduler.start()
        print("✅ Background cleanup job started - runs every 10 minutes")
        print(f"   📊 Current active sessions: {session_service.get_active_sessions_count()}")
    
    @app.on_event("shutdown")
    async def shutdown_scheduler():
        """Shutdown scheduler gracefully when application stops"""
        print("🔄 Shutting down background jobs...")
        scheduler.shutdown(wait=False)
        print("✅ Background jobs stopped")


app = create_application()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.PROJECT_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
