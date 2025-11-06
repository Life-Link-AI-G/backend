# app/core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379"
    PROJECT_NAME: str = "LifeLink AI Backend"
    BACKEND_PORT: int = 8000

    class Config:
        env_file = ".env"

settings = Settings()
