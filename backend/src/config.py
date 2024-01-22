from pydantic_settings import BaseSettings
from pydantic import SecretStr


class AppSettings(BaseSettings):
    ENVIRONMENT: str
    DB_PASSWORD: SecretStr

    class Config:
        env_file = "env.local"
        env_file_encoding = "utf-8"
        secrets_dir = "./secrets"
        # env_prefix=""
