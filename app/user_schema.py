from pydantic import BaseModel, Field
from typing import List, Optional

class UserSchema(BaseModel):
    user_id: str
    age: int
    gender: str
    emergency_contacts: List[str]
    
class UserCreate(BaseModel):
    user_id: str
    age: int
    gender: str
    emergency_contacts: List[str]
    password: str

class UserLogin(BaseModel):
    user_id: str
    password: str

# --- ADD THIS NEW CLASS ---
class RiskAnalysisRequest(BaseModel):
    """
    Defines the request body for the on-demand risk analysis endpoint.
    """
    user_id: Optional[str] = "TEMP_USER"
    age: int
    gender: str
    weight_kg: float
    height_cm: float
    fitness_level: str
    current_activity: str # e.g., "resting", "stressed", "running"