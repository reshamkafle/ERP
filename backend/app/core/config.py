from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SECRET_KEY = "change-me-in-production-use-openssl-rand-hex-32"
DEFAULT_ADMIN_PASSWORD = "changeme123"
DEFAULT_DATABASE_URL = "postgresql+asyncpg://erp:erp@localhost:5432/erp"
DEPLOYED_ENVIRONMENTS = frozenset({"production", "staging"})


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    database_url: str = DEFAULT_DATABASE_URL
    secret_key: str = DEFAULT_SECRET_KEY
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    admin_email: str = "admin@example.com"
    admin_password: str = DEFAULT_ADMIN_PASSWORD
    # Shared password for backend/scripts/seed_rbac_users.py (dev/demo only).
    seed_user_password: str = "SeedUser123!"
    # When false, startup skips BOM/garment/module demo seeds (use with scripts/clear_database.py).
    seed_demo_data: bool = True

    # OpenAI-compatible LLM (Ollama, vLLM, LiteLLM). Leave base URL empty for rule-only procurement agents.
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    # Comma-separated hostnames allowed for LLM_BASE_URL (required when LLM_BASE_URL is set).
    llm_allowed_hosts: str = ""

    # Login brute-force protection
    login_max_failures: int = 5
    login_lockout_minutes: int = 15

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def is_deployed(self) -> bool:
        return self.environment.lower() in DEPLOYED_ENVIRONMENTS

    @property
    def llm_allowed_host_list(self) -> list[str]:
        return [h.strip().lower() for h in self.llm_allowed_hosts.split(",") if h.strip()]

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        if self.llm_base_url.strip() and not self.llm_allowed_host_list:
            raise ValueError(
                "LLM_ALLOWED_HOSTS must be set when LLM_BASE_URL is configured",
            )
        if not self.is_deployed:
            return self
        if self.secret_key == DEFAULT_SECRET_KEY or len(self.secret_key) < 32:
            raise ValueError(
                "SECRET_KEY must be set to a unique random value of at least 32 characters "
                "in staging/production (e.g. openssl rand -hex 32)",
            )
        if self.admin_password == DEFAULT_ADMIN_PASSWORD:
            raise ValueError(
                "ADMIN_PASSWORD must be changed from the default in staging/production",
            )
        if self.database_url == DEFAULT_DATABASE_URL:
            raise ValueError(
                "DATABASE_URL must not use default credentials in staging/production",
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
