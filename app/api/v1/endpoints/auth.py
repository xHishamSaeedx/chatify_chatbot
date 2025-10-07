"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.services.firebase_service import firebase_service

router = APIRouter()

class LoginRequest(BaseModel):
    signInProvider: str
    displayName: Optional[str] = None
    photoURL: Optional[str] = None
    deviceId: Optional[str] = None

@router.get("/verify")
async def verify_auth():
    """
    Verify authentication status.
    For now, just return success since we're using Firebase on the frontend.
    """
    return {"success": True, "message": "Authentication verified"}

@router.get("/test-connection")
async def test_connection():
    """
    Test backend connectivity.
    """
    return {"success": True, "message": "Backend connection successful"}

@router.post("/login")
async def login(request: LoginRequest):
    """
    Handle Firebase authentication login.
    For now, just return success since we're using Firebase on the frontend.
    """
    # Create a mock user response
    user_data = {
        "id": f"user_{request.signInProvider}_{request.deviceId or 'default'}",
        "displayName": request.displayName or "User",
        "email": f"user@{request.signInProvider}.com",
        "photoURL": request.photoURL,
        "signInProvider": request.signInProvider,
        "isAnonymous": request.signInProvider == "anonymous",
    }
    
    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "user": user_data,
            "token": "mock_token_for_development"
        }
    }

@router.post("/logout")
async def logout():
    """
    Logout endpoint.
    For now, just return success since we're using Firebase on the frontend.
    """
    return {"success": True, "message": "Logged out successfully"}
