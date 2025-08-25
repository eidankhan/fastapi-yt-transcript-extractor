from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    api_key = Column(String(64), unique=True, nullable=False)
    tier = Column(String(50), nullable=False, default="free")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
