from fastapi import FastAPI
from app import models
from .routers import user,auth,profile,hotspot,match
from app.database import engine



models.Base.metadata.create_all(bind=engine)

app=FastAPI()

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(hotspot.router)
app.include_router(match.router)