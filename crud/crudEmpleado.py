import uuid
from datetime import datetime, timedelta, date, time
from .database import db
import numpy as np



class Empleado:
    def __init__(self, id_empleado=None, nombre=None, apellido=None, tipo_identificacion=None,
                 numero_identificacion=None, fecha_nacimiento=None, correo_electronico=None,
                 telefono=None, calle=None, numero_calle=None, localidad=None, partido=None, provincia=None,
                 genero=None, nacionalidad=None, estado_civil=None):

        provincias_validas = ['Buenos Aires', 'Catamarca', 'Chaco', 'Chubut', 'Córdoba',
                              'Corrientes', 'Entre Ríos', 'Formosa', 'Jujuy', 'La Pampa',
                              'La Rioja', 'Mendoza', 'Misiones', 'Neuquén', 'Río Negro',
                              'Salta', 'San Juan', 'San Luis', 'Santa Cruz', 'Santa Fe',
                              'Santiago del Estero', 'Tierra del Fuego', 'Tucumán',
                              'Ciudad Autónoma de Buenos Aires']
        if provincia and provincia not in provincias_validas:
            raise ValueError(f"Provincia inválida. Opciones válidas: {provincias_validas}")

        nacionalidades_validas = ['Argentina', 'Brasil', 'Chile', 'Uruguay', 'Paraguay',
                                  'Bolivia', 'Perú', 'Ecuador', 'Colombia', 'Venezuela', 'México']
        if nacionalidad and nacionalidad not in nacionalidades_validas:
            raise ValueError(f"Nacionalidad inválida. Opciones válidas: {nacionalidades_validas}")

        tipos_id_validos = ['DNI', 'Pasaporte', 'Cédula']
        if tipo_identificacion and tipo_identificacion not in tipos_id_validos:
            raise ValueError(f"Tipo de identificación inválido. Opciones válidas: {tipos_id_validos}")

        generos_validos = ['Masculino', 'Femenino', 'No binario', 'Prefiere no especificar', 'Otro']
        if genero and genero not in generos_validos:
            raise ValueError(f"Género inválido. Opciones válidas: {generos_validos}")

        self.id_empleado = id_empleado
        self.nombre = nombre
        self.apellido = apellido
        self.tipo_identificacion = tipo_identificacion
        self.numero_identificacion = numero_identificacion
        self.fecha_nacimiento = fecha_nacimiento
        self.correo_electronico = correo_electronico
        self.telefono = telefono
        self.calle = calle
        self.numero_calle = numero_calle
        self.localidad = localidad
        self.partido = partido
        self.provincia = provincia
        self.genero = genero
        self.nacionalidad = nacionalidad
        self.estado_civil = estado_civil

    @staticmethod
    def crear(nombre, apellido, tipo_identificacion, numero_identificacion,
              fecha_nacimiento, correo_electronico, telefono, calle, numero_calle, localidad,
              partido, provincia, genero, nacionalidad, estado_civil):
        """Crea un nuevo empleado"""
        try:
            conn, cur = db.get_conn_cursor()
            id_empleado = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO empleados (id_empleado, nombre, apellido, tipo_identificacion, numero_identificacion, 
                fecha_nacimiento, correo_electronico, telefono, calle, numero_calle, localidad, partido, provincia, 
                genero, nacionalidad, estado_civil)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_empleado
                """,
                (
                    id_empleado,
                    nombre,
                    apellido,
                    tipo_identificacion,
                    numero_identificacion,
                    fecha_nacimiento,
                    correo_electronico,
                    telefono,
                    calle,
                    numero_calle,
                    localidad,
                    partido,
                    provincia,
                    genero,
                    nacionalidad,
                    estado_civil
                )
            )
            conn.commit()
            return Empleado.obtener_por_id(id_empleado)
        except Exception as e:
            conn.rollback()
            raise ValueError(f"Error al crear empleado: {e}")

    @staticmethod
    def crear_cuenta(usuario):
        conn, cur = db.get_conn_cursor()
        cur.execute(
            """
            INSERT INTO usuario (id_empleado, id_rol, nombre_usuario, contrasena, esta_Activo, fecha_activacion, motivo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id_usuario
            """,
            (2, 2, usuario.nombre_usuario, usuario.contrasena, True, date.today(), "")
        )
        id_usuario = cur.fetchone()[0]
        conn.commit()
        return {"mensaje": "Usuario registrado correctamente", "id_usuario": id_usuario}

    @staticmethod
    def obtener_por_id(id_empleado):
        conn, cur = db.get_conn_cursor()
        cur.execute(
            """
            SELECT id_empleado, nombre, apellido, tipo_identificacion, numero_identificacion, 
                   fecha_nacimiento, correo_electronico, telefono, calle, numero_calle, 
                   localidad, partido, provincia, genero, nacionalidad, estado_civil
            FROM empleados
            WHERE id_empleado = %s
            """,
            (str(id_empleado),)
        )
        result = cur.fetchone()
        if result:
            return Empleado(*result)
        return None

    @staticmethod
    def obtener_por_numero_identificacion(numero_identificacion):
        conn, cur = db.get_conn_cursor()
        cur.execute(
            """
            SELECT id_empleado, nombre, apellido, tipo_identificacion, numero_identificacion, 
                   fecha_nacimiento, correo_electronico, telefono, calle, numero_calle, 
                   localidad, partido, provincia, genero, nacionalidad, estado_civil
            FROM empleados
            WHERE numero_identificacion = %s
            """,
            (numero_identificacion,)
        )
        result = cur.fetchone()
        if result:
            return Empleado(*result)
        return None



class RegistroHorario:
    def __init__(self, id_asistencia_biometrica, id_empleado, tipo, fecha, hora,
                 estado_asistencia, turno_asistencia, puesto_del_asistente, vector_capturado):
        self.id_asistencia_biometrica = id_asistencia_biometrica
        self.id_empleado = id_empleado
        self.tipo = tipo
        self.fecha = fecha
        self.hora = hora
        self.estado_asistencia = estado_asistencia
        self.turno_asistencia = turno_asistencia
        self.puesto_del_asistente = puesto_del_asistente
        self.vector_capturado = vector_capturado

    @staticmethod
    def registrar_asistencia(id_empleado: int, vector_biometrico: np.ndarray):
        """
        Registra una nueva asistencia biométrica realizando validaciones y clasificación del registro.

        Args:
            id_empleado (int): ID del empleado.
            vector_biometrico (np.ndarray): Vector biométrico capturado (formato numpy array).

        Returns:
            RegistroHorario: Registro creado exitosamente.

        Raises:
            ValueError: Si hay un error en la operación o en los datos proporcionados.
        """
        try:
            with db.conn.cursor() as cur:
                # Obtener datos laborales
                cur.execute("""
                    SELECT puesto, turno, hora_inicio_turno, hora_fin_turno
                    FROM informacion_laboral
                    WHERE id_empleado = %s
                """, (id_empleado,))
                datos = cur.fetchone()

                if not datos:
                    raise ValueError("No se encontró información laboral del empleado.")

                puesto, turno, hora_inicio, hora_fin = datos

                # Determinar momento y estado
                ahora = datetime.now()
                fecha = ahora.date()
                hora = ahora.time()

                dt_actual = datetime.combine(fecha, hora)
                dt_entrada = datetime.combine(fecha, hora_inicio)
                dt_salida = datetime.combine(fecha, hora_fin)

                anticipacion = timedelta(minutes=60)
                tolerancia = timedelta(minutes=5)
                retraso = timedelta(minutes=15)
                margen_salida = timedelta(minutes=30)

                if dt_entrada - anticipacion < dt_actual < dt_entrada:
                    tipo, estado = "Entrada", "Temprana"
                elif dt_entrada <= dt_actual <= dt_entrada + tolerancia:
                    tipo, estado = "Entrada", "A tiempo"
                elif dt_actual <= dt_entrada + retraso:
                    tipo, estado = "Entrada", "Retraso mínimo"
                elif dt_actual < dt_salida - timedelta(hours=3):
                    tipo, estado = "Entrada", "Tarde"
                elif dt_salida - margen_salida <= dt_actual <= dt_salida + margen_salida:
                    tipo = "Salida"
                    if dt_actual < dt_salida:
                        estado = "Temprana"
                    elif dt_actual > dt_salida:
                        estado = "Tarde"
                    else:
                        estado = "A tiempo"
                else:
                    tipo = "Entrada" if dt_actual < dt_salida else "Salida"
                    estado = "Fuera de rango"

                # Insertar asistencia
                cur.execute("""
                    INSERT INTO asistencia_biometrica (
                        id_empleado, tipo, fecha, hora, estado_asistencia,
                        turno_asistencia, puesto_del_asistente, vector_capturado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_asistencia_biometrica, id_empleado, tipo, fecha, hora,
                              estado_asistencia, turno_asistencia, puesto_del_asistente, vector_capturado
                """, (
                    id_empleado, tipo, fecha, hora, estado,
                    turno, puesto, vector_biometrico.tobytes()
                ))

                db.conn.commit()
                return RegistroHorario(*cur.fetchone())

        except Exception as e:
            db.conn.rollback()
            raise ValueError(f"Error al registrar asistencia: {e}")

    @staticmethod
    def registrar_asistencia_manual(
            id_empleado: int,
            tipo: str,
            fecha: date,
            hora: time,
            estado_asistencia: str = None,
            turno_asistencia: str = None,
            puesto_del_asistente: str = None,
            vector_biometrico: str = "MANUAL"
    ):
        """
        Registra una asistencia manual (usada por personal administrativo).

        Args:
            id_empleado (int): ID del empleado.
            tipo (str): "Entrada" o "Salida".
            fecha (date): Fecha del registro.
            hora (time): Hora del registro.
            estado_asistencia (str, optional): Estado del registro (calculado si no se provee).
            turno_asistencia (str, optional): Turno del empleado.
            puesto_del_asistente (str, optional): Puesto del empleado.
            vector_biometrico (str, optional): Vector capturado (default: "MANUAL").

        Returns:
            RegistroHorario: Registro creado exitosamente.

        Raises:
            ValueError: Si los datos son inválidos o falla la operación.
        """
        try:
            with db.conn.cursor() as cur:
                if not all([estado_asistencia, turno_asistencia, puesto_del_asistente]):
                    cur.execute("""
                        SELECT puesto, turno, hora_inicio_turno, hora_fin_turno
                        FROM informacion_laboral
                        WHERE id_empleado = %s
                    """, (id_empleado,))
                    datos = cur.fetchone()

                    if not datos:
                        raise ValueError("No se encontró información laboral del empleado.")

                    puesto, turno, hora_inicio, hora_fin = datos
                    turno_asistencia = turno_asistencia or turno
                    puesto_del_asistente = puesto_del_asistente or puesto

                    if not estado_asistencia:
                        dt_registro = datetime.combine(fecha, hora)
                        dt_entrada = datetime.combine(fecha, hora_inicio)
                        dt_salida = datetime.combine(fecha, hora_fin)

                        if tipo == "Entrada":
                            if dt_registro < dt_entrada - timedelta(minutes=60):
                                estado_asistencia = "Fuera de rango"
                            elif dt_registro < dt_entrada:
                                estado_asistencia = "Temprana"
                            elif dt_registro <= dt_entrada + timedelta(minutes=5):
                                estado_asistencia = "A tiempo"
                            elif dt_registro <= dt_entrada + timedelta(minutes=15):
                                estado_asistencia = "Retraso mínimo"
                            else:
                                estado_asistencia = "Tarde"
                        elif tipo == "Salida":
                            if dt_registro < dt_salida - timedelta(minutes=30):
                                estado_asistencia = "Fuera de rango"
                            elif dt_registro < dt_salida:
                                estado_asistencia = "Temprana"
                            elif dt_registro > dt_salida + timedelta(minutes=30):
                                estado_asistencia = "Fuera de rango"
                            else:
                                estado_asistencia = "A tiempo" if dt_registro == dt_salida else "Tarde"

                if tipo not in ["Entrada", "Salida"]:
                    raise ValueError("El tipo debe ser 'Entrada' o 'Salida'.")

                cur.execute("""
                    INSERT INTO asistencia_biometrica (
                        id_empleado, tipo, fecha, hora, estado_asistencia,
                        turno_asistencia, puesto_del_asistente, vector_capturado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_asistencia_biometrica, id_empleado, tipo, fecha, hora,
                              estado_asistencia, turno_asistencia, puesto_del_asistente, vector_capturado
                """, (
                    id_empleado, tipo, fecha, hora, estado_asistencia,
                    turno_asistencia, puesto_del_asistente, vector_biometrico
                ))

                db.conn.commit()
                return RegistroHorario(*cur.fetchone())

        except Exception as e:
            db.conn.rollback()
            raise ValueError(f"Error al registrar asistencia manual: {e}")

    @staticmethod
    def obtener_por_empleado(id_empleado: int) :
        """
        Obtiene todos los registros de asistencia biométrica de un empleado.

        Args:
            id_empleado (int): ID del empleado.

        Returns:
            list[RegistroHorario]: Lista de registros de asistencia asociados al empleado.

        Raises:
            ValueError: Si ocurre un error al recuperar los datos.
        """
        try:
            with db.conn.cursor() as cur:
                cur.execute("""
                    SELECT id_asistencia_biometrica, id_empleado, tipo, fecha, hora,
                           estado_asistencia, turno_asistencia, puesto_del_asistente, vector_capturado
                    FROM asistencia_biometrica
                    WHERE id_empleado = %s
                    ORDER BY fecha DESC, hora DESC
                """, (id_empleado,))

                resultados = cur.fetchall()
                return [RegistroHorario(*fila) for fila in resultados]

        except Exception as e:
            raise ValueError(f"Error al obtener asistencias del empleado {id_empleado}: {e}")

# ESTE TODAVIA NO
    @staticmethod
    def obtener_ultimo_registro(id_empleado: int):
        """
        Obtiene el último registro de asistencia del empleado para
        verificar si la última acción fue una entrada antes de permitir otra
        """
        registros = RegistroHorario.obtener_por_empleado(id_empleado, limite=1)
        return registros[0] if registros else None

    def __repr__(self):
        return (f"<RegistroHorario {self.id_asistencia_biometrica}: {self.tipo} "
                f"el {self.fecha} a las {self.hora} ({self.estado_asistencia})>")

    @staticmethod
    def obtener_registros_mensuales(empleado_id, año, mes):
        """
        Obtiene registros de jornada por mes
        """
        inicio = datetime(año, mes, 1).date()
        fin = (inicio + timedelta(days=31)).replace(day=1)

        conn, cur = db.get_conn_cursor()
        try:
            cur.execute(
                """
                SELECT id_registro_jornada, id_empleado, fecha, hora_entrada, hora_salida,
                       estado_jornada, horas_trabajadas, observaciones
                FROM registro_jornada
                WHERE id_empleado = %s 
                  AND fecha >= %s 
                  AND fecha < %s
                ORDER BY fecha
                """,
                (empleado_id, inicio, fin)
            )
            return cur.fetchall()
        except Exception as e:
            raise ValueError(f"Error al obtener registros mensuales: {e}")
        finally:
            conn.close()

    @staticmethod
    def calcular_horas_mensuales(empleado_id, año, mes):
        """
        Calcula la suma total de horas trabajadas en un mes
        """
        inicio = datetime(año, mes, 1).date()
        fin = (inicio + timedelta(days=31)).replace(day=1)

        conn, cur = db.get_conn_cursor()
        try:
            cur.execute(
                """
                SELECT SUM(horas_trabajadas)
                FROM registro_jornada
                WHERE id_empleado = %s
                  AND fecha >= %s
                  AND fecha < %s
                """,
                (empleado_id, inicio, fin)
            )
            resultado = cur.fetchone()
            return resultado[0] if resultado[0] else 0.0
        except Exception as e:
            raise ValueError(f"Error al calcular horas mensuales: {e}")
        finally:
            conn.close()

    @staticmethod
    def actualizar_datos_personales(
            id_asistencia: int,
            tipo: str = None,
            fecha: date = None,
            hora: time = None,
            estado_asistencia: str = None,
            turno_asistencia: str = None,
            puesto_del_asistente: str = None
    ):
        """
        Actualiza los datos personales de un registro de asistencia.

        Args:
            id_asistencia (int): ID del registro a modificar.
            tipo (str, optional): "Entrada" o "Salida".
            fecha (date, optional): Nueva fecha.
            hora (time, optional): Nueva hora.
            estado_asistencia (str, optional): Nuevo estado.
            turno_asistencia (str, optional): Nuevo turno.
            puesto_del_asistente (str, optional): Nuevo puesto.

        Returns:
            RegistroHorario: Registro actualizado.

        Raises:
            ValueError: Si no se proporciona ningún campo a actualizar o si ocurre un error.
        """
        try:
            campos = {
                "tipo": tipo,
                "fecha": fecha,
                "hora": hora,
                "estado_asistencia": estado_asistencia,
                "turno_asistencia": turno_asistencia,
                "puesto_del_asistente": puesto_del_asistente
            }

            campos_actualizar = {k: v for k, v in campos.items() if v is not None}

            if not campos_actualizar:
                raise ValueError("Debe proporcionarse al menos un campo para actualizar.")

            set_clause = ", ".join([f"{campo} = %s" for campo in campos_actualizar])
            valores = list(campos_actualizar.values())

            with db.conn.cursor() as cur:
                cur.execute(f"""
                    UPDATE asistencia_biometrica
                    SET {set_clause}
                    WHERE id_asistencia_biometrica = %s
                    RETURNING id_asistencia_biometrica, id_empleado, tipo, fecha, hora,
                              estado_asistencia, turno_asistencia, puesto_del_asistente, vector_capturado
                """, (*valores, id_asistencia))

                resultado = cur.fetchone()
                if not resultado:
                    raise ValueError(f"No se encontró un registro con ID {id_asistencia}.")

                db.conn.commit()
                return RegistroHorario(*resultado)

        except Exception as e:
            db.conn.rollback()
            raise ValueError(f"Error al actualizar el registro: {e}")




