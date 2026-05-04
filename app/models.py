from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from datetime import datetime
#from database import Base
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String, default="user")  # "admin" o "user"


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lat = Column(Float)
    lng = Column(Float)
    fecha = Column(DateTime, default=datetime.utcnow)
    tipo = Column(String)  # 👈 NUEVO