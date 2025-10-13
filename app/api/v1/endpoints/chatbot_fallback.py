"""
AI Chatbot Fallback API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.services.chatbot_fallback_service import chatbot_fallback_service
from app.services.redis_service import redis_service
from app.services.analytics_service import analytics_service

router = APIRouter()


class MatchingStateRequest(BaseModel):
    """Request model for setting user matching state"""
    user_id: str
    preferences: Dict[str, Any] = {}
    start_time: Optional[str] = None


class AIFallbackCheckRequest(BaseModel):
    """Request model for checking AI fallback"""
    user_id: str


class AIMessageRequest(BaseModel):
    """Request model for sending message to AI"""
    user_id: str
    message: str


class AIFallbackResponse(BaseModel):
    """Response model for AI fallback"""
    success: bool
    is_ai_match: bool = False
    session_data: Optional[Dict[str, Any]] = None
    ai_user_profile: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/set-matching-state")
async def set_matching_state(request: MatchingStateRequest) -> Dict[str, Any]:
    """
    Set user matching state in Redis
    
    This endpoint is called when a user starts matching to track their state
    """
    try:
        from datetime import datetime
        
        # Prepare matching state data
        state_data = {
            "user_id": request.user_id,
            "preferences": request.preferences,
            "start_time": request.start_time or datetime.utcnow().isoformat(),
            "status": "matching",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store in Redis
        success = await redis_service.set_user_matching_state(
            request.user_id, 
            state_data, 
            ttl=300  # 5 minutes TTL
        )
        
        if success:
            print(f"[API] Set matching state for user {request.user_id}")
            return {
                "success": True,
                "message": "Matching state set successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to set matching state")
            
    except Exception as e:
        print(f"[API] Error setting matching state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-ai-fallback", response_model=AIFallbackResponse)
async def check_ai_fallback(request: AIFallbackCheckRequest) -> AIFallbackResponse:
    """
    Check if user should be matched with AI chatbot
    
    This endpoint is called periodically to check if the user has been waiting
    long enough to trigger AI fallback
    """
    try:
        # Check for AI fallback
        ai_session_data = await chatbot_fallback_service.check_for_ai_fallback(request.user_id)
        
        if ai_session_data:
            print(f"[API] AI fallback triggered for user {request.user_id}")
            
            # Track analytics
            analytics_service.track_ai_fallback_triggered(
                user_id=request.user_id,
                wait_time=chatbot_fallback_service.matching_timeout,
                personality=ai_session_data.get("personality")
            )
            
            return AIFallbackResponse(
                success=True,
                is_ai_match=True,
                session_data=ai_session_data,
                ai_user_profile=ai_session_data.get("ai_user_profile")
            )
        else:
            return AIFallbackResponse(
                success=True,
                is_ai_match=False,
                session_data=None,
                ai_user_profile=None
            )
            
    except Exception as e:
        print(f"[API] Error checking AI fallback: {e}")
        return AIFallbackResponse(
            success=False,
            is_ai_match=False,
            error=str(e)
        )


@router.get("/ai-session/{user_id}")
async def get_ai_session(user_id: str) -> Dict[str, Any]:
    """
    Get AI session data for user
    
    This endpoint returns the current AI session data if the user is in an AI chat
    """
    try:
        session_data = await chatbot_fallback_service.get_ai_session(user_id)
        
        if session_data:
            return {
                "success": True,
                "session_data": session_data
            }
        else:
            return {
                "success": False,
                "message": "No AI session found"
            }
            
    except Exception as e:
        print(f"[API] Error getting AI session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-ai-message")
async def send_ai_message(request: AIMessageRequest) -> Dict[str, Any]:
    """
    Send message to AI chatbot
    
    This endpoint handles messages sent to AI chatbots
    """
    try:
        response = await chatbot_fallback_service.send_ai_message(
            request.user_id, 
            request.message
        )
        
        if response and response.get("success"):
            return {
                "success": True,
                "message": response["message"],
                "ai_user_id": response["ai_user_id"],
                "session_id": response["session_id"]
            }
        else:
            return {
                "success": False,
                "error": "Failed to send message to AI"
            }
            
    except Exception as e:
        print(f"[API] Error sending AI message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/end-ai-session/{user_id}")
@router.post("/end-ai-session/{user_id}")
async def end_ai_session(user_id: str) -> Dict[str, Any]:
    """
    End AI session for user
    
    This endpoint ends the AI chatbot session
    """
    try:
        success = await chatbot_fallback_service.end_ai_session(user_id)
        
        if success:
            return {
                "success": True,
                "message": "AI session ended successfully"
            }
        else:
            return {
                "success": False,
                "error": "Failed to end AI session"
            }
            
    except Exception as e:
        print(f"[API] Error ending AI session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear-matching-state/{user_id}")
async def clear_matching_state(user_id: str) -> Dict[str, Any]:
    """
    Clear user matching state
    
    This endpoint clears the user's matching state from Redis
    """
    try:
        success = await redis_service.delete_user_matching_state(user_id)
        
        if success:
            return {
                "success": True,
                "message": "Matching state cleared successfully"
            }
        else:
            return {
                "success": False,
                "error": "Failed to clear matching state"
            }
            
    except Exception as e:
        print(f"[API] Error clearing matching state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_fallback_stats() -> Dict[str, Any]:
    """
    Get AI fallback service statistics
    
    This endpoint returns statistics about the AI fallback service
    """
    try:
        fallback_stats = chatbot_fallback_service.get_stats()
        redis_stats = await redis_service.get_stats()
        
        return {
            "success": True,
            "fallback_service": fallback_stats,
            "redis_service": redis_stats
        }
        
    except Exception as e:
        print(f"[API] Error getting fallback stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/configure-timeout")
async def configure_timeout(timeout_seconds: int) -> Dict[str, Any]:
    """
    Configure AI fallback timeout
    
    This endpoint allows configuring the timeout for AI fallback
    """
    try:
        if timeout_seconds < 5 or timeout_seconds > 300:  # 5 seconds to 5 minutes
            raise HTTPException(
                status_code=400, 
                detail="Timeout must be between 5 and 300 seconds"
            )
        
        chatbot_fallback_service.set_matching_timeout(timeout_seconds)
        
        return {
            "success": True,
            "message": f"Timeout set to {timeout_seconds} seconds",
            "timeout": timeout_seconds
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error configuring timeout: {e}")
        raise HTTPException(status_code=500, detail=str(e))
