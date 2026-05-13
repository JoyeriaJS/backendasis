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
    totp_secret = Column(String, nullable=True)


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lat = Column(Float)
    lng = Column(Float)
    fecha = Column(DateTime, default=datetime.utcnow)
    tipo = Column(String)  # 👈 NUEVO

class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    nombre = Column(String)  # 👈 AGREGAR ESTA LINEA

    tipo = Column(String)  # liquidacion | contrato
    archivo_url = Column(String)

    periodo = Column(String)  # 2026-05

    estado = Column(String, default="pendiente")  # pendiente | firmado | rechazado
    observacion = Column(String, nullable=True)
    correo: str
    fecha_firma = Column(DateTime, nullable=True)