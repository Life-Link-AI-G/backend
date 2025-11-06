# app/api/schemas/health_schema.py
from pydantic import BaseModel, Field
from typing import Optional

class HealthData(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    heart_rate: int = Field(..., ge=0, le=250)
    spo2: float = Field(..., ge=50, le=100)
    motion: str = Field(..., description="still | walking | running | fall")
    stress: Optional[float] = None
    sleep_stage: Optional[str] = None