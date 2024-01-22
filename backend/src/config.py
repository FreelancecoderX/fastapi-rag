from pydantic_settings import BaseSettings


def get_settings():
    class AppSettings(BaseSettings):
        ENVIRONMENT: str
        FILES: str
        MODEL: str
        MONGO_URI: str
        PINECONE_API_KEY: str
        PINECONE_INDEX: str
        TOGETHER_API_KEY: str

        class Config:
            env_file = ".env.local"
            env_file_encoding = "utf-8"

    settings = AppSettings()
    return settings


settings = get_settings()
