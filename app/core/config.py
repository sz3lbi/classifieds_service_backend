import logging
import sys
from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, HttpUrl, PostgresDsn, RedisDsn, validator
from pydantic.networks import AnyHttpUrl


class Settings(BaseSettings):
    # Authorization
    access_token_expire_minutes: int = 7 * 24 * 60  # 7 days

    # Images upload
    images_max_size: int = 5_000_000  # 5 MB
    images_content_types: List[str] = ["image/png", "image/jpeg"]
    images_upload_path: str = "uploads/"

    # Logging config
    logging_path: str = "logs/{time}.log"
    logging_level: int = logging.INFO
    logging_rotation: str = "12:00"
    logging_retention: str = "3 months"
    logging_format: str = (
        "<level>{level: <8}</level> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
        "request id: {extra[request_id]} - <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    )

    # Databases
    test_database_url: Optional[PostgresDsn]
    database_url: PostgresDsn
    redis_url: RedisDsn = "redis://@localhost:6379/"

    @validator("database_url", pre=True)
    def build_test_database_url(cls, v: Optional[str], values: Dict[str, Any]):
        if "pytest" in sys.modules:
            if not values.get("test_database_url"):
                raise Exception(
                    "pytest detected, but test_database_url is not set in environment"
                )
            return values["test_database_url"]
        return v

    # Others
    project_name: str = "Classifieds service"
    backend_cors_origins: List[AnyHttpUrl] = []
    password_min_length: int = 12
    classified_expire_time_days: int = 30
    secret_key: str

    class Config:
        env_file = ".env"
        fields = {"redis_url": {"env": ["redis_url", "redistogo_url"]}}


settings = Settings()
