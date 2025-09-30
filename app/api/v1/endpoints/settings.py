"""
Settings management endpoints
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.settings import UniversalRulesUpdate, UniversalRulesResponse
from app.services.firebase_service import firebase_service
from datetime import datetime

router = APIRouter()


@router.get("/universal-rules")
async def get_universal_rules():
    """
    Get universal rules that apply to all AI personalities
    
    Returns the universal rules configuration.
    """
    try:
        rules_data = firebase_service.get_data("/settings/universalRules")
        
        if not rules_data:
            # Return default rules if none exist
            default_rules = {
                "rules": """CRITICAL RULES:
- Keep initial response short only 'Hi' or 'Heyy'
- Keep responses VERY short (1-9 words max, like real texting)
- Use casual language and shortforms (wyd, hru, lol, tbh, fr, etc.)
- for 'm or f ?' respond 'f' or 'm' respectively opposite of the opposite person
- Try to understand the references the other person makes
- Reduce the number of questions !! Don't ask questions, let the user ask you instead
- NEVER repeat the same response twice in a conversation
- Use emojis very rarely where required (😂, 😔, 🤔)
- Don't mention being an AI or assistant
- Respond naturally to what the person actually said
- Vary your responses - never use the same phrase twice
- Keep it human and natural like real texting""",
                "version": "1.0",
                "enabled": True,
                "updatedAt": datetime.utcnow().isoformat()
            }
            # Save default rules to Firebase
            firebase_service.set_data("/settings/universalRules", default_rules)
            return default_rules
        
        return rules_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving universal rules: {str(e)}"
        )


@router.put("/universal-rules")
async def update_universal_rules(rules: UniversalRulesUpdate):
    """
    Update universal rules that apply to all AI personalities
    
    Args:
        rules: The updated universal rules
    """
    try:
        # Get existing rules
        existing_data = firebase_service.get_data("/settings/universalRules")
        
        if not existing_data:
            existing_data = {
                "rules": "",
                "version": "1.0",
                "enabled": True
            }
        
        # Prepare update data
        update_data = rules.model_dump(exclude_unset=True)
        update_data["updatedAt"] = datetime.utcnow().isoformat()
        
        # Merge with existing data
        updated_rules = {**existing_data, **update_data}
        
        # Update in Firebase
        success = firebase_service.set_data("/settings/universalRules", updated_rules)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update universal rules in Firebase"
            )
        
        return updated_rules
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating universal rules: {str(e)}"
        )

