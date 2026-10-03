from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "BiznesLabs"
    environment: str = "development"
    debug: bool = False
    secret_key: str
    access_token_expire_minutes: int = 60
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: list[str] = ["http://localhost:3000"]
    llm_provider: str = "mock"
    embedding_provider: str = "mock"
    stt_provider: str = "mock"
    tts_provider: str = "mock"
    telephony_provider: str = "mock"
    vector_dimensions: int = 1536
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value):
        if isinstance(value, str):
            return [x.strip() for x in value.split(",") if x.strip()]
        return value

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
