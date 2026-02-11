from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    DATABASE_URL: str = "sqlite:///./data/app.db"
    # GOOGLE_API_KEY: str = Field(..., description="Google Gemini API key")


settings = Settings()
