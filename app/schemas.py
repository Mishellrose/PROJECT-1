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
    bio: Optional[str] 
    gender: Optional[str] 
    sexual_preference: Optional[str] 
    height: Optional[int] 
    language: Optional[str] 
    class Config():
        orm_mode= True

class HSCreate(BaseModel):
    name: str
    description: str
    image: Optional[str]
    location: Optional[str]

    class Config():
        orm_mode= True
    
    

class HSOut(BaseModel):
    id: int
    name: str
    description: str

class ImageOut(BaseModel):
    inside: bool
    user: UserOut
    profile: UserProfile
    profile_picture: Optional[str]
    images: str
    
    class config():
        orm_mode= True


class ProImageOut(BaseModel):
    profile: ProfileOut
    image_urls: str
    class Config():
        orm_mode= True

class UserHS(BaseModel):
    user_id: int
    hotspot_location: Optional[str]
    class Config():
        orm_mode= True




    



    




