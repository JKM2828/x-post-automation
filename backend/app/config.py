from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # X API Credentials
    X_API_KEY: Optional[str] = None
    X_API_SECRET: Optional[str] = None
    X_BEARER_TOKEN: Optional[str] = None
    X_OAUTH_CLIENT_ID: Optional[str] = None
    X_OAUTH_CLIENT_SECRET: Optional[str] = None
    X_CALLBACK_URL: str = "http://localhost:8000/auth/x/callback"
    
    # AI Configuration
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    AI_PROVIDER: str = "gemini"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    
    # Database
    DATABASE_URL: str = "postgresql://xpostuser:xpostpass@postgres:5432/xpostdb"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Application
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # URLs
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Rate Limits
    RATE_LIMIT_BUFFER: int = 10
    MAX_POSTS_PER_HOUR: int = 50
    
    # ML Model
    MODEL_PATH: str = "./models/viral_predictor.pkl"
    RETRAIN_INTERVAL_DAYS: int = 7
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
