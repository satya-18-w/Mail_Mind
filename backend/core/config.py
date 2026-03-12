from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_mail_agent"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/ai_mail_agent"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Gmail OAuth2
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_redirect_uri: str = "http://localhost:8000/auth/callback"

    # Groq API (Free tier)
    groq_api_key: str = ""

    # App
    app_env: str = "development"
    secret_key: str = "change-this-to-a-random-secret-key"

    # JWT
    jwt_secret_key: str = "ai-mail-agent-jwt-secret-2026"
    jwt_expiry_days: int = 7

    # Frontend
    frontend_url: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
