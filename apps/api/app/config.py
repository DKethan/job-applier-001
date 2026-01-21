from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    env: str = "local"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_allowed_origins: str = "http://localhost:3000"
    
    database_url: str = ""  # Not used with MongoDB
    mongodb_uri: str
    mongodb_db_name: str = "jobcopilot"
    mongodb_test_db: str = "test_db"
    redis_url: str = "redis://redis:6379/0"
    
    storage_provider: str = "local"
    storage_local_dir: str = "./data/uploads"  # Default to local project directory
    
    encryption_key_base64: str
    jwt_secret: str
    jwt_issuer: str = "jobcopilot"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    llm_provider: str = "openai"
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    
    log_level: str = "INFO"
    
    playwright_enabled: bool = True
    playwright_headless: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",")]

    def validate_required(self):
        """Validate required environment variables"""
        required = [
            "mongodb_uri",
            "encryption_key_base64",
            "jwt_secret",
            "openai_api_key",
        ]
        missing = [var for var in required if not getattr(self, var) or getattr(self, var) == "CHANGE_ME"]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        return True


settings = Settings()
settings.validate_required()
