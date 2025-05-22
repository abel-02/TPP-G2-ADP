from datetime import date, time
import psycopg2
from .database import db
from typing import Tuple, List
from crud.crudEmpleado import Empleado
from typing import Optional


class AdminCRUD:
    @staticmethod
    def crear_empleado(nuevoEmpleado):
        conn, cur = db.get_conn_cursor()
        try:
            cur.execute(
                """
                INSERT INTO empleado (
                    nombre, apellido, tipo_identificacion, numero_identificacion,
                    fecha_nacimiento, correo_electronico, telefono, calle,
                    numero_calle, localidad, partido, provincia, genero, pais_nacimiento, estado_civil
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_empleado, numero_identificacion, nombre, apellido
                """,
                (
                    nuevoEmpleado.nombre, nuevoEmpleado.apellido, nuevoEmpleado.tipo_identificacion,
                    nuevoEmpleado.numero_identificacion,
                    nuevoEmpleado.fecha_nacimiento, nuevoEmpleado.correo_electronico, nuevoEmpleado.telefono,
                    nuevoEmpleado.calle,
                    nuevoEmpleado.numero_calle, nuevoEmpleado.localidad, nuevoEmpleado.partido,
                    nuevoEmpleado.provincia,
                    nuevoEmpleado.genero, nuevoEmpleado.pais_nacimiento, nuevoEmpleado.estado_civil
                )
            )
            empleado = cur.fetchone()
            conn.commit()
            return {
                "id_empleado": empleado[0],
                "numero_identificacion": empleado[1],
                "nombre": empleado[2],
                "apellido": empleado[3]
            }
        except psycopg2.IntegrityError as e:
            conn.rollback()
            if "numero_identificacion" in str(e):
                raise ValueError("El número de identificación ya está registrado")
            raise ValueError(f"Error de integridad: {e}")
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al crear empleado: {e}")
        finally:
            cur.close()
            db.put_conn(conn)

    @staticmethod
    def obtener_empleados():
        conn, cur = db.get_conn_cursor()
        try:
            cur.execute(
                """
                SELECT id_empleado, numero_identificacion, nombre, apellido, correo_electronico, telefono
                FROM empleado
                ORDER BY apellido, nombre
                """
            )
            return [
                {
                    "id_empleado": row[0],
                    "numero_identificacion": row[1],
                    "nombre": row[2],
                    "apellido": row[3],
                    "correo": row[4],
                    "telefono": row[5]
                }
                for row in cur.fetchall()
            ]
        except Exception as e:
            print(f"\u274c Error en obtener_empleados: {e}")
            return []
        finally:
            cur.close()
            db.put_conn(conn)

    @staticmethod
    def obtener_detalle_empleado(numero_identificacion: str):
        conn, cur = db.get_conn_cursor()
        try:
            cur.execute(
                """
                SELECT id_empleado, nombre, apellido, tipo_identificacion, numero_identificacion,
                       fecha_nacimiento, correo_electronico, telefono, calle,
                       numero_calle, localidad, partido, genero, pais_nacimiento, estado_civil
                FROM empleado
                WHERE numero_identificacion = %s
                """,
                (numero_identificacion,)
            )
            result = cur.fetchone()
            if result:
                return {
                    "id_empleado": result[0],
                    "nombre": result[1],
                    "apellido": result[2],
                    "tipo_identificacion": result[3],
                    "numero_identificacion": result[4],
                    "fecha_nacimiento": result[5],
                    "correo_electronico": result[6],
                    "telefono": result[7],
                    "calle": result[8],
                    "numero_calle": result[9],
                    "localidad": result[10],
                    "partido": result[11],
                    "genero": result[12],
                    "nacionalidad": result[13],
                    "estado_civil": result[14]
                }
            return None
        finally:
            cur.close()
            db.put_conn(conn)

    @staticmethod
    def registrar_jornada_calendario(id_empleado: int, fecha: date, estado_jornada: str,
                                     hora_entrada: time = None, hora_salida: time = None,
                                     horas_trabajadas: int = None, horas_extras: int = None,
                                     descripcion: str = None):
        conn, cur = db.get_conn_cursor()
        try:
            cur.execute(
                "SELECT 1 FROM calendario WHERE id_empleado = %s AND fecha = %s",
                (id_empleado, fecha)
            )
            existe = cur.fetchone()

            if existe:
                cur.execute(
                    """
                    UPDATE calendario SET
                        estado_jornada = %s,
                        hora_entrada = %s,
                        hora_salida = %s,
                        horas_trabajadas = %s,
                        horas_extras = %s,
                        descripcion = %s
                    WHERE id_empleado = %s AND fecha = %s
                    RETURNING id_asistencia
                    """,
                    (
                        estado_jornada, hora_entrada, hora_salida,
                        horas_trabajadas, horas_extras, descripcion,
                        id_empleado, fecha
                    )
                )
            else:
                cur.execute(
                    """
                    INSERT INTO calendario (
                        id_empleado, fecha, dia, estado_jornada,
                        hora_entrada, hora_salida, horas_trabajadas,
                        horas_extras, descripcion
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_asistencia
                    """,
                    (
                        id_empleado, fecha, fecha.strftime("%A"),
                        estado_jornada, hora_entrada, hora_salida,
                        horas_trabajadas, horas_extras, descripcion
                    )
                )

            conn.commit()
            return cur.fetchone()[0]
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al registrar jornada: {e}")
        finally:
            cur.close()
            db.put_conn(conn)

    @staticmethod
    def obtener_calendario_empleado(id_empleado: int, mes: int = None, anio: int = None):
        conn, cur = db.get_conn_cursor()
        try:
            query = """
                SELECT id_asistencia, fecha, dia, estado_jornada,
                       hora_entrada, hora_salida, horas_trabajadas,
                       horas_extras, descripcion
                FROM calendario
                WHERE id_empleado = %s
            """
            params = [id_empleado]

            if mes and anio:
                query += " AND EXTRACT(MONTH FROM fecha) = %s AND EXTRACT(YEAR FROM fecha) = %s"
                params.extend([mes, anio])

            query += " ORDER BY fecha DESC"

            cur.execute(query, params)
            return [
                {
                    "id_asistencia": row[0],
                    "fecha": row[1],
                    "dia": row[2],
                    "estado_jornada": row[3],
                    "hora_entrada": row[4].strftime("%H:%M") if row[4] else None,
                    "hora_salida": row[5].strftime("%H:%M") if row[5] else None,
                    "horas_trabajadas": row[6],
                    "horas_extras": row[7],
                    "descripcion": row[8]
                }
                for row in cur.fetchall()
            ]
        finally:
            cur.close()
            db.put_conn(conn)

    @staticmethod
    def buscar_empleado_por_numero_identificacion(numero_identificacion: str):
        conn, cur = db.get_conn_cursor()
        try:
            cur.execute(
                """
                SELECT id_empleado, numero_identificacion, nombre, apellido, correo_electronico, telefono
                FROM empleado
                WHERE numero_identificacion = %s
                """,
                (numero_identificacion,)
            )
            result = cur.fetchone()
            if result:
                return {
                    "id_empleado": result[0],
                    "numero_identificacion": result[1],
                    "nombre": result[2],
                    "apellido": result[3],
                    "correo": result[4],
                    "telefono": result[5]
                }
            return None
        finally:
            cur.close()
            db.put_conn(conn)

    @staticmethod
    def buscar_avanzado(nombre=None, apellido=None, dni=None, pagina=1, por_pagina=10):
        base_query = """
            SELECT id_empleado, nombre, apellido, tipo_identificacion, numero_identificacion, 
                fecha_nacimiento, correo_electronico, telefono, calle, numero_calle, 
                localidad, partido, provincia, genero, nacionalidad, estado_civil
            FROM empleados
            WHERE 1=1
        """
        count_query = "SELECT COUNT(*) FROM empleados WHERE 1=1"

        params = []
        filters = []
        if nombre:
            filters.append("nombre ILIKE %s")
            params.append(f"%{nombre}%")

        if apellido:
            filters.append("apellido ILIKE %s")
            params.append(f"%{apellido}%")

        if dni:
            filters.append("numero_identificacion LIKE %s")
            params.append(f"%{dni}%")

        if filters:
            where_clause = " AND " + " AND ".join(filters)
            base_query += where_clause
            count_query += where_clause

        base_query += " LIMIT %s OFFSET %s"
        params.extend([por_pagina, (pagina - 1) * por_pagina])

        conn, cur = db.get_conn_cursor()
        try:
            cur.execute(base_query, tuple(params))
            results = cur.fetchall()

            cur.execute(count_query, tuple(params[:-2]))
            total = cur.fetchone()[0]

            empleados = [
                Empleado(
                    id_empleado=row[0], nombre=row[1], apellido=row[2], tipo_identificacion=row[3],
                    numero_identificacion=row[4], fecha_nacimiento=row[5], correo_electronico=row[6],
                    telefono=row[7], calle=row[8], numero_calle=row[9], localidad=row[10],
                    partido=row[11], provincia=row[12], genero=row[13], nacionalidad=row[14], estado_civil=row[15]
                ) for row in results
            ]
            return empleados, total
        finally:
            cur.close()
            db.put_conn(conn)

    @staticmethod
    def crear_cuenta(usuario):
        conn, cur = db.get_conn_cursor()
        try:
            cur.execute(
                """
                INSERT INTO usuario (id_empleado, id_rol, nombre_usuario, contrasena, esta_Activo, fecha_activacion, motivo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id_usuario
                """,
                (2, 1, usuario.nombre_usuario, usuario.contrasena, True, date.today(), "")
            )
            id_usuario = cur.fetchone()[0]
            conn.commit()
            return {"mensaje": "Usuario registrado correctamente", "id_usuario": id_usuario}
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al crear cuenta: {e}")
        finally:
            cur.close()
            db.put_conn(conn)