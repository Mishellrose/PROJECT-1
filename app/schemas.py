# from fastapi import EmailStr
# from datetime import datetime
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    class Config():
        orm_mode= True

class Token(BaseModel):
    access_token: str
    token_type: str

class token_data(BaseModel):
    id: Optional[str] = None
