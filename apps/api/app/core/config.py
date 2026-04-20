from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://hero:hero@localhost:5432/hero_ai"
    redis_url: str = "redis://localhost:6379/0"

    google_api_key: str = ""
    google_text_model: str = "gemini-2.5-pro"
    google_image_model: str = "gemini-2.5-flash-preview-image-generation"

    clerk_secret_key: str = ""

    local_asset_dir: str = "/app/storage"

    cors_allow_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
