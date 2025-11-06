from pydantic import BaseModel, Field
from typing import List

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
