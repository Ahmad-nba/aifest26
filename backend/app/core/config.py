from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Use a file-based SQLite DB by default
    # Local (non-docker): creates ./data/app.db relative to where backend runs
    # Docker: we’ll set DATABASE_URL=sqlite:////app/data/app.db
    DATABASE_URL: str = "sqlite:///./data/app.db"

    # For later (agent phase)
    OPENAI_API_KEY: str | None = None
    LLM_MODEL_NAME: str = "gpt-4o-mini"


settings = Settings()
