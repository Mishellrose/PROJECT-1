
from fastapi import APIRouter,HTTPException,status,Depends,UploadFile,File
from app import schemas,models
from sqlalchemy.orm import Session
from app.database import get_db


router=APIRouter(prefix="/hotspot",tags=['Hotspot'])

#create hotspot,add image,description and values in a single endpoint
#the text data (name, bio) directly in the database
#the image file in a folder (and save its path in the database)
@router.post("/",status_code= status.HTTP_201_CREATED,response_model=schemas.HSOut)
async def create_hotspot( hotspot: schemas.CreateHS ,file: UploadFile , db: Session = Depends(get_db)):
    db_image = db.query(models.Hotspot)
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    db_image.image=file_location
    db.commit()
    db.refresh(db_image)


    new_hotspot = models.Hotspot(**hotspot.dict())
    db.add(new_hotspot)
    db.commit()
    db.refresh(new_hotspot)

    return {"id": new_hotspot.id, "name": new_hotspot.name, "description": new_hotspot.description, "file_location": file.filename}

#get all hotspots





