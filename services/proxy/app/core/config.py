"""
Application configuration.
"""
import base64
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.
    """
    app_name: str = "Guardio Pokemon Stream API"
    stream_secret: str = ""
    pokeproxy_config: str = "config.json"
    decoded_secret_bytes: bytes = b""

    # TODO: replace this __init__ block with cleaner code
    def __init__(self, **values):
        super().__init__(**values)
        try:
            self.decoded_secret_bytes = base64.b64decode(self.stream_secret)
        except Exception:
            raise ValueError("Invalid stream secret format")

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
