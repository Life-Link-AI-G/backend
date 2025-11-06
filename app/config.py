# lifelink-ai/backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379"
    FIREBASE_CREDENTIALS: str = "./firebase-key.json"
    NOTIFICATION_CHANNEL: str = "notifications"
    SECRET_KEY: str = "a_very_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # other settings...
    class Config:
        env_file = ".env"

settings = Settings()
