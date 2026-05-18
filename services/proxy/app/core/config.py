"""
Application configuration.
"""
import base64
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.
    """
    app_name: str = "Guardio Pokemon Stream API"
    stream_secret: str = ""
    pokeproxy_config: str = ""

    @computed_field
    @property
    def decoded_secret_bytes(self) -> bytes:
        try:
            return base64.b64decode(self.stream_secret)
        except Exception:
            raise ValueError("Invalid stream secret format")

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
