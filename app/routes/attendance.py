from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from math import radians, cos, sin, asin, sqrt

from app.database import SessionLocal
from app.models import Attendance

router = APIRouter()

LAT_PERMITIDA = -33.43943
LNG_PERMITIDA = -70.648964
RANGO_METROS = 100


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def distancia_metros(lat1, lon1, lat2, lon2):
    r = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return r * c


@router.post("/marcar")
def marcar(data: dict, db: Session = Depends(get_db)):
    lat = data["lat"]
    lng = data["lng"]
    user_id = data["user_id"]

    distancia = distancia_metros(lat, lng, LAT_PERMITIDA, LNG_PERMITIDA)

    if distancia > RANGO_METROS:
        return {"ok": False, "mensaje": "Fuera de rango"}

    nuevo = Attendance(
        user_id=user_id,
        lat=lat,
        lng=lng
    )

    db.add(nuevo)
    db.commit()

    return {"ok": True, "mensaje": "Marcaje correcto"}