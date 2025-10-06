"""
Connection endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List, Dict, Any, Optional
from app.services.firebase_service import firebase_service
from app.services.redis_service import redis_service

router = APIRouter()

async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user from Firebase token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    token = authorization.split(" ")[1]
    # For now, return a mock user - in production, verify the Firebase token
    return {"uid": "mock_user_id", "email": "user@example.com"}


@router.get("/random/session/active")
async def get_active_random_chat_session(current_user: dict = Depends(get_current_user)):
    """Get active random chat session"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Check for active session in Redis
        session = await redis_service.get_active_session(user_id)
        
        if session:
            return {
                "success": True,
                "data": {
                    "session": session
                }
            }
        else:
            return {
                "success": True,
                "data": {
                    "session": None
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/random/session/clear")
async def force_clear_active_session(current_user: dict = Depends(get_current_user)):
    """Force clear active random chat session"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Clear active session in Redis
        await redis_service.clear_active_session(user_id)
        
        return {
            "success": True,
            "message": "Active session cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/random/session/end")
async def end_random_chat_session(
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """End random chat session"""
    try:
        user_id = current_user.get("uid")
        session_id = request.get("sessionId")
        reason = request.get("reason", "User ended session")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID required")
        
        # End session in Redis
        await redis_service.end_session(session_id, reason, user_id)
        
        return {
            "success": True,
            "message": "Session ended successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/friend-request")
async def send_friend_request(
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Send a friend request"""
    try:
        user_id = current_user.get("uid")
        to_user_id = request.get("toUserId")
        message = request.get("message")
        request_type = request.get("type")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        if not to_user_id:
            raise HTTPException(status_code=400, detail="Target user ID required")
        
        # Send friend request in Firebase
        friend_request = await firebase_service.send_friend_request(
            user_id, to_user_id, message, request_type
        )
        
        return {
            "success": True,
            "data": {
                "friendRequest": friend_request
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/friend-request/{connection_id}/accept")
async def accept_friend_request(
    connection_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Accept a friend request"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Accept friend request in Firebase
        connection = await firebase_service.accept_friend_request(connection_id, user_id)
        
        return {
            "success": True,
            "data": {
                "connection": connection
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/friend-request/{connection_id}/reject")
async def reject_friend_request(
    connection_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Reject a friend request"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Reject friend request in Firebase
        await firebase_service.reject_friend_request(connection_id, user_id)
        
        return {
            "success": True,
            "message": "Friend request rejected successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/friend-request/{connection_id}")
async def cancel_friend_request(
    connection_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancel a friend request"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Cancel friend request in Firebase
        await firebase_service.cancel_friend_request(connection_id, user_id)
        
        return {
            "success": True,
            "message": "Friend request cancelled successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/friend-requests/incoming")
async def get_incoming_friend_requests(current_user: dict = Depends(get_current_user)):
    """Get incoming friend requests"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Get incoming friend requests from Firebase
        requests = await firebase_service.get_incoming_friend_requests(user_id)
        
        return {
            "success": True,
            "data": {
                "requests": requests
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/friend-requests/outgoing")
async def get_outgoing_friend_requests(current_user: dict = Depends(get_current_user)):
    """Get outgoing friend requests"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Get outgoing friend requests from Firebase
        requests = await firebase_service.get_outgoing_friend_requests(user_id)
        
        return {
            "success": True,
            "data": {
                "requests": requests
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/friends")
async def get_friends(current_user: dict = Depends(get_current_user)):
    """Get user's friends"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Get friends from Firebase
        friends = await firebase_service.get_friends(user_id)
        
        return {
            "success": True,
            "data": {
                "friends": friends
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/friends/{friend_user_id}")
async def remove_friend(
    friend_user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove a friend"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Remove friend in Firebase
        await firebase_service.remove_friend(user_id, friend_user_id)
        
        return {
            "success": True,
            "message": "Friend removed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{target_user_id}")
async def get_connection_status(
    target_user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get connection status with a user"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Get connection status from Firebase
        status = await firebase_service.get_connection_status(user_id, target_user_id)
        
        return {
            "success": True,
            "data": {
                "status": status
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
