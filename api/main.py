from fastapi import FastAPI, HTTPException, Depends
from models import Empleado, RegistroHorario
import uuid
from typing import Optional
from datetime import datetime

app = FastAPI()

@app.post("/empleados/")
def crear_empleado(dni: str, nombre: str, apellido: str):
    try:
        empleado = Empleado.crear(dni, nombre, apellido)
        return {
            "id": empleado.id,
            "dni": empleado.dni,
            "nombre": empleado.nombre,
            "apellido": empleado.apellido
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/empleados/{dni}")
def obtener_empleado(dni: str):
    empleado = Empleado.obtener_por_dni(dni)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado.__dict__

@app.post("/registros/")
def registrar_horario(empleado_id: str, tipo: str):
    try:
        registro = RegistroHorario.registrar(empleado_id, tipo)
        return registro.__dict__
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/registros/{empleado_id}")
def obtener_registros(
    empleado_id: str,
    año: Optional[int] = None,
    mes: Optional[int] = None
):
    if año and mes:
        registros = RegistroHorario.obtener_registros_mensuales(empleado_id, año, mes)
    else:
        registros = RegistroHorario.obtener_todos(empleado_id)
    return [r.__dict__ for r in registros]

@app.get("/horas/{empleado_id}")
def calcular_horas(empleado_id: str, año: int, mes: int):
    horas = RegistroHorario.calcular_horas_mensuales(empleado_id, año, mes)
    return {"horas_trabajadas": horas}