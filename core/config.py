# core/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""

    # Tavily
    tavily_api_key: str = ""

    # IPinfo
    ipinfo_token: str = ""

    # Clearbit
    clearbit_api_key: str = ""

    # BuiltWith
    builtwith_api_key: str = ""

    # App
    app_env: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
