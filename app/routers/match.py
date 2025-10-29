from fastapi import APIRouter, Form,Depends,HTTPException,status
from app import oauth2,models,schemas
from app.database import get_db
from sqlalchemy import text

from sqlalchemy.orm import Session

router=APIRouter(prefix="/Swipe",tags=['SwipeMatch'])

@router.post("/",status_code=status.HTTP_200_OK,response_model=schemas.SwipeOut)
def swipe_match(swipe:schemas.SwipeIn,
                current_user: int=Depends(oauth2.get_current_user),db:Session=Depends(get_db)):
    
    db_user=db.query(models.User).filter(models.User.id==swipe.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404,detail="User not found")
    db_swiped_on_id= db.query(models.User.id==swipe.swiped_on_id).first()
    if not db_swiped_on_id:
        raise HTTPException(status_code=403,detail="The id which user swiped on doesnt exist")
    if swipe.user_id != current_user.id:
        raise HTTPException(status_code=403,detail="Invalid credentials")
    user_details = oauth2.get_user_by_id(swipe.user_id, db)
    swiped_on_details = oauth2.get_user_by_id(swipe.swiped_on_id, db)
    #add contents to swipetable
    insert_stmt=text(f"""INSERT INTO "SwipeTable" (user_id, user_name,swiped_on_id,swiped_on_id_name,direction)VALUES (:user_id, :user_name, :swiped_on_id, :swiped_on_id_name, :direction);""")                                                
    db.execute(insert_stmt, {"user_id": swipe.user_id,"user_name":user_details.name,"swiped_on_id": swipe.swiped_on_id,"swiped_on_id_name":swiped_on_details.name,"direction":swipe.direction })
    db.commit()

    return{
        "user_id": swipe.user_id,
        "user_name": user_details.name,
        "swiped_on_id": swipe.swiped_on_id,
        "swiped_on_id_name":swiped_on_details.name,
        "direction":swipe.direction
    }
    

    