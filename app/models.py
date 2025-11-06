# main_server/models.py
from datetime import datetime
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str
    age: int | None = None
    gender: str | None = None

class HealthData(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str
    timestamp: datetime
    heart_rate: float
    spo2: float
    stress: float
    activity: str

class Alert(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str
    alert_type: str
    timestamp: datetime
