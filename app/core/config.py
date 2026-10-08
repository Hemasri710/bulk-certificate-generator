import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base Directory of the repository
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application Settings loaded from environment variables or defaults."""

    APP_NAME: str = "Bulk Certificate Generator API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Database connection URL
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/certificate_db"

    # Base directory for storing generated certificates
    STORAGE_DIR: Path = BASE_DIR / "storage" / "certificates"

    # Input validation limit
    MAX_RECIPIENTS_PER_JOB: int = 1000

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# Ensure storage directory exists on startup
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
