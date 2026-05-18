"""
Application configuration.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.
    """
    app_name: str = "Guardio Pokemon Stream API"
    stream_secret: str = ""
    pokeproxy_config: str = "config.json"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
