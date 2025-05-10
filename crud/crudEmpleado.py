import uuid
from datetime import datetime, timedelta
from database import db


class Empleado:
    def __init__(self, dni, nombre, apellido, id=None):
        self.id = id or str(uuid.uuid4())
        self.dni = dni
        self.nombre = nombre
        self.apellido = apellido

    @staticmethod
    def crear(dni, nombre, apellido):
        """Crea un nuevo empleado"""
        try:
            with db.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO empleados (id, dni, nombre, apellido)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (str(uuid.uuid4()), dni, nombre, apellido)
                )
                empleado_id = cur.fetchone()[0]
                db.conn.commit()
                return Empleado.obtener_por_id(empleado_id)
        except Exception as e:
            db.conn.rollback()
            raise ValueError(f"Error al crear empleado: {e}")

    @staticmethod
    def obtener_por_id(id):
        """Obtiene un empleado por su ID"""
        with db.conn.cursor() as cur:
            cur.execute("SELECT employee_id, document_number, first_name, last_name FROM employees...")
            result = cur.fetchone()
            if result:
                return Empleado(id=result[0], dni=result[1], nombre=result[2], apellido=result[3])
            return None

    @staticmethod
    def obtener_por_dni(dni):
        """Obtiene un empleado por su DNI"""
        with db.conn.cursor() as cur:
            cur.execute(
                "SELECT id, dni, nombre, apellido FROM empleados WHERE dni = %s",
                (dni,))
            result = cur.fetchone()
            if result:
                return Empleado(id=result[0], dni=result[1], nombre=result[2], apellido=result[3])
            return None


class RegistroHorario:
    def __init__(self, id, empleado_id, tipo, fecha_hora):
        self.id = id
        self.empleado_id = empleado_id
        self.tipo = tipo
        self.fecha_hora = fecha_hora

    @staticmethod
    def registrar(empleado_id, tipo):
        """Registra un nuevo horario"""
        try:
            with db.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO registros_horario (id, empleado_id, tipo)
                    VALUES (%s, %s, %s)
                    RETURNING id, empleado_id, tipo, fecha_hora
                    """,
                    (str(uuid.uuid4()), str(empleado_id), tipo)
                )
                result = cur.fetchone()
                db.conn.commit()
                return RegistroHorario(*result)
        except Exception as e:
            db.conn.rollback()
            raise ValueError(f"Error al registrar horario: {e}")

    @staticmethod
    def obtener_registros_mensuales(empleado_id, año, mes):
        """Obtiene registros de horario por mes"""
        inicio = datetime(año, mes, 1)
        fin = (inicio + timedelta(days=31)).replace(day=1)

        with db.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, empleado_id, tipo, fecha_hora 
                FROM registros_horario
                WHERE empleado_id = %s 
                AND fecha_hora >= %s 
                AND fecha_hora < %s
                ORDER BY fecha_hora
                """,
                (str(empleado_id), inicio, fin)
            )
            return [RegistroHorario(*row) for row in cur.fetchall()]

    @staticmethod
    def calcular_horas_mensuales(empleado_id, año, mes):
        """Calcula horas trabajadas en un mes"""
        registros = RegistroHorario.obtener_registros_mensuales(empleado_id, año, mes)
        horas = 0.0
        entrada = None

        for reg in registros:
            if reg.tipo == 'entrada':
                entrada = reg.fecha_hora
            elif entrada and reg.tipo == 'salida':
                horas += (reg.fecha_hora - entrada).total_seconds() / 3600
                entrada = None

        return round(horas, 2)