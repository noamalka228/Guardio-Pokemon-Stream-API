"""
Application configuration.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.
    """
    app_name: str = "Guardio Pokemon Stream API"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
