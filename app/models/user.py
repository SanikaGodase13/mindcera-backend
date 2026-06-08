from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False)

    password_hash = Column(String, nullable=False)

    age = Column(Integer)

    gender = Column(String)

    occupation = Column(String)

    mental_health_goal = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())