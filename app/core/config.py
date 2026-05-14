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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings() # type: ignore[call-arg]

assert settings.DATABASE_URL, "DATABASE_URL is not set in the .env file"
