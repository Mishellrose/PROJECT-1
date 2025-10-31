from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app import schemas, oauth2
from app.database import get_db
from app.services import hotspot_service
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import date


from fastapi import FastAPI
from datetime import datetime
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler  # runs tasks in the background
from apscheduler.triggers.cron import CronTrigger  # allows us to specify a recurring time for execution


router = APIRouter(prefix="/match", tags=["Match"])


@router.post("/", status_code=status.HTTP_200_OK, response_model=schemas.SwipeOut)
def swipe_match(
    swipe: schemas.SwipeIn,
    current_user=Depends(oauth2.get_current_user),
    db: Session = Depends(get_db)
):
    # 1️⃣ Basic validation
    if swipe.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Invalid credentials")

    db_user = db.query(oauth2.models.User).filter_by(id=swipe.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    target_user = oauth2.get_user_by_id(swipe.swiped_on_id, db)
    if not target_user:
        raise HTTPException(status_code=404, detail="Swiped-on user not found")

    # 2️⃣ Check if swiped user is inside same hotspot (and valid by preference)
    result = hotspot_service.get_users_in_same_hotspot(swipe.user_id, swipe.user_location, db)
    if not result or swipe.swiped_on_id not in result["other_user_ids"]:
        raise HTTPException(status_code=400, detail="You can only swipe users inside your hotspot.")
        
    today = date.today()
    if db_user.last_swipe_reset != today:
        # reset if new day
        db_user.daily_swipe_count = 0
        db_user.last_swipe_reset = today
    if swipe.direction == "right" and not db_user.isPremium:
        if db_user.daily_swipe_count >= 5:
            raise HTTPException(
                status_code=400,
                detail="You have reached your daily swipe-right limit (5 per day)."
            )
        db_user.daily_swipe_count += 1

    db.commit()

    insert_stmt = text("""
        INSERT INTO "SwipeTable" (user_id, user_name, swiped_on_id, swiped_on_id_name, direction)
        VALUES (:uid, :uname, :sid, :sname, :dir);
    """)
    db.execute(insert_stmt, {
        "uid": swipe.user_id,
        "uname": db_user.name,
        "sid": swipe.swiped_on_id,
        "sname": target_user.name,
        "dir": swipe.direction
    })
    db.commit()

    # 4️⃣ Check if both swiped right (match)
    #a user can only swipe right 5 times a day

    if swipe.direction == "right":
        

        check_stmt = text("""
            SELECT * FROM "SwipeTable"
            WHERE user_id = :sid AND swiped_on_id = :uid AND direction = 'right';
        """)
        match = db.execute(check_stmt, {"sid": swipe.swiped_on_id, "uid": swipe.user_id}).fetchone()
        if match:
            db.execute(text("""
                INSERT INTO "MatchTable" (user_id, user_name, matched_user_id, matched_user_name)
                VALUES (:uid, :uname, :mid, :mname)
                ON CONFLICT DO NOTHING;
            """), {
                "uid": swipe.user_id,
                "uname": db_user.name,
                "mid": swipe.swiped_on_id,
                "mname": target_user.name
            })
            db.commit()
            print(f"New match: {db_user.name} ❤️ {target_user.name}")
    remaining = (
        5 - db_user.daily_swipe_count if not db_user.isPremium else "∞"
    )
            
    # 5️⃣ Response
    return {
        
        "user_id": swipe.user_id,
        "user_name": db_user.name,
        "user_location": swipe.user_location,
        "matched_user_id": swipe.swiped_on_id,
        "matched_user_name": target_user.name,
        "balance_swipe_rights":remaining
    }


@router.get("/MyMatches",status_code=status.HTTP_200_OK)
def get_all_my_matches(user_id: int,
                       current_user=Depends(oauth2.get_current_user),
                       db: Session=Depends(get_db)):
    db_user = db.query(oauth2.models.User).filter_by(id=user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")   
    if db_user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Invalid credentials")
    #show details ie how many swiped the user back right 

    #check user swiped right on others
    #return who is already matched in match table
    ids=[]
    stmt=text("""SELECT * FROM "MatchTable" WHERE user_id=:uid;""")
    matches=db.execute(stmt,{"uid":user_id}).fetchall()
    for match in matches:
        id=ids.append(match.matched_user_id)
        print("Matched IDs:",ids)
    back_ids=[]
    check_back_stmt=text("""SELECT * FROM "SwipeTable" WHERE swiped_on_id=:uid AND direction='right';""")
    swiped_right_back=db.execute(check_back_stmt,{"uid":user_id}).fetchall()
    for swipe in swiped_right_back:
        back_ids.append(swipe.user_id)
    final_ids=list(set(ids).intersection(set(back_ids)))
    print("Final Matched IDs:",final_ids)
    if not final_ids:
        return {"matched_user_id":None,"matched_user_name":None}
    #fetch all his matches one by one
    matches=[]
    for fid in final_ids:
        matched_user_dets=oauth2.get_user_by_id(fid,db)
        matched_profile_dets=oauth2.get_user_profile_by_id(fid,db)

        matches.append(schemas.MatchOut(
            matched_user=schemas.UserOut(
                id=matched_user_dets.id,
                email=matched_user_dets.email,
                name=matched_user_dets.name,
                created_at=matched_user_dets.created_at
            ),
            matched_profile=schemas.UserProfile(
                bio=matched_profile_dets.bio,
                gender=matched_profile_dets.gender,
                sexual_preference=matched_profile_dets.sexual_preference,
                height=matched_profile_dets.height,
                language=matched_profile_dets.language
            )
        ))
    return matches

            