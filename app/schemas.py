# from fastapi import EmailStr
# from datetime import datetime
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional,Literal

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
    
    profile: UserProfile
    user: UserOut
    profile_picture: Optional[str]
    

    class Config():
        orm_mode= True


class ProImageOut(BaseModel):
    profile: UserProfile
    user: UserOut
    profile_picture: Optional[str]
    images: Optional[list]
    class Config():
        orm_mode= True

class UserHS(BaseModel):
    user_id: int
    hotspot_location: Optional[str]
    class Config():
        orm_mode= True

class SwipeIn(BaseModel):
    user_id: int
    user_location: str
    swiped_on_id: int
    direction: str
    class Config():
        orm_mode= True

class SwipeOut(BaseModel):
    user_id: int
    user_name: str
    user_location: str
    matched_user_id: int
    matched_user_name: str
    balance_swipe_rights: int
    
    class Config():
        orm_mode= True

class MatchOut(BaseModel):
    matched_user: UserOut
    matched_profile: UserProfile

    class Config():
        orm_mode= True

class SubscribePlanIn(BaseModel):
    user_id:int
    plan_type: Literal["1_month", "3_month"]   
    class Config():
        orm_mode= True

class PaymentVerifyIn(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    



    




