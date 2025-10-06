"""
Main API router
"""

from fastapi import APIRouter
from app.api.v1.endpoints import firebase, chat, chatbot, personality, settings, analytics, chatbot_fallback, auth, profiles, connections

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(firebase.router, prefix="/firebase", tags=["firebase"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
api_router.include_router(personality.router, prefix="/personalities", tags=["personalities"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(chatbot_fallback.router, prefix="/ai-fallback", tags=["ai-fallback"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(connections.router, prefix="/connections", tags=["connections"])


@api_router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Chatify Chatbot API"}


@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
