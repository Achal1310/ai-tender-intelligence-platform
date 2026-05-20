from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Tender Intelligence Platform"
    app_env: str = "development"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/ai_tender"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    demo_mode: bool = True
    uploads_dir: str = "uploads"
    reports_dir: str = "reports"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
