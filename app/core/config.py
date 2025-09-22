"""
Application configuration settings
"""

from typing import List
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
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID: str
    FIREBASE_DATABASE_URL: str
    FIREBASE_STORAGE_BUCKET: str
    FIREBASE_CLIENT_EMAIL: str
    FIREBASE_PRIVATE_KEY_ID: str
    FIREBASE_PRIVATE_KEY: str
    FIREBASE_CLIENT_ID: str
    FIREBASE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    FIREBASE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    FIREBASE_AUTH_PROVIDER_X509_CERT_URL: str = "https://www.googleapis.com/oauth2/v1/certs"
    FIREBASE_CLIENT_X509_CERT_URL: str
    FIREBASE_UNIVERSE_DOMAIN: str = "googleapis.com"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = ""
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env file


settings = Settings()
