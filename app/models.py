from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from datetime import datetime
#from database import Base
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String, default="vendedora")  # "admin" o "user"
    totp_secret = Column(String, nullable=True)


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    username = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    fecha = Column(DateTime, default=datetime.utcnow)
    tipo = Column(String)  # 👈 NUEVO

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=True)

    username = Column(String)

    accion = Column(String)

    detalle = Column(String)

    fecha = Column(DateTime)

    ip = Column(String, nullable=True)

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
    fecha_firma = Column(DateTime, nullable=True)
    correo = Column(String, nullable=True)