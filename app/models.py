from sqlalchemy import Column,Integer,String,TIMESTAMP,ForeignKey,Boolean,Date
from app.database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import date


class User(Base):
    __tablename__="users"


    id=Column(Integer,primary_key=True,nullable=False)
    name=Column(String,nullable=False)
    email=Column(String,unique=True,nullable=False)
    password=Column(String,nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    isPremium=Column(Boolean,default=False)
    isActive=Column(Boolean,default=True)
    daily_swipe_count = Column(Integer, default=0)
    last_swipe_reset = Column(Date, nullable=True)

class Profile(Base):
    __tablename__="profile"


    id=Column(Integer,primary_key=True,nullable=False)
    user_id=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    profile_picture=Column(String,nullable=True)
    bio=Column(String(100),nullable=True)
    gender=Column(String,nullable=True)
    sexual_preference=Column(String,nullable=True)
    height=Column(Integer,nullable=True)
    language=Column(String,nullable=True)
    images=Column(String,nullable=True)
    #updated_at=Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'),onupdate=text('now()'))

    owner= relationship("User")
    
    
#create hotspot table , name,description,image

class Hotspot(Base):
    __tablename__="hotspot"

    id=Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    name=Column(String,nullable=False)
    description=Column(String,nullable=False)
    image=Column(String,nullable=True)
    location=Column(String,unique=True,nullable=False)


#class TempTable(Base):
   # __tablename__="temptable"

    #user_id= Column(Integer,ForeignKey("users.id",ondelete='CASCADE'),primary_key=True)
    #hotspot_location=Column(String,ForeignKey("hotspot.location",ondelete='CASCADE'), primary_key=True)

class General_hotspot(Base):
    __tablename__="general_hotspot"

    id=Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    user_id= Column(Integer,ForeignKey("users.id",ondelete='CASCADE'),nullable=False)
    user_name=Column(String,nullable=False)
    hotspot_location=Column(String,nullable=False)

class SwipeTable(Base):
    __tablename__="SwipeTable"

    id=Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    user_id= Column(Integer,ForeignKey("users.id",ondelete='CASCADE'),nullable=False)
    user_name=Column(String,nullable=False)
    swiped_on_id= Column(Integer,ForeignKey("users.id",ondelete='CASCADE'),nullable=False)
    swiped_on_id_name=Column(String,nullable=False)
    direction=Column(String,nullable=False)  # 'left' or 'right'

class MatchTable(Base):
    __tablename__="MatchTable"

    id=Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    user_id= Column(Integer,ForeignKey("users.id",ondelete='CASCADE'),nullable=False)
    user_name=Column(String,nullable=False)
    matched_user_id= Column(Integer,ForeignKey("users.id",ondelete='CASCADE'),nullable=False)
    matched_user_name=Column(String,nullable=False)