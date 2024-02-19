from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    API_KEY: SecretStr
    YADISK_ID: SecretStr
    YADISK_SECRET: SecretStr
    YADISK_TOKEN: SecretStr
    NEUROAPI_KEY: SecretStr
    DATABASE_FILE: str
    DATABASE_NAME_FOR_YADISK: str
    CHATGPT_PROMPT: str
    ADMINISTRATOR_01: int
    ADMINISTRATOR_02: int
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()
