
from fastapi import APIRouter, Form,HTTPException,status,Depends,UploadFile,File
from app import schemas,models,oauth2
from sqlalchemy.orm import Session
from app.database import get_db
from sqlalchemy import text
from shapely.geometry import Point, LineString, Polygon



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
        current_user: int = Depends(oauth2.get_current_user),
        db: Session = Depends(get_db)
    ):
        # WHILE ENTERING THE LATS AND LONS DONT PUT COMMA BETWWEN LAT AND LON--- IT SHOULD BE LIKE (63747 32653)---NO COMMA IN BETWEEN!!! 
        # 1️⃣ Check if user exists and credentials are valid
        db_user = db.query(models.User).filter(models.User.id == user.user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        if db_user.id != current_user.id:
            raise HTTPException(status_code=403, detail="Invalid credentials")
        # 2️⃣ Parse user location into Point
        try:
            user_lon, user_lat = map(float, user.hotspot_location.split(","))  # "lon,lat"
            user_point = Point(user_lon, user_lat)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid user hotspot location format. Expected 'lon,lat'."
            )
        # 3️⃣ Retrieve all hotspots
        hotspots = db.query(models.Hotspot).all()
        for location in hotspots:
            try:
                raw_coords = location.location  # e.g., "{(12.9720 77.5945), (12.9730 77.5950), ...}"
                cleaned = raw_coords.replace("{", "").replace("}", "").replace("(", "").replace(")", "")
                # cleaned -> "12.9720 77.5945, 12.9730 77.5950, ..."
                polygon_coords = []
                for point_str in cleaned.split(","):
                    point_str = point_str.strip()  # "12.9720 77.5945"
                    lat_str, lon_str = point_str.split()  # Split by space
                    lat = float(lat_str)
                    lon = float(lon_str)
                    polygon_coords.append((lon, lat))  # Shapely expects (x=lon, y=lat)
                polygon = Polygon(polygon_coords)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid hotspot coordinates for {location.name}: {e}"
                )
        if polygon.contains(user_point):
                # CHECKING IF USER IS ALREADY INSIDE THE HOTSPOT
            check_stmt = text(f"""
                    SELECT * FROM "{location.name}_temporary_table" WHERE user_id = :user_id;""")
            result = db.execute(check_stmt, {"user_id": user.user_id}).fetchone()
            if result:
                    raise HTTPException(
                        status_code=400,
                        detail="User is already marked as inside this hotspot."
                    )
            insert_stmt = text(f"""INSERT INTO "{location.name}_temporary_table" (user_location,user_id)VALUES (:user_location, :user_id); """)
            db.execute(insert_stmt, {"user_location": user.hotspot_location,"user_id": user.user_id} )
            db.commit()
                # FETCHING OTHER USERS INSIDE THE SAME HOTSPOT
            other_users_id = db.scalars(text(f"SELECT user_id from {location.name}_temporary_table WHERE user_id != {current_user.id};")).all()
            ids = other_users_id
            print ("OTHER USERS IDS INSIDE HOTSPOT:", ids)
            users_data = []

            for user_id in other_users_id:
                other_users = oauth2.get_user_by_id(user_id, db)
                other_profiles = oauth2.get_user_profile_by_id(user_id, db)
                # to males show females only and vice versa
                if other_profiles.sexual_preference == oauth2.get_user_profile_by_id(current_user.id, db).sexual_preference:
                    continue
                users_data.append({
                    "user": {
                    "id": other_users.id,
                    "email": other_users.email,
                    "name": other_users.name,
                    "created_at": other_users.created_at
                },
                    "profile": {
                    "bio": other_profiles.bio,
                    "gender": other_profiles.gender,
                    "sexual_preference": other_profiles.sexual_preference,
                    "height": other_profiles.height,
                    "language": other_profiles.language,
                    "profile_picture": other_profiles.profile_picture,
                    "images": other_profiles.images
                }
                })              
            return {"other_users": users_data}

        else:
            return {
                    "user_id": user.user_id,
                    "hotspot_location": user.hotspot_location,
                    "inside": False
        }
