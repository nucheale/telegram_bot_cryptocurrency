from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    API_KEY: SecretStr
    YADISK_ID: SecretStr
    YADISK_SECRET: SecretStr
    YADISK_TOKEN: SecretStr
    DATABASE_FILE: str
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()
