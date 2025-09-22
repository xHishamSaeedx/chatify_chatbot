"""
Chat-related Pydantic schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Individual chat message schema"""
    role: str = Field(..., description="Message role: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str = Field(..., description="User's message", min_length=1, max_length=4000)
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=None, 
        description="Previous conversation history"
    )
    system_prompt: Optional[str] = Field(
        default=None, 
        description="System prompt to set context", 
        max_length=2000
    )
    temperature: Optional[float] = Field(
        default=0.7, 
        ge=0.0, 
        le=2.0, 
        description="Sampling temperature (0.0 to 2.0)"
    )
    max_tokens: Optional[int] = Field(
        default=None, 
        ge=1, 
        le=4000, 
        description="Maximum tokens to generate"
    )


class ChatUsage(BaseModel):
    """Token usage information"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    """Chat response schema"""
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    usage: Optional[ChatUsage] = None
    model: Optional[str] = None


class SimpleChatRequest(BaseModel):
    """Simple chat request schema"""
    message: str = Field(..., description="User's message", min_length=1, max_length=4000)
    system_prompt: Optional[str] = Field(
        default=None, 
        description="System prompt to set context", 
        max_length=2000
    )


class ConversationRequest(BaseModel):
    """Conversation request schema with full conversation context"""
    messages: List[ChatMessage] = Field(..., description="Full conversation messages")
    temperature: Optional[float] = Field(
        default=0.7, 
        ge=0.0, 
        le=2.0, 
        description="Sampling temperature (0.0 to 2.0)"
    )
    max_tokens: Optional[int] = Field(
        default=None, 
        ge=1, 
        le=4000, 
        description="Maximum tokens to generate"
    )
