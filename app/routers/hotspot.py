
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

    db.execute(text(f"CREATE TABLE {new_hotspot.name}_temporary_table (id SERIAL PRIMARY KEY, location VARCHAR UNIQUE NOT NULL);"))
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
            # Clean the coordinate string from DB
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

        # 4️⃣ Check if user is inside polygon
        if polygon.contains(user_point):
            # Insert user location into corresponding temporary table safely
            insert_stmt = text(f"""
                INSERT INTO {location.name}_temporary_table (location)
                VALUES (:hotspot_location)
                ON CONFLICT (location) DO NOTHING;
            """)
            db.execute(insert_stmt, {"hotspot_location": user.hotspot_location})
            db.commit()

            return {
                "user_id": user.user_id,
                "hotspot_location": user.hotspot_location,
                "hotspot_id": location.id,
                "hotspot_name": location.name,
                "inside": True
            }

    # 5️⃣ If user is not inside any hotspot
    return {
        "user_id": user.user_id,
        "hotspot_location": user.hotspot_location,
        "inside": False
    }
