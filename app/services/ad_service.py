"""
Ad Service for Lightweight Ad Management
Handles ad rotation and delivery via socket events
"""

import random
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.config import settings


class AdService:
    """Service for managing lightweight ads"""
    
    def __init__(self):
        # Sample ads - in production, these would come from a database or ad network
        self.ads: List[Dict[str, Any]] = [
            {
                "id": "ad_1",
                "url": "https://example.com/promo1",
                "image": "https://via.placeholder.com/300x100?text=Ad+1",
                "text": "Check out our special offer!",
                "type": "banner"
            },
            {
                "id": "ad_2",
                "url": "https://example.com/promo2",
                "image": "https://via.placeholder.com/300x100?text=Ad+2",
                "text": "New features available now",
                "type": "banner"
            },
            {
                "id": "ad_3",
                "url": "https://example.com/promo3",
                "image": "https://via.placeholder.com/300x100?text=Ad+3",
                "text": "Upgrade your experience",
                "type": "banner"
            },
            {
                "id": "ad_4",
                "url": "https://example.com/promo4",
                "image": "https://via.placeholder.com/300x100?text=Ad+4",
                "text": "Limited time offer",
                "type": "banner"
            }
        ]
        self.current_ad_index = 0
    
    def get_next_ad(self) -> Dict[str, Any]:
        """
        Get next ad in rotation
        
        Returns:
            Ad data
        """
        if not self.ads:
            return self._get_default_ad()
        
        # Rotate through ads
        ad = self.ads[self.current_ad_index]
        self.current_ad_index = (self.current_ad_index + 1) % len(self.ads)
        
        return {
            **ad,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_random_ad(self) -> Dict[str, Any]:
        """
        Get random ad
        
        Returns:
            Ad data
        """
        if not self.ads:
            return self._get_default_ad()
        
        ad = random.choice(self.ads)
        return {
            **ad,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_default_ad(self) -> Dict[str, Any]:
        """Get default ad if none available"""
        return {
            "id": "ad_default",
            "url": "#",
            "image": None,
            "text": "Thanks for waiting!",
            "type": "text",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def add_ad(self, ad_data: Dict[str, Any]) -> bool:
        """
        Add new ad to rotation
        
        Args:
            ad_data: Ad data (id, url, image, text, type)
            
        Returns:
            Success status
        """
        try:
            required_fields = ["id", "url", "text"]
            if not all(field in ad_data for field in required_fields):
                return False
            
            self.ads.append({
                "id": ad_data["id"],
                "url": ad_data.get("url", "#"),
                "image": ad_data.get("image"),
                "text": ad_data.get("text", ""),
                "type": ad_data.get("type", "banner")
            })
            
            print(f"[AD] Added new ad: {ad_data['id']}")
            return True
            
        except Exception as e:
            print(f"[AD] Error adding ad: {e}")
            return False
    
    def remove_ad(self, ad_id: str) -> bool:
        """
        Remove ad from rotation
        
        Args:
            ad_id: Ad identifier
            
        Returns:
            Success status
        """
        try:
            self.ads = [ad for ad in self.ads if ad["id"] != ad_id]
            print(f"[AD] Removed ad: {ad_id}")
            return True
            
        except Exception as e:
            print(f"[AD] Error removing ad: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ad service statistics"""
        return {
            "total_ads": len(self.ads),
            "current_index": self.current_ad_index,
            "rotation_interval_seconds": settings.AD_ROTATION_INTERVAL_SECONDS
        }


# Global ad service instance
ad_service = AdService()

