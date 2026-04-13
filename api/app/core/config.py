from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Personal Knowledge Memory API"
    OPENROUTER_API_KEY: SecretStr
    MODEL_NAME: str = "openrouter/free"
    DATABASE_URL: str


settings = Settings()