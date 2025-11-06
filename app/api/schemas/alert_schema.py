# app/api/schemas/alert_schema.py
from pydantic import BaseModel
from typing import List, Optional

class Contact(BaseModel):
    name: Optional[str] = None
    phone: str

class Alert(BaseModel):
    user_id: str
    message: str
    contacts: List[Contact]