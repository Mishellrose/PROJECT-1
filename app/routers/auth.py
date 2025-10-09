from fastapi import APIRouter,status,HTTPException,Depends
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import models,schemas,utils,oauth2
from app.database import get_db


router=APIRouter(tags=['Authentication'])

@router.post("/login",response_model=schemas.Token)
def Login_user(user_credentials:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user=db.query(models.User).filter(models.User.email==user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=403,detail=f'Invalid Credentials')
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=403,detail=f'Invalid Credentials')
    
    access_token = oauth2.create_access_token(data={"user_id":user.id})
    return {"access_token":access_token, "token_type":"bearer"}
