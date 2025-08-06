from sqlalchemy import Column, Integer, String
from app.db.database import Base


class User(Base):
    __tablename__ = "Meals"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
