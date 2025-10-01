"""
Analytics service for tracking chatbot usage and statistics
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
from app.services.firebase_service import firebase_service


class AnalyticsService:
    """Service for tracking and retrieving chatbot analytics"""
    
    def __init__(self):
        self._in_memory_stats = {
            "total_sessions_created": 0,
            "total_messages_sent": 0,
            "total_sessions_ended": 0,
            "sessions_by_personality": defaultdict(int),
            "messages_by_user": defaultdict(int),
            "daily_stats": defaultdict(lambda: {
                "sessions": 0,
                "messages": 0,
                "users": set()
            })
        }
    
    def track_session_created(self, user_id: str, template_id: str, session_id: str):
        """Track when a new session is created"""
        try:
            self._in_memory_stats["total_sessions_created"] += 1
            self._in_memory_stats["sessions_by_personality"][template_id] += 1
            
            today = datetime.utcnow().date().isoformat()
            self._in_memory_stats["daily_stats"][today]["sessions"] += 1
            self._in_memory_stats["daily_stats"][today]["users"].add(user_id)
            
            # Store in Firebase for persistence
            event_data = {
                "event_type": "session_created",
                "user_id": user_id,
                "session_id": session_id,
                "template_id": template_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            firebase_service.push_data("/analytics/events", event_data)
            
            print(f"📊 Analytics: Session created - User: {user_id}, Template: {template_id}")
            
        except Exception as e:
            print(f"⚠️ Analytics tracking error: {e}")
    
    def track_message_sent(self, user_id: str, session_id: str, message_length: int):
        """Track when a message is sent"""
        try:
            self._in_memory_stats["total_messages_sent"] += 1
            self._in_memory_stats["messages_by_user"][user_id] += 1
            
            today = datetime.utcnow().date().isoformat()
            self._in_memory_stats["daily_stats"][today]["messages"] += 1
            
            print(f"📊 Analytics: Message sent - User: {user_id}, Length: {message_length}")
            
        except Exception as e:
            print(f"⚠️ Analytics tracking error: {e}")
    
    def track_session_ended(self, user_id: str, session_id: str, message_count: int, duration_seconds: float):
        """Track when a session ends"""
        try:
            self._in_memory_stats["total_sessions_ended"] += 1
            
            # Store detailed session data in Firebase
            event_data = {
                "event_type": "session_ended",
                "user_id": user_id,
                "session_id": session_id,
                "message_count": message_count,
                "duration_seconds": duration_seconds,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            firebase_service.push_data("/analytics/events", event_data)
            
            print(f"📊 Analytics: Session ended - User: {user_id}, Messages: {message_count}, Duration: {duration_seconds:.1f}s")
            
        except Exception as e:
            print(f"⚠️ Analytics tracking error: {e}")
    
    def get_overview_stats(self) -> Dict[str, Any]:
        """Get overview analytics statistics"""
        return {
            "total_sessions_created": self._in_memory_stats["total_sessions_created"],
            "total_messages_sent": self._in_memory_stats["total_messages_sent"],
            "total_sessions_ended": self._in_memory_stats["total_sessions_ended"],
            "active_sessions": self._in_memory_stats["total_sessions_created"] - self._in_memory_stats["total_sessions_ended"]
        }
    
    def get_personality_stats(self) -> List[Dict[str, Any]]:
        """Get statistics by personality type"""
        stats = []
        for template_id, count in self._in_memory_stats["sessions_by_personality"].items():
            stats.append({
                "template_id": template_id,
                "session_count": count
            })
        
        # Sort by session count (descending)
        stats.sort(key=lambda x: x["session_count"], reverse=True)
        return stats
    
    def get_daily_stats(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily statistics for the last N days"""
        daily_stats = []
        today = datetime.utcnow().date()
        
        for i in range(days):
            date = (today - timedelta(days=i)).isoformat()
            stats = self._in_memory_stats["daily_stats"][date]
            
            daily_stats.append({
                "date": date,
                "sessions": stats["sessions"],
                "messages": stats["messages"],
                "unique_users": len(stats["users"])
            })
        
        # Reverse to show oldest first
        daily_stats.reverse()
        return daily_stats
    
    def get_user_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most active users by message count"""
        user_stats = []
        
        for user_id, message_count in self._in_memory_stats["messages_by_user"].items():
            user_stats.append({
                "user_id": user_id,
                "message_count": message_count
            })
        
        # Sort by message count (descending)
        user_stats.sort(key=lambda x: x["message_count"], reverse=True)
        return user_stats[:limit]
    
    async def get_firebase_stats(self) -> Dict[str, Any]:
        """Get historical statistics from Firebase"""
        try:
            events = firebase_service.get_data("/analytics/events")
            
            if not events:
                return {
                    "total_events": 0,
                    "session_created_count": 0,
                    "session_ended_count": 0,
                    "average_duration": 0,
                    "average_messages_per_session": 0
                }
            
            session_created = 0
            session_ended = 0
            total_duration = 0
            total_messages = 0
            
            for event_id, event_data in events.items():
                if isinstance(event_data, dict):
                    event_type = event_data.get("event_type")
                    
                    if event_type == "session_created":
                        session_created += 1
                    elif event_type == "session_ended":
                        session_ended += 1
                        total_duration += event_data.get("duration_seconds", 0)
                        total_messages += event_data.get("message_count", 0)
            
            avg_duration = total_duration / session_ended if session_ended > 0 else 0
            avg_messages = total_messages / session_ended if session_ended > 0 else 0
            
            return {
                "total_events": len(events),
                "session_created_count": session_created,
                "session_ended_count": session_ended,
                "average_duration": round(avg_duration, 2),
                "average_messages_per_session": round(avg_messages, 2)
            }
            
        except Exception as e:
            print(f"⚠️ Error getting Firebase stats: {e}")
            return {
                "total_events": 0,
                "session_created_count": 0,
                "session_ended_count": 0,
                "average_duration": 0,
                "average_messages_per_session": 0
            }
    
    def get_all_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics data"""
        return {
            "overview": self.get_overview_stats(),
            "personality_stats": self.get_personality_stats(),
            "daily_stats": self.get_daily_stats(7),
            "top_users": self.get_user_activity(10)
        }


# Global analytics service instance
analytics_service = AnalyticsService()

