# main_server/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    TWILIO_SID: str | None = None
    TWILIO_AUTH: str | None = None
    TWILIO_PHONE: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
