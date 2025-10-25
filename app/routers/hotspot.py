
from fastapi import APIRouter, Form,HTTPException,status,Depends,UploadFile,File
from app import schemas,models
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
    db: Session = Depends(get_db)
):
    
    file_location = f"uploads/{image.filename}"
    with open(file_location, "wb") as file_object:
        file_object.write(image.file.read())

    new_hotspot = models.Hotspot(
        name=name,
        description=description,
        image=file_location
    )
    db.add(new_hotspot)
    db.commit()
    db.refresh(new_hotspot)

    return {
        "id": new_hotspot.id,
        "name": new_hotspot.name,
        "description": new_hotspot.description,
        "image": file_location
    }

#get all hotspots
@router.get("/",response_model=list[schemas.HSCreate])
def get_all_hotspots(db: Session = Depends(get_db)):
    hotspots = db.query(models.Hotspot).all()
    return hotspots







