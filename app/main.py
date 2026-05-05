from fastapi import FastAPI, Depends, HTTPException
from datetime import datetime, date
from sqlalchemy.orm import Session
from math import radians, cos, sin, asin, sqrt
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal, engine, Base
from app.models import Attendance, User

from fastapi.responses import FileResponse
from openpyxl import Workbook

from collections import defaultdict
import os

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ crear tablas
Base.metadata.create_all(bind=engine)

# 📍 ubicación empresa
LAT_EMPRESA = -33.4394545
LNG_EMPRESA = -70.6493824
DISTANCIA_MAX_METROS = 80


# ✅ conexión BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ fórmula distancia (Haversine)
def calcular_distancia_metros(lat1, lon1, lat2, lon2):
    r = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    return r * c


# 🔐 LOGIN
@app.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data["username"]).first()

    if not user or user.password != data["password"]:
        return {"error": "Credenciales inválidas"}

    return {
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }


# 📍 MARCAR ASISTENCIA (FIX GPS REAL)
@app.post("/marcar")
def marcar(data: dict, db: Session = Depends(get_db)):

    if "user_id" not in data:
        return {"error": "Falta user_id"}

    if "lat" not in data or "lng" not in data:
        return {"error": "Faltan coordenadas"}

    user_id = data["user_id"]
    lat = data["lat"]
    lng = data["lng"]

    # 👇 opcional (viene del frontend)
    accuracy = data.get("accuracy", 50)

    # 📍 calcular distancia
    distancia = calcular_distancia_metros(lat, lng, LAT_EMPRESA, LNG_EMPRESA)

    # 🧠 margen dinámico (LA SOLUCIÓN REAL)
    margen = max(DISTANCIA_MAX_METROS, accuracy)

    if distancia > margen:
        return {
            "error": "Fuera de la zona permitida",
            "distancia_metros": round(distancia, 2),
            "accuracy": accuracy
        }

    # 📅 registros de hoy
    hoy = date.today()

    registros_hoy = (
        db.query(Attendance)
        .filter(
            Attendance.user_id == user_id,
            Attendance.fecha >= datetime.combine(hoy, datetime.min.time())
        )
        .order_by(Attendance.fecha.asc())
        .all()
    )

    cantidad = len(registros_hoy)

    if cantidad >= 4:
        return {"error": "Ya completaste tus 4 marcajes del día"}

    tipos = [
        "entrada",
        "salida_colacion",
        "entrada_colacion",
        "salida"
    ]

    tipo = tipos[cantidad]

    nuevo = Attendance(
        user_id=user_id,
        lat=lat,
        lng=lng,
        fecha=datetime.now(),
        tipo=tipo
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return {
        "message": f"{tipo.replace('_', ' ').capitalize()} registrada",
        "tipo": tipo,
        "distancia_metros": round(distancia, 2),
        "accuracy": accuracy
    }


# 📊 ESTADO
@app.get("/estado/{user_id}")
def estado(user_id: int, db: Session = Depends(get_db)):

    hoy = date.today()

    registros = (
        db.query(Attendance)
        .filter(
            Attendance.user_id == user_id,
            Attendance.fecha >= datetime.combine(hoy, datetime.min.time())
        )
        .order_by(Attendance.fecha.asc())
        .all()
    )

    tipos = ["Entrada", "Salida a colación", "Entrada de colación", "Salida"]

    if len(registros) >= 4:
        return {"estado": "completo", "siguiente": None}

    return {
        "estado": "pendiente",
        "siguiente": tipos[len(registros)]
    }


# 📜 HISTORIAL
@app.get("/historial/{user_id}")
def historial(user_id: int, db: Session = Depends(get_db)):
    return db.query(Attendance)\
        .filter(Attendance.user_id == user_id)\
        .order_by(Attendance.fecha.desc())\
        .all()


# 📊 RESUMEN
@app.get("/resumen")
def resumen(db: Session = Depends(get_db)):

    registros = db.query(Attendance).order_by(Attendance.fecha).all()
    users = db.query(User).all()

    resumen = defaultdict(lambda: {
        "user": "",
        "horas": 0,
        "atrasos": 0,
        "retiros": 0
    })

    agrupado = defaultdict(lambda: defaultdict(list))

    for r in registros:
        fecha = r.fecha.date()
        agrupado[r.user_id][fecha].append(r)

    for user_id, dias in agrupado.items():

        user = next((u for u in users if u.id == user_id), None)
        if not user:
            continue

        resumen[user_id]["user"] = user.username

        for fecha, registros_dia in dias.items():

            registros_dia.sort(key=lambda x: x.fecha)

            entrada = None
            salida = None
            salida_colacion = None
            entrada_colacion = None

            for r in registros_dia:

                hora = r.fecha.hour

                if r.tipo == "entrada" and not entrada:
                    entrada = r.fecha
                    if hora >= 10:
                        resumen[user_id]["atrasos"] += 1

                elif r.tipo == "salida":
                    salida = r.fecha
                    if hora < 18:
                        resumen[user_id]["retiros"] += 1

                elif r.tipo == "salida_colacion" and not salida_colacion:
                    salida_colacion = r.fecha

                elif r.tipo == "entrada_colacion":
                    entrada_colacion = r.fecha

            if entrada and salida and salida > entrada:

                total = (salida - entrada).total_seconds()

                if salida_colacion and entrada_colacion and entrada_colacion > salida_colacion:
                    colacion = (entrada_colacion - salida_colacion).total_seconds()
                    total -= colacion

                if total < 0:
                    total = 0

                resumen[user_id]["horas"] += total

    resultado = []

    for r in resumen.values():
        horas = int(r["horas"] // 3600)
        minutos = int((r["horas"] % 3600) // 60)

        resultado.append({
            "user": r["user"],
            "horas": f"{horas}h {minutos}min",
            "atrasos": r["atrasos"],
            "retiros": r["retiros"]
        })

    return resultado


# 📥 EXPORTAR EXCEL
@app.get("/exportar-excel")
def exportar_excel(db: Session = Depends(get_db)):

    data = resumen(db)

    wb = Workbook()
    ws = wb.active
    ws.title = "Resumen"

    ws.append(["Usuario", "Horas", "Atrasos", "Retiros"])

    for r in data:
        ws.append([
            r["user"],
            r["horas"],
            r["atrasos"],
            r["retiros"]
        ])

    file_path = "reporte_asistencia.xlsx"
    wb.save(file_path)

    return FileResponse(
        path=file_path,
        filename="reporte_asistencia.xlsx",
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


# 🔐 ADMIN
def require_admin(user):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")