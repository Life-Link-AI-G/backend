# lifelink-ai/backend/app/core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379"
    FIREBASE_CREDENTIALS: str = "./firebase-key.json"
    NOTIFICATION_CHANNEL: str = "notifications"
    # other settings...
    class Config:
        env_file = ".env"

settings = Settings()
