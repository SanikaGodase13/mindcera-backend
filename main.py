from fastapi import FastAPI

from app.database.db import engine
from app.database.base import Base

import app.models.user
import app.models.password_reset_otp

from app.api.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MindCera API",
    version="1.0.0"
)

app.include_router(auth_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to MindCera API"
    }