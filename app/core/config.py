from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool
    API_V1_PREFIX: str
    DATABASE_URL: str
    REDIS_URL: str
    TEST_DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRY_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRY_DAYS: int
    JWT_RESET_PASSWORD_TOKEN_EXPIRY_MINUTES: int
    MAIL_HOST: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    APP_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings() # type: ignore[call-arg]

assert settings.DATABASE_URL, "DATABASE_URL is not set in the .env file"
