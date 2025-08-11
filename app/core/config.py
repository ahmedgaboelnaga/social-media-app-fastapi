from typing import Annotated
from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env.example")


@lru_cache
def get_settings():
    return Settings()  # type: ignore


settings = Settings()  # type: ignore
SettingsDep = Annotated[Settings, Depends(get_settings)]
