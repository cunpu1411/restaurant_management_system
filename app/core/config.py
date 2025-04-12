import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import secrets

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Restaurant Management System"
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost/restaurant_management")
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_hex(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list = ["http://localhost", "http://localhost:8000", "http://localhost:3000"]
    
    class Config:
        case_sensitive = True

settings = Settings()