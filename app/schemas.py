# from fastapi import EmailStr
# from datetime import datetime
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    created_at: datetime
    class Config():
        orm_mode= True

class Token(BaseModel):
    access_token: str
    token_type: str

class token_data(BaseModel):
    id: Optional[int] = None

class UserProfile(BaseModel):   
    
    bio: str
    gender: str
    sexual_preference: str
    height: int
    language: str
    class Config():
        orm_mode= True

class ProfileOut(BaseModel):
    profile: UserProfile
    user: UserOut

    class Config():
        orm_mode=True

class PartialProf(BaseModel):
    bio: Optional[str] = None
    gender: Optional[str] = None
    sexual_preference: Optional[str] = None
    height: Optional[int] = None
    language: Optional[str] = None

class CreateHS(BaseModel):
    name: str
    description: str
    

class HSOut(BaseModel):
    id: int
    name: str
    description: str
    

    


    



    




