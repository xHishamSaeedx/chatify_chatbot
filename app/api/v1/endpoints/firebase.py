"""
Firebase test endpoints
"""

from fastapi import APIRouter, HTTPException
from app.services.firebase_service import firebase_service

router = APIRouter()


@router.get("/test-connection")
async def test_firebase_connection():
    """Test Firebase connection"""
    try:
        # Test database connection by getting root data
        data = firebase_service.get_data("/")
        return {
            "status": "success",
            "message": "Firebase connection successful",
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Firebase connection failed: {str(e)}"
        )


@router.post("/test-write")
async def test_firebase_write():
    """Test Firebase write operation"""
    try:
        test_data = {
            "message": "Hello from Chatify Chatbot!",
            "timestamp": "2024-01-01T00:00:00Z",
            "test": True
        }
        
        # Write test data
        success = firebase_service.set_data("/test/connection", test_data)
        
        if success:
            return {
                "status": "success",
                "message": "Firebase write operation successful",
                "data": test_data
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Firebase write operation failed"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Firebase write test failed: {str(e)}"
        )


@router.get("/test-read")
async def test_firebase_read():
    """Test Firebase read operation"""
    try:
        # Read test data
        data = firebase_service.get_data("/test/connection")
        
        return {
            "status": "success",
            "message": "Firebase read operation successful",
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Firebase read test failed: {str(e)}"
        )
