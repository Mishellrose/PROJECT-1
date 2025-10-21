from sqlalchemy import Column,Integer,String,TIMESTAMP,ForeignKey,Boolean
from app.database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__="users"


    id=Column(Integer,primary_key=True,nullable=False)
    name=Column(String,nullable=False)
    email=Column(String,unique=True,nullable=False)
    password=Column(String,nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    isPremium=Column(Boolean,default=False)
    isActive=Column(Boolean,default=True)

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
    
    

