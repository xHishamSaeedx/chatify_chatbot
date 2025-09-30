"""
Personality/Template schemas for validation
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class PersonalityBase(BaseModel):
    """Base personality schema"""
    name: str = Field(..., description="Unique template identifier", min_length=1, max_length=100)
    title: str = Field(..., description="Display title", min_length=1, max_length=200)
    description: str = Field(..., description="Template description", min_length=1, max_length=500)
    category: str = Field(default="general", description="Template category")
    system_prompt: str = Field(..., description="System prompt for the chatbot", min_length=10, alias="systemPrompt")
    welcome_message: str = Field(default="Hello! How can I help you?", description="Initial welcome message", alias="welcomeMessage")
    model: str = Field(default="gpt-4o-mini", description="Recommended AI model")
    temperature: float = Field(default=0.9, description="Temperature setting", ge=0.0, le=2.0)
    max_tokens: int = Field(default=150, description="Max tokens", ge=10, le=4000)
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    is_public: bool = Field(default=True, description="Whether template is public", alias="isPublic")
    is_default: bool = Field(default=False, description="Whether this is a default template", alias="isDefault")


class PersonalityCreate(PersonalityBase):
    """Schema for creating a new personality"""
    pass


class PersonalityUpdate(BaseModel):
    """Schema for updating a personality"""
    title: Optional[str] = Field(None, description="Display title", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Template description", min_length=1, max_length=500)
    category: Optional[str] = Field(None, description="Template category")
    system_prompt: Optional[str] = Field(None, description="System prompt for the chatbot", min_length=10, alias="systemPrompt")
    welcome_message: Optional[str] = Field(None, description="Initial welcome message", alias="welcomeMessage")
    model: Optional[str] = Field(None, description="Recommended AI model")
    temperature: Optional[float] = Field(None, description="Temperature setting", ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, description="Max tokens", ge=10, le=4000)
    tags: Optional[List[str]] = Field(None, description="Searchable tags")
    is_public: Optional[bool] = Field(None, description="Whether template is public", alias="isPublic")
    is_default: Optional[bool] = Field(None, description="Whether this is a default template", alias="isDefault")


class PersonalityResponse(PersonalityBase):
    """Schema for personality response"""
    id: Optional[str] = None
    usage_count: int = Field(default=0, description="How many times used", alias="usageCount")
    created_at: Optional[str] = Field(None, description="When created", alias="createdAt")
    updated_at: Optional[str] = Field(None, description="Last update", alias="updatedAt")
    
    class Config:
        populate_by_name = True
        from_attributes = True

