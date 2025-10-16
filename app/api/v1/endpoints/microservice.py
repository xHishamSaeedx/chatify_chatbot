"""
Microservice optimized endpoints for backend-to-backend communication
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel, Field
from app.services.microservice_adapter import microservice_adapter

router = APIRouter()


class MicroserviceRequest(BaseModel):
    """Base request for microservice operations"""
    orchestrator_id: Optional[str] = Field(None, description="Backend orchestrator identifier")
    orchestrator_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata from orchestrator")


class CreateSessionMicroserviceRequest(MicroserviceRequest):
    """Request to create a new chatbot session via microservice"""
    user_id: str = Field(..., description="Unique user identifier")
    template_id: Optional[str] = Field("general-assistant", description="Chatbot personality type")


class SendMessageMicroserviceRequest(MicroserviceRequest):
    """Request to send a message to chatbot via microservice"""
    message: str = Field(..., description="User's message", min_length=1, max_length=4000)


class EndSessionMicroserviceRequest(MicroserviceRequest):
    """Request to end a chatbot session via microservice"""
    reason: Optional[str] = Field("manual", description="Reason for ending session")


class MicroserviceResponse(BaseModel):
    """Enhanced microservice response with metadata"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    session_id: Optional[str] = None
    response: Optional[str] = None
    message_count: Optional[int] = None
    debug_info: Optional[Dict[str, Any]] = None
    terminated: Optional[bool] = None
    termination_reason: Optional[str] = None
    on_seen: Optional[bool] = None
    microservice: Optional[Dict[str, Any]] = None


@router.post("/session", response_model=MicroserviceResponse)
async def create_session_microservice(
    request: CreateSessionMicroserviceRequest,
    x_orchestrator_id: Optional[str] = Header(None, description="Backend orchestrator ID")
):
    """
    Create a new chatbot session (Microservice Optimized)
    
    This endpoint is optimized for backend-to-backend communication
    and includes enhanced metadata and monitoring capabilities.
    """
    try:
        # Merge orchestrator metadata
        orchestrator_metadata = request.orchestrator_metadata or {}
        if x_orchestrator_id:
            orchestrator_metadata['orchestrator_id'] = x_orchestrator_id
        
        # Create session through microservice adapter
        result = await microservice_adapter.create_session_optimized(
            user_id=request.user_id,
            template_id=request.template_id,
            orchestrator_metadata=orchestrator_metadata
        )
        
        if result["success"]:
            return MicroserviceResponse(
                success=True,
                message="Session created successfully",
                session_id=result["session_id"],
                debug_info=result.get("debug_info"),
                microservice=result.get("microservice")
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to create session")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Microservice error: {str(e)}"
        )


@router.post("/session/{session_id}/message", response_model=MicroserviceResponse)
async def send_message_microservice(
    session_id: str,
    request: SendMessageMicroserviceRequest,
    x_orchestrator_id: Optional[str] = Header(None, description="Backend orchestrator ID")
):
    """
    Send a message to the chatbot (Microservice Optimized)
    
    This endpoint is optimized for backend-to-backend communication
    with enhanced response metadata and performance tracking.
    """
    try:
        print("\n" + "="*80)
        print("[MICROSERVICE] INCOMING MESSAGE TO CHATBOT")
        print("="*80)
        print(f"Session ID: {session_id}")
        print(f"Message: {request.message}")
        print(f"Message Length: {len(request.message)} characters")
        print(f"Orchestrator ID: {x_orchestrator_id or 'None'}")
        print(f"Timestamp: {__import__('datetime').datetime.now().isoformat()}")
        print("="*80 + "\n")
        
        # Merge orchestrator metadata
        orchestrator_metadata = request.orchestrator_metadata or {}
        if x_orchestrator_id:
            orchestrator_metadata['orchestrator_id'] = x_orchestrator_id
        orchestrator_metadata['session_id'] = session_id
        
        # Send message through microservice adapter
        result = await microservice_adapter.send_message_optimized(
            session_id=session_id,
            user_message=request.message,
            orchestrator_metadata=orchestrator_metadata
        )
        
        if result["success"]:
            print("\n" + "="*80)
            print("[MICROSERVICE] CHATBOT RESPONSE READY")
            print("="*80)
            print(f"Session ID: {session_id}")
            print(f"Response: {result.get('response', '')}")
            print(f"Message Count: {result.get('message_count', 0)}")
            print(f"Terminated: {result.get('terminated', False)}")
            print(f"On Seen: {result.get('on_seen', False)}")
            if result.get('terminated'):
                print(f"Termination Reason: {result.get('termination_reason', 'N/A')}")
            print(f"Timestamp: {__import__('datetime').datetime.now().isoformat()}")
            print("="*80 + "\n")
            
            return MicroserviceResponse(
                success=True,
                response=result.get("response"),
                session_id=result.get("session_id"),
                message_count=result.get("message_count"),
                debug_info=result.get("debug_info"),
                terminated=result.get("terminated"),
                termination_reason=result.get("termination_reason"),
                on_seen=result.get("on_seen"),
                microservice=result.get("microservice")
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
            detail=f"Microservice error: {str(e)}"
        )


@router.delete("/session/{session_id}", response_model=MicroserviceResponse)
async def end_session_microservice(
    session_id: str,
    request: EndSessionMicroserviceRequest,
    x_orchestrator_id: Optional[str] = Header(None, description="Backend orchestrator ID")
):
    """
    End a chatbot session (Microservice Optimized)
    
    This endpoint is optimized for backend-to-backend communication
    with proper cleanup and metadata tracking.
    """
    try:
        # Merge orchestrator metadata
        orchestrator_metadata = request.orchestrator_metadata or {}
        if x_orchestrator_id:
            orchestrator_metadata['orchestrator_id'] = x_orchestrator_id
        orchestrator_metadata['session_id'] = session_id
        orchestrator_metadata['end_reason'] = request.reason
        
        # End session through microservice adapter
        result = await microservice_adapter.end_session_optimized(
            session_id=session_id,
            orchestrator_metadata=orchestrator_metadata
        )
        
        if result["success"]:
            return MicroserviceResponse(
                success=True,
                message="Session ended successfully",
                microservice=result.get("microservice")
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
            detail=f"Microservice error: {str(e)}"
        )


@router.get("/health/detailed", response_model=Dict[str, Any])
async def get_detailed_health():
    """
    Get detailed microservice health information
    
    This endpoint provides comprehensive health status including
    dependencies, metrics, and service state.
    """
    try:
        health_data = microservice_adapter.get_service_health()
        
        status_code = 200 if health_data['status'] == 'healthy' else 503
        
        if status_code == 503:
            raise HTTPException(
                status_code=status_code,
                detail=health_data
            )
        
        return health_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check error: {str(e)}"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_microservice_stats():
    """
    Get comprehensive microservice statistics
    
    This endpoint provides detailed service metrics, session stats,
    and performance information for monitoring and debugging.
    """
    try:
        stats_data = microservice_adapter.get_service_stats()
        return stats_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stats retrieval error: {str(e)}"
        )


@router.post("/cleanup", response_model=Dict[str, Any])
async def trigger_cleanup():
    """
    Trigger service cleanup operations
    
    This endpoint allows the orchestrator to trigger cleanup
    of expired sessions and service maintenance.
    """
    try:
        cleanup_result = await microservice_adapter.cleanup_service()
        return cleanup_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cleanup error: {str(e)}"
        )


@router.get("/version")
async def get_service_version():
    """
    Get microservice version and basic info
    
    Simple endpoint for version checking and service identification.
    """
    return {
        "service": microservice_adapter.service_name,
        "version": microservice_adapter.version,
        "status": "operational",
        "endpoints": {
            "session_create": "POST /microservice/session",
            "session_message": "POST /microservice/session/{id}/message", 
            "session_end": "DELETE /microservice/session/{id}",
            "health": "GET /microservice/health/detailed",
            "stats": "GET /microservice/stats",
            "cleanup": "POST /microservice/cleanup"
        }
    }

