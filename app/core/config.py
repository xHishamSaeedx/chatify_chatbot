"""
Application configuration settings
"""

from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Basic app settings
    PROJECT_NAME: str = "Chatify Chatbot"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A FastAPI chatbot service with Firebase integration"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: Optional[List[str]] = None
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        import os
        return os.getenv("ENVIRONMENT", self.ENVIRONMENT).lower() in ["production", "prod"]
    
    # Server settings
    HOST: str = "0.0.0.0"  # Use 0.0.0.0 for deployment (Render, Docker, etc.)
    PORT: int = 8000  # Default port, can be overridden by environment variable
    
    @property
    def get_port(self) -> int:
        """Get the port from environment variable or default"""
        import os
        return int(os.getenv("PORT", self.PORT))
    
    @property
    def get_host(self) -> str:
        """Get the appropriate host based on environment"""
        # For local development, use localhost to avoid Windows binding issues
        if not self.is_production and self.DEBUG:
            return "127.0.0.1"
        # For production/deployment, use 0.0.0.0
        return self.HOST
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_DATABASE_URL: Optional[str] = None
    FIREBASE_STORAGE_BUCKET: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    FIREBASE_PRIVATE_KEY_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_CLIENT_ID: Optional[str] = None
    FIREBASE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    FIREBASE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    FIREBASE_AUTH_PROVIDER_X509_CERT_URL: str = "https://www.googleapis.com/oauth2/v1/certs"
    FIREBASE_CLIENT_X509_CERT_URL: Optional[str] = None
    FIREBASE_UNIVERSE_DOMAIN: str = "googleapis.com"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = ""
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if v is None:
            return ["http://localhost:3000", "http://localhost:8080", "http://localhost:8000"]
        if isinstance(v, str):
            if v.startswith("["):
                import json
                return json.loads(v)
            else:
                return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env file


settings = Settings()
