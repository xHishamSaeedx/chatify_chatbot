"""
Personality/Template management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from app.schemas.personality import PersonalityCreate, PersonalityUpdate, PersonalityResponse
from app.services.firebase_service import firebase_service
from datetime import datetime

router = APIRouter()


@router.get("/")
async def get_all_personalities():
    """
    Get all AI personalities/templates
    
    Returns a list of all available AI personality templates.
    """
    try:
        # Get templates from Firebase Realtime Database
        templates_data = firebase_service.get_data("/templates")
        
        if not templates_data:
            return []
        
        # Convert to list with normalized field names
        personalities = []
        for template_id, template_data in templates_data.items():
            if isinstance(template_data, dict):
                # Normalize the data to handle both old and new formats
                # Handle systemPrompt -> personalityPrompt migration
                personality_prompt = template_data.get("personalityPrompt") or template_data.get("systemPrompt", "")
                
                personality = {
                    "id": template_id,
                    "name": template_data.get("name") or template_data.get("personalityType") or template_id,
                    "title": template_data.get("title") or template_data.get("name") or template_id.replace("-", " ").title(),
                    "description": template_data.get("description", ""),
                    "category": template_data.get("category", "general"),
                    "personalityPrompt": personality_prompt,
                    "welcomeMessage": template_data.get("welcomeMessage", "Hello! How can I help you?"),
                    "model": template_data.get("model", "gpt-4o-mini"),
                    "temperature": template_data.get("temperature", 0.9),
                    "maxTokens": template_data.get("maxTokens", 150),
                    "tags": template_data.get("tags", []),
                    "isPublic": template_data.get("isPublic", True),
                    "isDefault": template_data.get("isDefault", False),
                    "usageCount": template_data.get("usageCount", 0),
                    "createdAt": template_data.get("createdAt"),
                    "updatedAt": template_data.get("updatedAt"),
                }
                personalities.append(personality)
        
        return personalities
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving personalities: {str(e)}"
        )


@router.get("/{personality_id}")
async def get_personality(personality_id: str):
    """
    Get a specific AI personality by ID
    
    Args:
        personality_id: The unique identifier of the personality
    """
    try:
        template_data = firebase_service.get_data(f"/templates/{personality_id}")
        
        if not template_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Personality '{personality_id}' not found"
            )
        
        # Normalize the data to handle both old and new formats
        # Handle systemPrompt -> personalityPrompt migration
        personality_prompt = template_data.get("personalityPrompt") or template_data.get("systemPrompt", "")
        
        personality = {
            "id": personality_id,
            "name": template_data.get("name") or template_data.get("personalityType") or personality_id,
            "title": template_data.get("title") or template_data.get("name") or personality_id.replace("-", " ").title(),
            "description": template_data.get("description", ""),
            "category": template_data.get("category", "general"),
            "personalityPrompt": personality_prompt,
            "welcomeMessage": template_data.get("welcomeMessage", "Hello! How can I help you?"),
            "model": template_data.get("model", "gpt-4o-mini"),
            "temperature": template_data.get("temperature", 0.9),
            "maxTokens": template_data.get("maxTokens", 150),
            "tags": template_data.get("tags", []),
            "isPublic": template_data.get("isPublic", True),
            "isDefault": template_data.get("isDefault", False),
            "usageCount": template_data.get("usageCount", 0),
            "createdAt": template_data.get("createdAt"),
            "updatedAt": template_data.get("updatedAt"),
        }
        
        return personality
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving personality: {str(e)}"
        )


@router.post("/")
async def create_personality(personality: PersonalityCreate):
    """
    Create a new AI personality/template
    
    Args:
        personality: The personality data to create
    """
    try:
        # Check if personality with same name already exists
        existing_templates = firebase_service.get_data("/templates")
        if existing_templates:
            for template_id, template_data in existing_templates.items():
                if isinstance(template_data, dict) and template_data.get("name") == personality.name:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Personality with name '{personality.name}' already exists"
                    )
        
        # Use the name as the ID (normalized)
        personality_id = personality.name.lower().replace(" ", "-")
        
        # Prepare data for Firebase
        personality_data = personality.model_dump(by_alias=True)
        personality_data["createdAt"] = datetime.utcnow().isoformat()
        personality_data["updatedAt"] = datetime.utcnow().isoformat()
        personality_data["usageCount"] = 0
        
        # Save to Firebase
        success = firebase_service.set_data(f"/templates/{personality_id}", personality_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create personality in Firebase"
            )
        
        return {
            "id": personality_id,
            **personality_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating personality: {str(e)}"
        )


@router.put("/{personality_id}")
async def update_personality(personality_id: str, personality: PersonalityUpdate):
    """
    Update an existing AI personality/template
    
    Args:
        personality_id: The unique identifier of the personality to update
        personality: The updated personality data
    """
    try:
        # Check if personality exists
        existing_data = firebase_service.get_data(f"/templates/{personality_id}")
        
        if not existing_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Personality '{personality_id}' not found"
            )
        
        # Prepare update data (only include fields that were provided)
        update_data = personality.model_dump(by_alias=True, exclude_unset=True)
        update_data["updatedAt"] = datetime.utcnow().isoformat()
        
        # Merge with existing data
        updated_personality = {**existing_data, **update_data}
        
        # Update in Firebase
        success = firebase_service.set_data(f"/templates/{personality_id}", updated_personality)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update personality in Firebase"
            )
        
        return {
            "id": personality_id,
            **updated_personality
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating personality: {str(e)}"
        )


@router.delete("/{personality_id}")
async def delete_personality(personality_id: str):
    """
    Delete an AI personality/template
    
    Args:
        personality_id: The unique identifier of the personality to delete
    """
    try:
        # Check if personality exists
        existing_data = firebase_service.get_data(f"/templates/{personality_id}")
        
        if not existing_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Personality '{personality_id}' not found"
            )
        
        # Don't allow deletion of default personalities
        if existing_data.get("isDefault"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete default personality"
            )
        
        # Delete from Firebase
        success = firebase_service.delete_data(f"/templates/{personality_id}")
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete personality from Firebase"
            )
        
        return {
            "success": True,
            "message": f"Personality '{personality_id}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting personality: {str(e)}"
        )

