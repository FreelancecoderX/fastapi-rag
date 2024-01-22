from pydantic_settings import BaseSettings
from pydantic import SecretStr

class AppSettings(BaseSettings):
    ENVIRONMENT: str
    db_password: SecretStr

    class Config:
        env_file= ".env"
        env_file_encoding= "utf-8"