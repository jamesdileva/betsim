from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BETSIM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db_path: Path = Path.home() / ".betsim" / "betsim.db"
    port: int = 8000
    theoddsapi_api_key: str = ""


settings = Settings()
