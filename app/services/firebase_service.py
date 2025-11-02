"""
Firebase service for database operations
"""

import json
from typing import Dict, Any, Optional, List
import firebase_admin
from firebase_admin import credentials, db, storage
from app.core.config import settings


class FirebaseService:
    """Firebase service for database and storage operations"""
    
    def __init__(self):
        self._db = None
        self._storage = None
        self._initialized = False
    
    def initialize(self):
        """Initialize Firebase Admin SDK"""
        if self._initialized:
            return
        
        # Check if Firebase configuration is available and valid
        if (not settings.FIREBASE_PROJECT_ID or 
            settings.FIREBASE_PROJECT_ID == "your-firebase-project-id" or
            not settings.FIREBASE_PRIVATE_KEY or
            settings.FIREBASE_PRIVATE_KEY == "-----BEGIN PRIVATE KEY-----\\nYour private key here\\n-----END PRIVATE KEY-----\\n"):
            print("[WARN] Firebase configuration not found or using default values. Running in demo mode without Firebase.")
            self._initialized = True
            return
        
        try:
            # Create credentials from environment variables
            cred_dict = {
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
                "client_id": settings.FIREBASE_CLIENT_ID,
                "auth_uri": settings.FIREBASE_AUTH_URI,
                "token_uri": settings.FIREBASE_TOKEN_URI,
                "auth_provider_x509_cert_url": settings.FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
                "client_x509_cert_url": settings.FIREBASE_CLIENT_X509_CERT_URL,
                "universe_domain": settings.FIREBASE_UNIVERSE_DOMAIN
            }
            
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                'databaseURL': settings.FIREBASE_DATABASE_URL,
                'storageBucket': settings.FIREBASE_STORAGE_BUCKET
            })
            
            # Initialize database and storage references
            self._db = db
            self._storage = storage
            self._initialized = True
            
            print("Firebase initialized successfully")
            
        except Exception as e:
            print(f"[WARN] Error initializing Firebase: {str(e)}")
            print("[WARN] Continuing in demo mode without Firebase.")
            self._initialized = True
            return
    
    @property
    def db(self):
        """Get database reference"""
        if not self._initialized:
            self.initialize()
        return self._db
    
    @property
    def storage(self):
        """Get storage reference"""
        if not self._initialized:
            self.initialize()
        return self._storage
    
    # Database operations
    def get_data(self, path: str) -> Optional[Dict[str, Any]]:
        """Get data from Firebase Realtime Database"""
        try:
            if not self._initialized or not self._db:
                return None
            ref = self.db.reference(path)
            return ref.get()
        except Exception as e:
            print(f"[WARN] Error getting data from {path}: {str(e)}")
            return None
    
    def set_data(self, path: str, data: Dict[str, Any]) -> bool:
        """Set data in Firebase Realtime Database"""
        try:
            if not self._initialized or not self._db:
                return False
            ref = self.db.reference(path)
            ref.set(data)
            return True
        except Exception as e:
            print(f"[WARN] Error setting data to {path}: {str(e)}")
            return False
    
    def update_data(self, path: str, data: Dict[str, Any]) -> bool:
        """Update data in Firebase Realtime Database"""
        try:
            ref = self.db.reference(path)
            ref.update(data)
            return True
        except Exception as e:
            print(f"Error updating data at {path}: {str(e)}")
            return False
    
    def push_data(self, path: str, data: Dict[str, Any]) -> Optional[str]:
        """Push data to Firebase Realtime Database and return the key"""
        try:
            if not self._initialized or not self._db:
                print(f"[WARN] Firebase not initialized, skipping push to {path}")
                return None
            ref = self.db.reference(path)
            new_ref = ref.push(data)
            return new_ref.key
        except Exception as e:
            print(f"Error pushing data to {path}: {str(e)}")
            return None
    
    def delete_data(self, path: str) -> bool:
        """Delete data from Firebase Realtime Database"""
        try:
            if not self._initialized or not self._db:
                return False
            ref = self.db.reference(path)
            ref.delete()
            return True
        except Exception as e:
            print(f"[WARN] Error deleting data at {path}: {str(e)}")
            return False
    
    def listen_to_changes(self, path: str, callback):
        """Listen to real-time changes in Firebase Realtime Database"""
        try:
            ref = self.db.reference(path)
            ref.listen(callback)
        except Exception as e:
            print(f"Error listening to changes at {path}: {str(e)}")
    
    # Storage operations
    def upload_file(self, file_path: str, destination_path: str) -> Optional[str]:
        """Upload file to Firebase Storage"""
        try:
            bucket = self.storage.bucket()
            blob = bucket.blob(destination_path)
            blob.upload_from_filename(file_path)
            return blob.public_url
        except Exception as e:
            print(f"Error uploading file {file_path}: {str(e)}")
            return None
    
    def download_file(self, source_path: str, destination_path: str) -> bool:
        """Download file from Firebase Storage"""
        try:
            bucket = self.storage.bucket()
            blob = bucket.blob(source_path)
            blob.download_to_filename(destination_path)
            return True
        except Exception as e:
            print(f"Error downloading file {source_path}: {str(e)}")
            return False
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from Firebase Storage"""
        try:
            bucket = self.storage.bucket()
            blob = bucket.blob(file_path)
            blob.delete()
            return True
        except Exception as e:
            print(f"Error deleting file {file_path}: {str(e)}")
            return False
    
    def get_file_url(self, file_path: str) -> Optional[str]:
        """Get public URL for a file in Firebase Storage"""
        try:
            bucket = self.storage.bucket()
            blob = bucket.blob(file_path)
            return blob.public_url
        except Exception as e:
            print(f"Error getting URL for file {file_path}: {str(e)}")
            return None
    
    # Mock methods for profile and connection endpoints
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile - mock implementation"""
        return {
            "id": user_id,
            "displayName": "Mock User",
            "email": "user@example.com",
            "photoURL": None,
            "interests": ["music", "sports"],
            "age": 25,
            "location": "New York"
        }
    
    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile - mock implementation"""
        profile = await self.get_user_profile(user_id)
        profile.update(updates)
        return profile
    
    async def delete_user_account(self, user_id: str) -> bool:
        """Delete user account - mock implementation"""
        return True
    
    async def get_blocked_users(self, user_id: str) -> List[Dict[str, Any]]:
        """Get blocked users - mock implementation"""
        return []
    
    async def block_user(self, user_id: str, target_user_id: str) -> bool:
        """Block user - mock implementation"""
        return True
    
    async def unblock_user(self, user_id: str, target_user_id: str) -> bool:
        """Unblock user - mock implementation"""
        return True
    
    async def check_username_availability(self, username: str) -> bool:
        """Check username availability - mock implementation"""
        return True
    
    async def create_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create user profile - mock implementation"""
        profile = await self.get_user_profile(user_id)
        profile.update(profile_data)
        return profile
    
    async def get_profile_stats(self, user_id: str) -> Dict[str, Any]:
        """Get profile stats - mock implementation"""
        return {
            "views": 0,
            "likes": 0,
            "connections": 0
        }
    
    async def search_profiles(self, search_params: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Search profiles - mock implementation"""
        return []
    
    async def get_trending_interests(self) -> List[str]:
        """Get trending interests - mock implementation"""
        return ["music", "sports", "travel", "food", "technology"]
    
    async def get_user_gallery(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user gallery - mock implementation"""
        return []
    
    async def set_main_picture(self, user_id: str, filename: str) -> bool:
        """Set main picture - mock implementation"""
        return True
    
    async def remove_gallery_picture(self, user_id: str, filename: str) -> bool:
        """Remove gallery picture - mock implementation"""
        return True
    
    async def purchase_profile_boost(self, user_id: str, cost: int, duration: float) -> Dict[str, Any]:
        """Purchase profile boost - mock implementation"""
        return {
            "id": f"boost_{user_id}",
            "cost": cost,
            "duration": duration,
            "expiresAt": "2024-01-01T00:00:00Z"
        }
    
    async def cancel_profile_boost(self, user_id: str) -> bool:
        """Cancel profile boost - mock implementation"""
        return True
    
    async def get_boosted_profiles(self) -> List[Dict[str, Any]]:
        """Get boosted profiles - mock implementation"""
        return []
    
    # Connection methods
    async def send_friend_request(self, user_id: str, to_user_id: str, message: str = None, request_type: str = None) -> Dict[str, Any]:
        """Send friend request - mock implementation"""
        return {
            "id": f"request_{user_id}_{to_user_id}",
            "fromUserId": user_id,
            "toUserId": to_user_id,
            "message": message,
            "type": request_type,
            "status": "pending"
        }
    
    async def accept_friend_request(self, connection_id: str, user_id: str) -> Dict[str, Any]:
        """Accept friend request - mock implementation"""
        return {
            "id": connection_id,
            "status": "accepted"
        }
    
    async def reject_friend_request(self, connection_id: str, user_id: str) -> bool:
        """Reject friend request - mock implementation"""
        return True
    
    async def cancel_friend_request(self, connection_id: str, user_id: str) -> bool:
        """Cancel friend request - mock implementation"""
        return True
    
    async def get_incoming_friend_requests(self, user_id: str) -> List[Dict[str, Any]]:
        """Get incoming friend requests - mock implementation"""
        return []
    
    async def get_outgoing_friend_requests(self, user_id: str) -> List[Dict[str, Any]]:
        """Get outgoing friend requests - mock implementation"""
        return []
    
    async def get_friends(self, user_id: str) -> List[Dict[str, Any]]:
        """Get friends - mock implementation"""
        return []
    
    async def remove_friend(self, user_id: str, friend_user_id: str) -> bool:
        """Remove friend - mock implementation"""
        return True
    
    async def get_connection_status(self, user_id: str, target_user_id: str) -> Dict[str, Any]:
        """Get connection status - mock implementation"""
        return {
            "status": "none",
            "isFriend": False,
            "hasPendingRequest": False
        }


# Global Firebase service instance
firebase_service = FirebaseService()
