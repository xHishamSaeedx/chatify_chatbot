"""
Chatbot session management endpoints
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.services.session_service import session_service

router = APIRouter()


class CreateSessionRequest(BaseModel):
    """Request to create a new chatbot session"""
    user_id: str = Field(..., description="Unique user identifier")
    template_id: Optional[str] = Field("general", description="Chatbot personality type to use")


class SendMessageRequest(BaseModel):
    """Request to send a message to chatbot"""
    message: str = Field(..., description="User's message", min_length=1, max_length=4000)


class ChatbotResponse(BaseModel):
    """Chatbot response"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    session_id: Optional[str] = None
    response: Optional[str] = None
    message_count: Optional[int] = None


@router.post("/session", response_model=ChatbotResponse)
async def create_session(request: CreateSessionRequest):
    """
    Create a new chatbot session
    
    This endpoint creates a new chatbot session for a user.
    Each session maintains conversation history and context.
    """
    try:
        result = await session_service.create_session(
            user_id=request.user_id,
            template_id=request.template_id
        )
        
        if result["success"]:
            return ChatbotResponse(
                success=True,
                message="Session created successfully",
                session_id=result["session_id"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to create session")
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating session: {str(e)}"
        )


@router.post("/session/{session_id}/message", response_model=ChatbotResponse)
async def send_message(session_id: str, request: SendMessageRequest):
    """
    Send a message to the chatbot
    
    This endpoint allows users to send messages to their active chatbot session.
    The AI will respond based on the conversation history and system prompt.
    """
    try:
        result = await session_service.send_message(
            session_id=session_id,
            user_message=request.message
        )
        
        if result["success"]:
            return ChatbotResponse(
                success=True,
                response=result["response"],
                session_id=result["session_id"],
                message_count=result["message_count"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to send message")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending message: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=ChatbotResponse)
async def get_session(session_id: str):
    """
    Get session information
    
    This endpoint retrieves information about a specific chatbot session.
    """
    try:
        result = await session_service.get_session(session_id)
        
        if result["success"]:
            return ChatbotResponse(
                success=True,
                message="Session retrieved successfully",
                session_id=session_id
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Session not found")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving session: {str(e)}"
        )


@router.delete("/session/{session_id}", response_model=ChatbotResponse)
async def end_session(session_id: str):
    """
    End a chatbot session
    
    This endpoint ends an active chatbot session and cleans up resources.
    """
    try:
        result = await session_service.end_session(session_id)
        
        if result["success"]:
            return ChatbotResponse(
                success=True,
                message="Session ended successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to end session")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ending session: {str(e)}"
        )


@router.get("/stats")
async def get_session_stats():
    """
    Get chatbot session statistics
    
    This endpoint provides statistics about active sessions and system status.
    """
    try:
        stats = session_service.get_session_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving stats: {str(e)}"
        )


@router.post("/cleanup")
async def cleanup_sessions():
    """
    Clean up expired sessions from both memory and Firebase
    
    This endpoint manually triggers cleanup of expired sessions.
    """
    try:
        result = await session_service.cleanup_expired_sessions()
        return {
            "success": True,
            "message": "Cleanup completed",
            "memory_sessions_cleaned": result["cleaned_sessions"],
            "firebase_sessions_cleaned": result["firebase_cleaned"],
            "active_sessions": result["active_sessions"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during cleanup: {str(e)}"
        )


@router.get("/personalities")
async def get_available_personalities():
    """
    Get available chatbot personalities
    
    This endpoint returns a list of all available chatbot personality types
    that users can choose from when creating a session.
    """
    try:
        personalities = {
            "general": "Friendly and casual general chatbot",
            "baddie": "Confident, sassy baddie with attitude",
            "hot-bold-slutty": "Bold, sexually confident and flirty",
            "party-girl": "Fun, energetic party girl always ready for adventure",
            "career-driven": "Focused, ambitious career-driven hustler",
            "hippie-spiritual": "Peaceful, spiritual hippie with good vibes",
            "content-creator": "Creative, social media savvy content creator",
            "innocent-cute": "Sweet, innocent and cute personality",
            "sarcastic-savage": "Witty, sarcastic with sharp tongue",
            "hopeless-romantic": "Romantic, dreamy believer in true love",
            "mysterious-quiet": "Mysterious, quiet and intriguing",
            "pick-me-girl": "Tries too hard to be liked, puts others down",
            "clingy-possessive": "Clingy, possessive and wants constant attention"
        }
        
        return {
            "success": True,
            "personalities": personalities,
            "default": "general"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving personalities: {str(e)}"
        )

