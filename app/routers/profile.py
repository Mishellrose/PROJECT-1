import shutil
from fastapi import APIRouter,Depends,status,HTTPException,File,UploadFile
from app import schemas,models,oauth2
from app.database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.encoders import jsonable_encoder

router=APIRouter(prefix="/profile",tags=['EditProfile'])

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.ProfileOut)
def create_profile(prof: schemas.UserProfile,current_user: int=Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    
    new_prof=models.Profile(user_id=current_user.id, **prof.dict())
    db.add(new_prof)
    db.commit()
    db.refresh(new_prof)

    return schemas.ProfileOut(
        profile=schemas.UserProfile(
            bio=new_prof.bio,
            gender=new_prof.gender,
            sexual_preference=new_prof.sexual_preference,
            height=new_prof.height,
            language=new_prof.language
        ),
        user=schemas.UserOut(
            id=current_user.id,
            email=current_user.email, 
            name=current_user.name,
            created_at=current_user.created_at
        ))

@router.put("/edit/{id}",response_model=schemas.ProfileOut)
def update(id: int, upd_prof: schemas.UserProfile, current_user:int=Depends(oauth2.get_current_user), db: Session=Depends(get_db)):

    prof_query=db.query(models.Profile).filter(models.Profile.id==id)
    prof=prof_query.first()
    if not prof:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'post with id {id} not found')
    
    if prof.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="not authorized to perform action")
    
    prof_query.update(upd_prof.dict(),synchronize_session=False)
    db.commit()


    return schemas.ProfileOut(
        profile=schemas.UserProfile(
            bio=upd_prof.bio,
            gender=upd_prof.gender,
            sexual_preference=upd_prof.sexual_preference,
            height=upd_prof.height,
            language=upd_prof.language
        ),
        user=schemas.UserOut(
            id=current_user.id,
            email=current_user.email, 
            name=current_user.name,
            created_at=current_user.created_at
        ))

    
#delete endpoint

#patch endpoint

@router.patch("/update/{profile_id}")
def partial_update(
    profile_id: int,
    profile: schemas.PartialProf,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    # Get profile from DB
    db_profile = db.query(models.Profile).filter(models.Profile.id == profile_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if db_profile.user_id != current_user.id:
     raise HTTPException(status_code=403, detail="Not allowed to update this profile")

    # Convert only provided fields into a dict
    update_data = profile.dict(exclude_unset=True)

    # Apply updates
    for key, value in update_data.items():
        setattr(db_profile, key, value)

    # Save changes to DB
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)

    return db_profile



#upload profile picture

@router.post("/upload/{profile_id}")
async def upload_picture(file:UploadFile, profile_id: int, current_user= Depends(oauth2.get_current_user),db:Session= Depends(get_db)):

    # Check if the profile belongs to the current user
    db_profile = db.query(models.Profile).filter(models.Profile.id == profile_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if db_profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to update this profile")
    
    # Save the uploaded file to a directory (e.g., "uploads/")
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update the profile picture path in the database
    db_profile.profile_picture = file_location
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)  

    return {"filename": file.filename, "user_id": current_user.id}



#upload multiple images
@router.post("/upload-multiple/{profile_id}")
async def upload_multiple_pictures(files: List[UploadFile], profile_id: int, current_user= Depends(oauth2.get_current_user),db:Session= Depends(get_db)):

    # Check if the profile belongs to the current user
    db_profile = db.query(models.Profile).filter(models.Profile.id == profile_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if db_profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to update this profile")
    
    file_locations = []
    for file in files:
        file_location = f"uploads/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_locations.append(file_location)

    # Store the list of image paths as a comma-separated string
    db_profile.images = ",".join(file_locations)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)  

    return {"filenames": [file.filename for file in files], "user_id": current_user.id}




