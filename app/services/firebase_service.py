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
        
        # Check if Firebase configuration is available
        if not settings.FIREBASE_PROJECT_ID:
            print("⚠️  Firebase configuration not found. Running in demo mode without Firebase.")
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
            print(f"Error initializing Firebase: {str(e)}")
            raise
    
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
            ref = self.db.reference(path)
            return ref.get()
        except Exception as e:
            print(f"Error getting data from {path}: {str(e)}")
            return None
    
    def set_data(self, path: str, data: Dict[str, Any]) -> bool:
        """Set data in Firebase Realtime Database"""
        try:
            ref = self.db.reference(path)
            ref.set(data)
            return True
        except Exception as e:
            print(f"Error setting data to {path}: {str(e)}")
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
            ref = self.db.reference(path)
            new_ref = ref.push(data)
            return new_ref.key
        except Exception as e:
            print(f"Error pushing data to {path}: {str(e)}")
            return None
    
    def delete_data(self, path: str) -> bool:
        """Delete data from Firebase Realtime Database"""
        try:
            ref = self.db.reference(path)
            ref.delete()
            return True
        except Exception as e:
            print(f"Error deleting data at {path}: {str(e)}")
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


# Global Firebase service instance
firebase_service = FirebaseService()
