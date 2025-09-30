"""
Settings schemas for system-wide configuration
"""

from typing import Optional
from pydantic import BaseModel, Field


class UniversalRulesBase(BaseModel):
    """Base schema for universal rules"""
    rules: str = Field(..., description="Universal rules that apply to all personalities", min_length=10)
    version: str = Field(default="1.0", description="Version of the rules")
    enabled: bool = Field(default=True, description="Whether to apply these rules")


class UniversalRulesUpdate(BaseModel):
    """Schema for updating universal rules"""
    rules: Optional[str] = Field(None, description="Universal rules that apply to all personalities", min_length=10)
    version: Optional[str] = Field(None, description="Version of the rules")
    enabled: Optional[bool] = Field(None, description="Whether to apply these rules")


class UniversalRulesResponse(UniversalRulesBase):
    """Schema for universal rules response"""
    updated_at: Optional[str] = Field(None, description="Last update timestamp", alias="updatedAt")
    
    class Config:
        populate_by_name = True
        from_attributes = True

