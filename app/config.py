from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"]
    LOG_LEVEL: Literal["DEBUG", "INFO"]

    DB_HOST: str = Field(alias="DB_HOST")
    DB_PORT: int = Field(alias="DB_PORT")
    DB_USER: str = Field(alias="DB_USER")
    DB_PASS: str = Field(alias="DB_PASS")
    DB_NAME: str = Field(alias="DB_NAME")

    BROKER_HOST: str = Field(alias="BROKER_HOST")
    BROKER_PORT: str = Field(alias="BROKER_PORT")
    BROKER_USER: str = Field(alias="BROKER_USER")
    BROKER_PASSWORD: str = Field(alias="BROKER_PASSWORD")

    SECRET_KEY: str = Field(alias="SECRET_KEY")
    ALGORITHM: str = Field(alias="ALGORITHM")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(alias="REFRESH_TOKEN_EXPIRE_DAYS")

    SMTP_HOST: str = Field(alias="SMTP_HOST")
    SMTP_PORT: int = Field(alias="SMTP_PORT")
    SMTP_USER: str = Field(alias="SMTP_USER")
    SMTP_PASS: str = Field(alias="SMTP_PASS")
    REDIS_HOST: str = Field(alias="REDIS_HOST")
    REDIS_PORT: int = Field(alias="REDIS_PORT")

    TEST_DB_HOST: str = Field(alias="TEST_DB_HOST")
    TEST_DB_PORT: int = Field(alias="TEST_DB_PORT")
    TEST_DB_USER: str = Field(alias="TEST_DB_USER")
    TEST_DB_PASS: str = Field(alias="TEST_DB_PASS")
    TEST_DB_NAME: str = Field(alias="TEST_DB_NAME")

    MONGO_HOST: str = Field(alias="MONGO_HOST")
    MONGO_PORT: int = Field(alias="MONGO_PORT")
    MONGO_USER: str = Field(alias="MONGO_USER")
    MONGO_PASSWORD: str = Field(alias="MONGO_PASSWORD")
    MONGO_NAME: str = Field(alias="MONGO_NAME")

    S3_HOST: str = Field(alias="S3_HOST")
    S3_ACCESS_KEY: str = Field(alias="S3_ACCESS_KEY")
    S3_SECRET_KEY: str = Field(alias="S3_SECRET_KEY")
    S3_BUCKET_NAME: str = Field(alias="S3_BUCKET_NAME")

    FLOWER_BASIC_AUTH: str = Field(alias="FLOWER_BASIC_AUTH")

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def TEST_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"

    @property
    def BROKER_URL(self):
        return f"amqp://{self.BROKER_USER}:{self.BROKER_PASSWORD}@{self.BROKER_HOST}:{self.BROKER_PORT}/"

    @property
    def MONGO_URL(self):
        return f"{self.MONGO_NAME}://{self.MONGO_HOST}:{self.MONGO_PORT}"

    @property
    def S3_URL(self):
        return f"https://{self.S3_HOST}"

    @property
    def S3_PREFIX(self):
        return f"https://{self.S3_HOST}/{self.S3_BUCKET_NAME}/"

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
