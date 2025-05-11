from uuid import UUID
from datetime import datetime, timedelta


#Acá se maneja la lógica que interactúa con la base de datos, es decir se manejan las consultas

#A chequear las consultas porque me las tiró gpt


def crear_empleado(db, dni: str, nombre: str, apellido: str):
    try:
        with db.cursor() as cur:
            cur.execute("""
                INSERT INTO empleados (dni, nombre, apellido)
                VALUES (%s, %s, %s) RETURNING id
            """, (dni, nombre, apellido))
            empleado_id = cur.fetchone()[0]
            db.commit()
            return {"id": empleado_id, "dni": dni, "nombre": nombre, "apellido": apellido}
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error en la BD: {e}")

def obtener_empleado_por_dni(db, dni: str):
    with db.cursor() as cur:
        cur.execute("SELECT id, dni, nombre, apellido FROM empleados WHERE dni = %s", (dni,))
        resultado = cur.fetchone()
        if resultado:
            return {"id": resultado[0], "dni": resultado[1], "nombre": resultado[2], "apellido": resultado[3]}
        return None

def registrar_horario(db, empleado_id: UUID, tipo: str):
    with db.cursor() as cur:
        cur.execute("""
            INSERT INTO registros_horario (empleado_id, tipo, fecha_hora)
            VALUES (%s, %s, %s)
        """, (empleado_id, tipo, datetime.utcnow()))
        db.commit()

def obtener_registros_mensuales(db, empleado_id: UUID, año: int, mes: int):
    inicio = datetime(año, mes, 1)
    fin = (inicio + timedelta(days=31)).replace(day=1)

    with db.cursor() as cur:
        cur.execute("""
            SELECT id, empleado_id, tipo, fecha_hora
            FROM registros_horario
            WHERE empleado_id = %s AND fecha_hora BETWEEN %s AND %s
            ORDER BY fecha_hora
        """, (empleado_id, inicio, fin))
        return cur.fetchall()

# A detallar
def obtenerTodosLosEmpleados(db):
    with db.cursor() as cur:
        cur.execute("""
                    SELECT * from empleado
                """)
        return cur.fetchall()