# main_server/database.py
from sqlmodel import SQLModel, create_engine, Session
from main_server.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)

def init_db():
    from main_server.models import User, HealthData, Alert
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
