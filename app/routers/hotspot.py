
from fastapi import APIRouter, Form,HTTPException,status,Depends,UploadFile,File
from app import schemas,models,oauth2
from sqlalchemy.orm import Session
from app.database import get_db


router=APIRouter(prefix="/hotspot",tags=['Hotspot'])

#create hotspot,add image,description and values in a single endpoint
#the text data (name, bio) directly in the database
#the image file in a folder (and save its path in the database)
@router.post("/",status_code= status.HTTP_201_CREATED,response_model=schemas.HSCreate)
async def create_hotspot(
    name: str = Form(...),
    description: str = Form(...),
    image : UploadFile = File(...),
    location: str = Form(None),
    db: Session = Depends(get_db)
):
    
    file_location = f"uploads/{image.filename}"
    with open(file_location, "wb") as file_object:
        file_object.write(image.file.read())

    new_hotspot = models.Hotspot(
        name=name,
        description=description,
        image=file_location,
        location=location
    )
    db.add(new_hotspot)
    db.commit()
    db.refresh(new_hotspot)

    return {
        "id": new_hotspot.id,
        "name": new_hotspot.name,
        "description": new_hotspot.description,
        "image": file_location, 
        "location": new_hotspot.location
    }

#get all hotspots
@router.get("/",response_model=list[schemas.HSCreate])
def get_all_hotspots(db: Session = Depends(get_db)):
    hotspots = db.query(models.Hotspot).all()
    return hotspots
#id and location

@router.post("/inside",status_code=status.HTTP_201_CREATED)
def temptable_user(user: schemas.UserHS,current_user= Depends(oauth2.get_current_user),db:Session=Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.id == user.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.id != current_user.id:
     raise HTTPException(status_code=403, detail="Invalid credentials")
    if user.hotspot_location:
        db_hotspot = db.query(models.Hotspot).filter(models.Hotspot.location == user.hotspot_location).first()
        if not db_hotspot:
            raise HTTPException(status_code=404, detail="Hotspot not found")

    user_query=models.TempTable(**user.dict())
    db.add(user_query)
    db.commit()
    db.refresh(user_query)

    return{"user_id":user.user_id, "hotspot_location":user.hotspot_location}
    





