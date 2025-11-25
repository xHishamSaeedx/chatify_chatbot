"""
Queue endpoints for user matching
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Query
from typing import Dict, Any, Optional
from app.services.queue_service import queue_service
from app.services.socket_service import socket_service
from app.services.chatbot_fallback_service import chatbot_fallback_service

router = APIRouter()


async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user from Firebase token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    token = authorization.split(" ")[1]
    # For now, return a mock user - in production, verify the Firebase token
    return {"uid": "mock_user_id", "email": "user@example.com"}


@router.post("/join")
async def join_queue(
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Join the matching queue
    
    Request body:
    - socketId: Socket.IO session ID
    """
    try:
        # Prioritize userId from request body, fallback to authenticated user
        user_id = request.get("userId") or current_user.get("uid")
        socket_id = request.get("socketId")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        if not socket_id:
            raise HTTPException(status_code=400, detail="Socket ID required")
        
        result = await queue_service.join_queue(user_id, socket_id)
        
        if result.get("success"):
            # Emit socket event
            await socket_service.sio.emit("queue_joined", {
                "status": result.get("status"),
                "position": result.get("position"),
                "wait_time_seconds": result.get("wait_time_seconds", 0)
            }, room=socket_id)
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/leave")
async def leave_queue(current_user: dict = Depends(get_current_user)):
    """
    Leave the matching queue
    """
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        result = await queue_service.leave_queue(user_id)
        
        if result.get("success"):
            # Get socket ID if user exists
            if user_id in queue_service.users:
                socket_id = queue_service.users[user_id].socket_id
                await socket_service.sio.emit("queue_left", {
                    "success": True
                }, room=socket_id)
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_queue_status(
    userId: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Get queue status for current user
    
    Query params:
    - userId: Optional user ID (if not provided, uses authenticated user)
    """
    try:
        # Prioritize userId from query param, fallback to authenticated user
        user_id = userId or current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        status = await queue_service.get_status(user_id)
        
        return {
            "success": True,
            "data": status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exit-ai")
async def exit_ai_chat(
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Exit AI chat and rejoin queue
    
    Request body:
    - socketId: Socket.IO session ID
    """
    try:
        # Prioritize userId from request body, fallback to authenticated user
        user_id = request.get("userId") or current_user.get("uid")
        socket_id = request.get("socketId")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        if not socket_id:
            raise HTTPException(status_code=400, detail="Socket ID required")
        
        # End AI session
        await chatbot_fallback_service.end_ai_session(user_id)
        
        # Requeue user
        result = await queue_service.end_ai_chat_and_requeue(user_id)
        
        if result.get("success"):
            # Update socket ID if needed
            if user_id in queue_service.users:
                queue_service.users[user_id].socket_id = socket_id
            
            # Emit socket events
            await socket_service.sio.emit("ai_chat_ended", {
                "requeued": True,
                "position": result.get("position"),
                "wait_time_seconds": result.get("wait_time_seconds", 0)
            }, room=socket_id)
            
            await socket_service.sio.emit("queue_joined", {
                "status": "requeued",
                "position": result.get("position"),
                "wait_time_seconds": result.get("wait_time_seconds", 0)
            }, room=socket_id)
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active-count")
async def get_active_count():
    """
    Get active user count (in queue + matched)
    """
    try:
        count = queue_service.get_active_count()
        stats = queue_service.get_stats()
        
        return {
            "success": True,
            "data": {
                "active_count": count,
                "stats": stats
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

