from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_DIR / ".env"), ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # API Base
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "WhatsApp Task Tracker"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "super_secret_development_key_change_in_production"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Database
    DATABASE_URL: str = "postgresql://postgres:root@localhost:5432/attendance_tracker?schema=public"

    # Meta WhatsApp Cloud API
    META_ACCESS_TOKEN: str = "placeholder_access_token"
    META_VERIFY_TOKEN: str = "placeholder_verify_token"
    META_PHONE_NUMBER_ID: str = "100000000000000"
    META_WHATSAPP_API_VERSION: str = "v20.0"

    # LLM Parser
    LLM_PROVIDER: str = "gemini"  # "gemini" | "openai"
    LLM_API_KEY: str = "placeholder_llm_key"
    LLM_MODEL: str = "gemini-1.5-flash"

    @property
    def meta_graph_url(self) -> str:
        return f"https://graph.facebook.com/{self.META_WHATSAPP_API_VERSION}/{self.META_PHONE_NUMBER_ID}/messages"


settings = Settings()
