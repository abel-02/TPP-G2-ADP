from models import empleado, empleado, registroHorario
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from uuid import UUID #mejora de clave primaria
from sqlalchemy.orm import sessionmaker, Session

from models.empleado import Empleado, RegistroHorario


def crear_empleado(dni: str, nombre: str, apellido: str):
    session = Session() #es el intermediario entre el código Python y la base de datos
    try:
        empleado = Empleado(dni=dni, nombre=nombre, apellido=apellido)
        session.add(empleado)
        session.commit()
        return empleado
    except IntegrityError:
        session.rollback()
        raise ValueError("El DNI ya existe")
    finally:
        session.close()


def registrar_horario(empleado_id: UUID, tipo: str):
    session = Session()
    try:
        registro = RegistroHorario(empleado_id=empleado_id, tipo=tipo)
        session.add(registro)
        session.commit()
        return registro
    finally:
        session.close()


def obtener_registros_mensuales(empleado_id: UUID, año: int, mes: int):
    session = Session()
    try:
        inicio = datetime(año, mes, 1)
        fin = (inicio + timedelta(days=31)).replace(day=1)  # Primer día del siguiente mes

        return session.query(RegistroHorario).filter(
            RegistroHorario.empleado_id == empleado_id,
            RegistroHorario.fecha_hora >= inicio,
            RegistroHorario.fecha_hora < fin
        ).order_by(RegistroHorario.fecha_hora).all()
    finally:
        session.close()