from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

settings = Settings()