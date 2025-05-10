from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models.database import SessionLocal
from schemas.empleado import EmpleadoCreate, EmpleadoResponse
from utils import crud, crear_empleado, obtener_empleado_por_dni
from uuid import UUID

app = FastAPI(title="API de Empleados")

# Dependencia para la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----- Endpoints -----
@app.post("/empleados/", response_model=EmpleadoResponse)
def crear_empleado_api(empleado: EmpleadoCreate, db: Session = Depends(get_db)):
    db_empleado = obtener_empleado_por_dni(db, dni=empleado.dni)
    if db_empleado:
        raise HTTPException(status_code=400, detail="DNI ya registrado")
    return crear_empleado(db=db, empleado=empleado)

@app.get("/empleados/{dni}", response_model=EmpleadoResponse)
def leer_empleado(dni: str, db: Session = Depends(get_db)):
    empleado = obtener_empleado_por_dni(db, dni=dni)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado

@app.get("/empleados/{empleado_id}/registros")
def obtener_registros_empleado(
    empleado_id: UUID,
    año: int,
    mes: int,
    db: Session = Depends(get_db)
):
    # Lógica para filtrar registros por mes/año
    registros = db.query(RegistroHorario).filter(
        RegistroHorario.empleado_id == empleado_id,
        extract('year', RegistroHorario.fecha_hora) == año,
        extract('month', RegistroHorario.fecha_hora) == mes
    ).all()
    return registros