from shapely.geometry import Point, Polygon
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app import models, oauth2


def get_users_in_same_hotspot(user_id: int, user_location: str, db: Session):
    """
    Determine which hotspot (if any) the user is inside,
    and return the list of other user IDs in that hotspot
    filtered by sexual preference.
    """
    # Parse "lon,lat" string into floats
    try:
        lon, lat = map(float, user_location.split(","))
        user_point = Point(lon, lat)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid location format. Expected 'lon,lat'.")

    hotspots = db.query(models.Hotspot).all()
    for hs in hotspots:
        # Parse polygon coordinates from "{(lat lon), (lat lon), ...}"
        cleaned = hs.location.replace("{", "").replace("}", "").replace("(", "").replace(")", "")
        coords = []
        for pt in cleaned.split(","):
            parts = pt.strip().split()
            if len(parts) != 2:
                continue
            lat_str, lon_str = parts
            coords.append((float(lon_str), float(lat_str)))  # Shapely expects (lon, lat)
        polygon = Polygon(coords)

        if polygon.contains(user_point):
            # user is inside this hotspot
            current_profile = oauth2.get_user_profile_by_id(user_id, db)
            table_name = f"{hs.name}_temporary_table"

            # Get all other users in same hotspot
            other_ids = db.scalars(
                text(f'SELECT user_id FROM "{table_name}" WHERE user_id != :uid'),
                {"uid": user_id}
            ).all()

            # Filter users by sexual preference
            filtered_ids = []
            for oid in other_ids:
                other_profile = oauth2.get_user_profile_by_id(oid, db)
                # Only show users with different sexual preferences
                if other_profile.sexual_preference == current_profile.sexual_preference:
                    continue
                filtered_ids.append(oid)

            return {
                "hotspot": hs,
                "other_user_ids": filtered_ids
            }

    # not inside any hotspot
    return None
