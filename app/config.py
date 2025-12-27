from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    GCP_BUCKET_NAME: str
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB default
    ALLOWED_FILE_TYPES: Optional[str] = None  # None means all types allowed
    PORT: int = 8080


# Global settings instance
settings = Settings()


def get_allowed_extensions() -> Optional[list[str]]:
    """Parse allowed file types from environment variable."""
    if settings.ALLOWED_FILE_TYPES:
        return [ext.strip().lower() for ext in settings.ALLOWED_FILE_TYPES.split(",")]
    return None

