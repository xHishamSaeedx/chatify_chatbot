"""
Profile endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List, Dict, Any, Optional
from app.services.firebase_service import firebase_service

router = APIRouter()

async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user from Firebase token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    token = authorization.split(" ")[1]
    # For now, return a mock user - in production, verify the Firebase token
    return {"uid": "mock_user_id", "email": "user@example.com"}


@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's profile"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Get user profile from Firebase
        profile = await firebase_service.get_user_profile(user_id)
        
        return {
            "success": True,
            "data": {
                "profile": profile
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/me")
async def update_profile(
    updates: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update current user's profile"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Update user profile in Firebase
        updated_profile = await firebase_service.update_user_profile(user_id, updates)
        
        return {
            "success": True,
            "data": {
                "profile": updated_profile
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/me")
async def delete_account(current_user: dict = Depends(get_current_user)):
    """Delete current user's account"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Delete user account from Firebase
        await firebase_service.delete_user_account(user_id)
        
        return {
            "success": True,
            "message": "Account deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me/blocked")
async def get_blocked_users(current_user: dict = Depends(get_current_user)):
    """Get list of blocked users"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Get blocked users from Firebase
        blocked_users = await firebase_service.get_blocked_users(user_id)
        
        return {
            "success": True,
            "data": {
                "blockedUsers": blocked_users
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/me/block")
async def block_user(
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Block a user"""
    try:
        user_id = current_user.get("uid")
        target_user_id = request.get("userId")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        if not target_user_id:
            raise HTTPException(status_code=400, detail="Target user ID required")
        
        # Block user in Firebase
        await firebase_service.block_user(user_id, target_user_id)
        
        return {
            "success": True,
            "message": "User blocked successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/me/unblock")
async def unblock_user(
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Unblock a user"""
    try:
        user_id = current_user.get("uid")
        target_user_id = request.get("userId")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        if not target_user_id:
            raise HTTPException(status_code=400, detail="Target user ID required")
        
        # Unblock user in Firebase
        await firebase_service.unblock_user(user_id, target_user_id)
        
        return {
            "success": True,
            "message": "User unblocked successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}")
async def get_user_profile(user_id: str):
    """Get a specific user's profile"""
    try:
        # Get user profile from Firebase
        profile = await firebase_service.get_user_profile(user_id)
        
        return {
            "success": True,
            "data": {
                "profile": profile
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-username")
async def check_username_availability(request: Dict[str, Any]):
    """Check if username is available"""
    try:
        username = request.get("username")
        if not username:
            raise HTTPException(status_code=400, detail="Username required")
        
        # Check username availability in Firebase
        is_available = await firebase_service.check_username_availability(username)
        
        return {
            "success": True,
            "data": {
                "available": is_available
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_profile(
    profile_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Create a new profile"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Create profile in Firebase
        profile = await firebase_service.create_user_profile(user_id, profile_data)
        
        return {
            "success": True,
            "data": {
                "profile": profile
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me/stats")
async def get_profile_stats(current_user: dict = Depends(get_current_user)):
    """Get profile statistics"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Get profile stats from Firebase
        stats = await firebase_service.get_profile_stats(user_id)
        
        return {
            "success": True,
            "data": {
                "stats": stats
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_profiles(
    age_min: int = None,
    age_max: int = None,
    interests: str = None,
    location: str = None,
    limit: int = 20
):
    """Search profiles"""
    try:
        search_params = {}
        if age_min is not None:
            search_params["age_min"] = age_min
        if age_max is not None:
            search_params["age_max"] = age_max
        if interests:
            search_params["interests"] = interests.split(",")
        if location:
            search_params["location"] = location
        
        # Search profiles in Firebase
        profiles = await firebase_service.search_profiles(search_params, limit)
        
        return {
            "success": True,
            "data": {
                "profiles": profiles
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending-interests")
async def get_trending_interests():
    """Get trending interests"""
    try:
        # Get trending interests from Firebase
        interests = await firebase_service.get_trending_interests()
        
        return {
            "success": True,
            "data": {
                "interests": interests
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/me/gallery")
async def add_gallery_picture(
    current_user: dict = Depends(get_current_user)
):
    """Add a picture to gallery"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # This would typically handle file upload
        # For now, return a placeholder response
        return {
            "success": True,
            "message": "Gallery picture added successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me/gallery")
async def get_gallery(current_user: dict = Depends(get_current_user)):
    """Get user's gallery"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Get gallery from Firebase
        gallery = await firebase_service.get_user_gallery(user_id)
        
        return {
            "success": True,
            "data": {
                "gallery": gallery
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/me/gallery/{filename}/main")
async def set_main_picture(
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    """Set a gallery picture as main"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Set main picture in Firebase
        await firebase_service.set_main_picture(user_id, filename)
        
        return {
            "success": True,
            "message": "Main picture updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/me/gallery/{filename}")
async def remove_gallery_picture(
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove a gallery picture"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Remove picture from Firebase
        await firebase_service.remove_gallery_picture(user_id, filename)
        
        return {
            "success": True,
            "message": "Gallery picture removed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/boost")
async def purchase_profile_boost(
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Purchase profile boost"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        cost = request.get("cost", 30)
        duration = request.get("duration", 1.5)
        
        # Purchase boost in Firebase
        boost = await firebase_service.purchase_profile_boost(user_id, cost, duration)
        
        return {
            "success": True,
            "data": {
                "boost": boost
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/boost/cancel")
async def cancel_profile_boost(current_user: dict = Depends(get_current_user)):
    """Cancel profile boost"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Cancel boost in Firebase
        await firebase_service.cancel_profile_boost(user_id)
        
        return {
            "success": True,
            "message": "Profile boost cancelled successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/boosted-profiles")
async def get_boosted_profiles():
    """Get list of boosted profiles"""
    try:
        # Get boosted profiles from Firebase
        profiles = await firebase_service.get_boosted_profiles()
        
        return {
            "success": True,
            "data": {
                "profiles": profiles
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
