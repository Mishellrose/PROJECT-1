from sqlalchemy import text
from fastapi import Depends,HTTPException,status
from app import schemas,models
from app.config import settings
from datetime import datetime,timedelta
from sqlalchemy.orm import Session
from jose import JWTError,jwt
from app.database import get_db
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme=OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY= settings.secret_key
ALGORITHM= settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=settings.access_token_expire_minutes

def create_access_token(data:dict):
    to_encode=data.copy()
    expire= datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp" : expire})
    encoded_jwt= jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str,credentials_exception):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        id: str=payload.get("user_id")
        if not id:
            raise credentials_exception
        token_data=schemas.token_data(id=id)
    except JWTError:
        raise credentials_exception
    return token_data

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()
    if not user:
        raise credentials_exception

    return user

                                        
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_id_det = db.execute(text(f"SELECT * FROM users WHERE id = {user_id};")).fetchone()
    return user_id_det

def get_user_profile_by_id(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    profile_id_det = db.execute(text(f"SELECT * FROM profile  WHERE user_id = {user_id};")).fetchone()
    return profile_id_det

def get_location_by_id(user_id: int, db: Session = Depends(get_db)):
    location= db.query(models.General_hotspot).filter(models.General_hotspot.user_id==user_id).first()
    location_id_det = db.execute(text(f"SELECT * FROM general_hotspot  WHERE user_id = {user_id};")).fetchone()
    return location_id_det
