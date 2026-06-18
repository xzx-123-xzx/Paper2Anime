import os
from pathlib import Path
from typing import List
from common.config import Config as CommonConfig

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
STORAGE_PATH = PROJECT_ROOT / "storage"
STORAGE_PATH.mkdir(parents=True, exist_ok=True)


class Settings(CommonConfig):
    APP_NAME: str = "Paper2Anime"
    APP_ENV: str = "development"
    DEBUG: bool = True

    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"

    CORS_ORIGINS: List[str] = ["*"]

    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS: List[str] = ["txt", "docx", "pdf"]

    DEFAULT_QUALITY_PRESET: str = "standard"
    MAX_CONCURRENT_TASKS: int = 3

    DEFAULT_ASPECT_RATIO: str = "16:9"
    DEFAULT_RESOLUTION: str = "1920x1080"
    DEFAULT_FPS: int = 24

    QUALITY_THRESHOLD: float = 0.75
    MAX_RETRIES: int = 3

    STORAGE_TYPE: str = "local"
    LOCAL_STORAGE_PATH: str = str(STORAGE_PATH)

    SECRET_KEY: str = "your-secret-key-change-in-production"

    LOG_FILE: str = str(PROJECT_ROOT / "logs" / "app.log")


settings = Settings()
