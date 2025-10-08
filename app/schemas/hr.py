# schemas/hr.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class HRBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None

class HRCreate(HRBase):
    password: str  # plain password

class HRUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class HRResponse(HRBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    created_by_id: int

    class Config:
        orm_mode = True

class HRLogin(BaseModel):
    email: EmailStr
    password: str

# --------------------
# Token Schema (for login response)
# --------------------
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    user_email: str
    role:str
    user_name:str
