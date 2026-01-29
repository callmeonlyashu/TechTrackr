import logging
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server Configuration
    environment: str = "development"
    debug: bool = True
    host: str = "localhost"
    port: int = 8000
    
    # Logging Configuration
    log_level: str = "INFO"
    
    # CORS Configuration
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()