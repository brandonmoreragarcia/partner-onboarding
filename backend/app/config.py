from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://localhost/partner_onboarding"
    provider_timeout_seconds: float = 5.0
    partner_id: str = "demo-partner"


settings = Settings()
