
from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "HiveSync Starter"
    database_url: str = "sqlite:///./hivesync.db"
    secret_key: str = "CHANGE_ME_TO_A_RANDOM_SECRET"
    access_token_expire_minutes: int = 60 * 24

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
