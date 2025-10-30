
from fastapi import APIRouter, Form,HTTPException,status,Depends,UploadFile,File
from app import schemas,models,oauth2
from sqlalchemy.orm import Session
from app.database import get_db
from sqlalchemy import text
from shapely.geometry import Point, LineString, Polygon
from app.services import hotspot_service


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
    #create new temporary table for each created hotspot

    db.execute(text(f"CREATE TABLE {new_hotspot.name}_temporary_table (id SERIAL PRIMARY KEY, user_location VARCHAR , user_id INTEGER UNIQUE);"))
    db.commit()
    

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

#@router.post("/inside",status_code=status.HTTP_201_CREATED)
#DEF TEMPTABLE_USER(USER: SCHEMAS.USERHS,CURRENT_USER= DEPENDS(OAUTH2.GET_CURRENT_USER),DB:SESSION=DEPENDS(GET_DB)):

   # DB_USER = DB.QUERY(MODELS.USER).FILTER(MODELS.USER.ID == USER.USER_ID).FIRST() IF NOT DB_USER: RAISE HTTPEXCEPTION(STATUS_CODE=404, DETAIL="USER NOT FOUND")IF DB_USER.ID != CURRENT_USER.ID: RAISE HTTPEXCEPTION(STATUS_CODE=403, DETAIL="INVALID CREDENTIALS")
    #IF USER.HOTSPOT_LOCATION:
        #DB_HOTSPOT = DB.QUERY(MODELS.HOTSPOT).FILTER(MODELS.HOTSPOT.LOCATION == USER.HOTSPOT_LOCATION).FIRST()
        #IF NOT DB_HOTSPOT:
         #   RAISE HTTPEXCEPTION(STATUS_CODE=404, DETAIL="HOTSPOT NOT FOUND")

    #USER_QUERY=MODELS.TEMPTABLE(**USER.DICT())
    #DB.ADD(USER_QUERY)
    #DB.COMMIT()
    #DB.REFRESH(USER_QUERY)

    #RETURN{"USER_ID":USER.USER_ID, "HOTSPOT_LOCATION":USER.HOTSPOT_LOCATION, "HOTSPOT_ID":DB_HOTSPOT.ID, "HOTSPOT_NAME":DB_HOTSPOT.NAME}
 
  #find user is inside or outside hotspot,we get id and location of user

@router.post("/inside", status_code=status.HTTP_200_OK)
def inside_hotspot(
    user: schemas.UserHS,
    current_user=Depends(oauth2.get_current_user),
    db: Session = Depends(get_db)
):
    # 1️⃣ Validate user
    db_user = db.query(models.User).filter(models.User.id == user.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Invalid credentials")

    # 2️⃣ Check which hotspot they’re in
    result = hotspot_service.get_users_in_same_hotspot(user.user_id, user.hotspot_location, db)
    if not result:
        return {"inside": False, "message": "User is not inside any hotspot."}

    hotspot = result["hotspot"]
    other_ids = result["other_user_ids"]

    # 3️⃣ Add user to General_hotspot and hotspot's temporary table (if not already there)
    user_dets = oauth2.get_user_by_id(user.user_id, db)
    db.execute(
        text('INSERT INTO "General_hotspot" (user_id, user_name, hotspot_location) '
             'VALUES (:uid, :uname, :loc) ON CONFLICT DO NOTHING;'),
        {"uid": user.user_id, "uname": user_dets.name, "loc": user.hotspot_location}
    )

    # Check if already inside hotspot
    check_stmt = text(f'SELECT * FROM "{hotspot.name}_temporary_table" WHERE user_id = :uid')
    result_check = db.execute(check_stmt, {"uid": user.user_id}).fetchone()
    if not result_check:
        insert_stmt = text(f'INSERT INTO "{hotspot.name}_temporary_table" (user_location, user_id) '
                           'VALUES (:loc, :uid);')
        db.execute(insert_stmt, {"loc": user.hotspot_location, "uid": user.user_id})
    db.commit()

    # 4️⃣ Fetch other users' data
    users_data = []
    for oid in other_ids:
        other_user = oauth2.get_user_by_id(oid, db)
        other_profile = oauth2.get_user_profile_by_id(oid, db)
        users_data.append({
            "user": {
                "id": other_user.id,
                "email": other_user.email,
                "name": other_user.name,
                "created_at": other_user.created_at
            },
            "profile": {
                "bio": other_profile.bio,
                "gender": other_profile.gender,
                "sexual_preference": other_profile.sexual_preference,
                "height": other_profile.height,
                "language": other_profile.language,
                "profile_picture": other_profile.profile_picture,
                "images": other_profile.images
            }
        })

    return {
        "inside": True,
        "hotspot_name": hotspot.name,
        "other_users": users_data
    }
