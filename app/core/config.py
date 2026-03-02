<<<<<<< HEAD
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

=======
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

>>>>>>> 21599b0b39eba37876fc43d9838497fbe2974000
settings = Settings()