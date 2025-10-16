from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="./environments/.env.dev")

    MODE: Literal["DEV", "TEST", "PROD"] = "DEV"
    VISIBILITY_DOCUMENTATION: bool = False

    WEB_APP_URL: str = "http://localhost:3000"

    SECRET_KEY: str = "secret"
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    DB_HOST: str = "localhost"
    DB_NAME: str = "dev_db_construct"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASS: str = "postgres"

    ACCESS_KEY_S3: str
    SECRET_KEY_S3: str
    ENDPOINT_URL_S3: str
    BUCKET_NAME_S3: str
    DOMAIN_S3: str

    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"
    
    LLM_URL: str
    
    ACCESS_EXPIRES_AT_MIN: int = 480

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
