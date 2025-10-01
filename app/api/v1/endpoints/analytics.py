"""
Analytics endpoints
"""

from fastapi import APIRouter, HTTPException, status
from app.services.analytics_service import analytics_service

router = APIRouter()


@router.get("/overview")
async def get_analytics_overview():
    """
    Get overview analytics
    
    Returns basic statistics about chatbot usage.
    """
    try:
        overview = analytics_service.get_overview_stats()
        
        return {
            "success": True,
            "data": overview
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analytics: {str(e)}"
        )


@router.get("/personalities")
async def get_personality_analytics():
    """
    Get analytics by personality type
    
    Returns usage statistics for each personality template.
    """
    try:
        personality_stats = analytics_service.get_personality_stats()
        
        return {
            "success": True,
            "data": personality_stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving personality analytics: {str(e)}"
        )


@router.get("/daily")
async def get_daily_analytics():
    """
    Get daily analytics for the last 7 days
    
    Returns daily statistics including sessions, messages, and unique users.
    """
    try:
        daily_stats = analytics_service.get_daily_stats(days=7)
        
        return {
            "success": True,
            "data": daily_stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving daily analytics: {str(e)}"
        )


@router.get("/users")
async def get_user_analytics():
    """
    Get user activity analytics
    
    Returns most active users by message count.
    """
    try:
        user_stats = analytics_service.get_user_activity(limit=10)
        
        return {
            "success": True,
            "data": user_stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user analytics: {str(e)}"
        )


@router.get("/comprehensive")
async def get_comprehensive_analytics():
    """
    Get comprehensive analytics
    
    Returns all analytics data in one response:
    - Overview statistics
    - Personality usage
    - Daily trends
    - Top users
    - Historical data from Firebase
    """
    try:
        # Get in-memory analytics
        analytics = analytics_service.get_all_analytics()
        
        # Get Firebase historical data
        firebase_stats = await analytics_service.get_firebase_stats()
        
        return {
            "success": True,
            "data": {
                **analytics,
                "firebase_stats": firebase_stats
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving comprehensive analytics: {str(e)}"
        )

