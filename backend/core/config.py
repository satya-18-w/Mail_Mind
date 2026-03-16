from pydantic import field_validator
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

    # Runtime
    port: int = 8000
    auto_create_tables: bool = False
    db_init_timeout_seconds: int = 12

    # --- Validators: normalise DB URL schemes regardless of what Railway injects ---

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_async_scheme(cls, v: str) -> str:
        """Ensure DATABASE_URL always uses the asyncpg driver scheme.
        Railway's ${{Postgres.DATABASE_URL}} returns plain postgresql://.
        """
        if isinstance(v, str):
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
        return v

    @field_validator("database_url_sync", mode="before")
    @classmethod
    def fix_sync_scheme(cls, v: str) -> str:
        """Ensure DATABASE_URL_SYNC never has the asyncpg driver scheme."""
        if isinstance(v, str):
            if v.startswith("postgresql+asyncpg://"):
                return v.replace("postgresql+asyncpg://", "postgresql://", 1)
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql://", 1)
        return v

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
