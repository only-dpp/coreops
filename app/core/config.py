from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    DATABASE_URL: str
    REDIS_URL: str

    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int = 60

    DISCORD_WEBHOOK_URL: str | None = None
    DISCORD_BOT_NAME: str = "CoreOps"
    ALERT_ON_FAILURES: int = 1

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASS: str
    SMTP_FROM: str

    SESSION_SECRET: str
    SESSION_HTTPS_ONLY: bool = False
    SESSION_MAX_AGE_SECONDS: int = 60 * 60 * 8

    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str


settings = Settings()