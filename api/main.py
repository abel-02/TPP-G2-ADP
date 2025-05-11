from fastapi import FastAPI, Depends, HTTPException
from db.database import get_db
from repository import empleadoRepository
from repository.empleadoRepository import *
from schema import empleadoSchema


app = FastAPI(title="API de Empleados")

#Abrir db
db = get_db()
#Cerrar db
db.close()

@app.post("/empleados/")
def crear_empleado_api(empleado: empleadoSchema):
    db = get_db()
    if obtener_empleado_por_dni(db, empleado.dni):
        raise HTTPException(status_code=400, detail="DNI ya registrado")
    db.close()
    return crear_empleado(db, empleado)


@app.get("/empleados/{dni}")
def leer_empleado(dni: str):
    db = get_db()
    empleado = obtener_empleado_por_dni(db, dni)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    db.close()
    return empleado

@app.get("/empleados")
def traerTodosLosEmpleados():
    db = get_db()
    data = obtenerTodosLosEmpleados(db)
    db.close()
    return data