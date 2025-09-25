"""
Chat endpoints for OpenAI ChatGPT integration
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
from app.schemas.chat import (
    ChatRequest, 
    ChatResponse, 
    SimpleChatRequest, 
    ConversationRequest,
    ChatMessage
)
from app.services.openai_service import openai_service

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with ChatGPT using conversation history
    
    This endpoint allows you to have a conversation with ChatGPT,
    optionally including conversation history and system prompts.
    """
    try:
        # Convert conversation history to the format expected by OpenAI
        conversation_history = []
        if request.conversation_history:
            for msg in request.conversation_history:
                conversation_history.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Get chat completion
        result = await openai_service.conversational_chat(
            conversation_history=conversation_history,
            user_message=request.message,
            system_prompt=request.system_prompt
        )
        
        if not result["success"]:
            error_detail = result['error']
            # Check for quota/billing errors (including 429 status codes)
            if ("quota" in error_detail.lower() or 
                "billing" in error_detail.lower() or 
                "exceeded" in error_detail.lower() or
                "429" in error_detail or
                "insufficient_quota" in error_detail.lower()):
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail=f"OpenAI API quota exceeded. Please check your billing details: {error_detail}"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"OpenAI API error: {error_detail}"
                )
        
        return ChatResponse(**result)
        
    except HTTPException:
        # Re-raise HTTPExceptions (like quota errors) without modification
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/simple", response_model=ChatResponse)
async def simple_chat(request: SimpleChatRequest):
    """
    Simple chat with ChatGPT (no conversation history)
    
    This endpoint provides a simple interface for chatting with ChatGPT
    without managing conversation history.
    """
    try:
        result = await openai_service.simple_chat(
            user_message=request.message,
            system_prompt=request.system_prompt
        )
        
        if not result["success"]:
            error_detail = result['error']
            # Check for quota/billing errors (including 429 status codes)
            if ("quota" in error_detail.lower() or 
                "billing" in error_detail.lower() or 
                "exceeded" in error_detail.lower() or
                "429" in error_detail or
                "insufficient_quota" in error_detail.lower()):
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail=f"OpenAI API quota exceeded. Please check your billing details: {error_detail}"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"OpenAI API error: {error_detail}"
                )
        
        return ChatResponse(**result)
        
    except HTTPException:
        # Re-raise HTTPExceptions (like quota errors) without modification
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/conversation", response_model=ChatResponse)
async def conversation_chat(request: ConversationRequest):
    """
    Chat with full conversation context
    
    This endpoint allows you to send the entire conversation context
    as a list of messages to ChatGPT.
    """
    try:
        # Convert messages to the format expected by OpenAI
        messages = []
        for msg in request.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Get chat completion
        result = await openai_service.chat_completion(
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        if not result["success"]:
            error_detail = result['error']
            # Check for quota/billing errors (including 429 status codes)
            if ("quota" in error_detail.lower() or 
                "billing" in error_detail.lower() or 
                "exceeded" in error_detail.lower() or
                "429" in error_detail or
                "insufficient_quota" in error_detail.lower()):
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail=f"OpenAI API quota exceeded. Please check your billing details: {error_detail}"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"OpenAI API error: {error_detail}"
                )
        
        return ChatResponse(**result)
        
    except HTTPException:
        # Re-raise HTTPExceptions (like quota errors) without modification
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/models")
async def get_available_models():
    """
    Get information about available OpenAI models
    """
    return {
        "current_model": openai_service.model,
        "available_models": [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-4",
            "gpt-4-turbo-preview"
        ],
        "default_model": "gpt-3.5-turbo"
    }
