from fastapi import APIRouter,Depends,status
from app import models,schemas,utils
from app.database import get_db
from sqlalchemy.orm import Session

router=APIRouter(prefix="/user",tags=['Register'])

@router.post("/",response_model=schemas.UserOut)
def create_user(user:schemas.UserCreate,status_code=status.HTTP_201_CREATED,db:Session=Depends(get_db)):
    hashed_password=utils.hash(user.password)
    user.password=hashed_password

    new_user=models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user




    