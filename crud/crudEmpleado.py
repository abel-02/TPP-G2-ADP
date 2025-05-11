import uuid
from datetime import datetime, timedelta
from database import db


class Empleado:
    def __init__(self, id_empleado=None, nombre=None, apellido=None, tipo_identificacion=None, numero_identificacion=None,
                 fecha_nacimiento=None, correo_electronico=None, telefono=None,
                 calle=None, numero_calle=None, localidad=None, provincia=None, genero=None, nacionalidad=None, estado_civil=None):
        self.id_empleado = id_empleado or str(uuid.uuid4())
        self.nombre = nombre
        self.apellido = apellido
        self.tipo_identificacion= tipo_identificacion
        self.numero_identificacion= numero_identificacion
        self.fecha_nacimiento = fecha_nacimiento
        self.correo_electronico = correo_electronico
        self.telefono = telefono
        self.calle= calle
        self.numero_calle= numero_calle,
        self.localidad= localidad
        self.provincia= provincia
        self.genero = genero
        self.nacionalidad = nacionalidad
        self.estado_civil = estado_civil

    @staticmethod
    def crear(id_empleado, nombre, apellido, tipo_identificacion, numero_identificacion,
            fecha_nacimiento, correo_electronico, telefono, calle, numero_calle, localidad,
              genero, nacionalidad, estado_civil):
        """Crea un nuevo empleado"""
        try:
            with db.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO empleados (id_empleado, nombre, apellido, tipo_identificacion, numero_identificacion, 
                    fecha_nacimiento, correo_electronico, telefono, calle, numero_calle, localidad, genero, nacionalidad, estado_civil)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_empleado
                """,
                (
                    str(uuid.uuid4()),  # Generamos nuevo UUID
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
                    genero,
                    nacionalidad,
                    estado_civil
                )
            )
                id_empleado = cur.fetchone()[0]
                db.conn.commit()
                return Empleado.obtener_por_id(id_empleado)
        except Exception as e:
            db.conn.rollback()
            raise ValueError(f"Error al crear empleado: {e}")

    @staticmethod
    def obtener_por_id(id_empleado):
        """Obtiene un empleado por su ID"""
        with db.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id_empleado, nombre, apellido, tipo_identificacion, numero_identificacion, 
                    fecha_nacimiento, correo_electronico, telefono, calle, numero_calle, 
                    localidad, provincia, genero, nacionalidad, estado_civil
                FROM empleados
                WHERE id_empleado = %s
                """,
                (str(id_empleado),)
            )
            result = cur.fetchone()
            if result:
                return Empleado(
                    id_empleado=result[0],
                    nombre=result[1],
                    apellido=result[2],
                    tipo_identificacion=result[3],
                    numero_identificacion=result[4],
                    fecha_nacimiento=result[5],
                    correo_electronico=result[6],
                    telefono=result[7],
                    calle=result[8],
                    numero_calle=result[9],
                    localidad=result[10],
                    provincia=result[11],
                    genero=result[12],
                    nacionalidad=result[13],
                    estado_civil=result[14]
                )
            return None  # En caso de no encontrar

    @staticmethod
    def obtener_por_numero_identificacion(numero_identificacion):
        """Obtiene un empleado por su número de identificación"""
        with db.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id_empleado, nombre, apellido, tipo_identificacion, numero_identificacion, 
                    fecha_nacimiento, correo_electronico, telefono, calle, numero_calle, 
                    localidad, provincia, genero, nacionalidad, estado_civil
                FROM empleados
                WHERE numero_identificacion = %s
                """,
                (numero_identificacion,)
            )
            result = cur.fetchone()
            if result:
                return Empleado(
                    id_empleado=result[0],
                    nombre=result[1],
                    apellido=result[2],
                    tipo_identificacion=result[3],
                    numero_identificacion=result[4],
                    fecha_nacimiento=result[5],
                    correo_electronico=result[6],
                    telefono=result[7],
                    calle=result[8],
                    numero_calle=result[9],
                    localidad=result[10],
                    provincia=result[11],
                    genero=result[12],
                    nacionalidad=result[13],
                    estado_civil=result[14]
                )
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
    def registrar_asistencia(id_empleado: int, vector_biometrico: str):
        """
        Registra una nueva asistencia biométrica con toda la lógica de validación

        Args:
            id_empleado (int): ID del empleado
            vector_biometrico (str): Vector biométrico capturado

        Returns:
            RegistroHorario: Instancia del nuevo registro

        Raises:
            ValueError: Si hay error en los datos o en la operación
        """
        try:
            with db.conn.cursor() as cur:
                # 1. Recuperar información laboral del empleado
                cur.execute(
                    "SELECT puesto, turno, hora_inicio_turno, hora_fin_turno "
                    "FROM informacion_laboral WHERE id_empleado = %s",
                    (id_empleado,)
                )
                resultado = cur.fetchone()

                if not resultado:
                    raise ValueError("No se encontró información laboral para el empleado")

                puesto, turno, hora_inicio_turno, hora_fin_turno = resultado

                # 2. Determinar tipo y estado de la asistencia
                now = datetime.now()
                fecha_actual = now.date()
                hora_actual = now.time()

                # Convertir a datetime para comparaciones
                entrada_dt = datetime.combine(fecha_actual, hora_inicio_turno)
                salida_dt = datetime.combine(fecha_actual, hora_fin_turno)
                actual_dt = datetime.combine(fecha_actual, hora_actual)

                # Tolerancias
                tiempo_permitido_entrada_temprana = timedelta(minutes=60)
                tolerancia_a_tiempo = timedelta(minutes=5)
                retraso_minimo = timedelta(minutes=15)

                # Lógica de determinación
                if entrada_dt - tiempo_permitido_entrada_temprana < actual_dt < entrada_dt:
                    tipo = "Entrada"
                    estado_asistencia = "Temprana"
                elif entrada_dt <= actual_dt <= entrada_dt + tolerancia_a_tiempo:
                    tipo = "Entrada"
                    estado_asistencia = "A tiempo"
                elif entrada_dt + tolerancia_a_tiempo < actual_dt <= entrada_dt + retraso_minimo:
                    tipo = "Entrada"
                    estado_asistencia = "Retraso minimo"
                elif entrada_dt + retraso_minimo < actual_dt < salida_dt - timedelta(hours=3):
                    tipo = "Entrada"
                    estado_asistencia = "Tarde"
                elif salida_dt - timedelta(minutes=30) <= actual_dt <= salida_dt + timedelta(minutes=30):
                    tipo = "Salida"
                    if actual_dt < salida_dt:
                        estado_asistencia = "Temprana"
                    elif actual_dt > salida_dt:
                        estado_asistencia = "Tarde"
                    else:
                        estado_asistencia = "A tiempo"
                else:
                    if actual_dt < salida_dt:
                        tipo = "Entrada"
                        estado_asistencia = "Fuera de rango"
                    else:
                        tipo = "Salida"
                        estado_asistencia = "Fuera de rango"

                # 3. Insertar en la base de datos
                cur.execute(
                    """
                    INSERT INTO asistencia_biometrica (
                        id_empleado,
                        tipo,
                        fecha,
                        hora,
                        estado_asistencia,
                        turno_asistencia,
                        puesto_del_asistente,
                        vector_capturado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_asistencia_biometrica, id_empleado, tipo, fecha, hora,
                              estado_asistencia, turno_asistencia, puesto_del_asistente, vector_capturado
                    """,
                    (
                        id_empleado,
                        tipo,
                        fecha_actual,
                        hora_actual,
                        estado_asistencia,
                        turno,
                        puesto,
                        vector_biometrico
                    )
                )

                resultado = cur.fetchone()
                db.conn.commit()

                return RegistroHorario(*resultado)

        except Exception as e:
            db.conn.rollback()
            raise ValueError(f"Error al registrar asistencia biométrica: {e}")

    @staticmethod
    def obtener_por_empleado(id_empleado: int, limite: int = None):
        """
        Obtiene los registros de asistencia de un empleado

        Args:
            id_empleado (int): ID del empleado
            limite (int): Cantidad máxima de registros a devolver

        Returns:
            List[RegistroHorario]: Lista de registros ordenados por fecha y hora descendente
        """
        try:
            with db.conn.cursor() as cur:
                query = """
                    SELECT id_asistencia_biometrica, id_empleado, tipo, fecha, hora,
                           estado_asistencia, turno_asistencia, puesto_del_asistente, vector_capturado
                    FROM asistencia_biometrica
                    WHERE id_empleado = %s
                    ORDER BY fecha DESC, hora DESC
                """

                params = [id_empleado]

                if limite:
                    query += " LIMIT %s"
                    params.append(limite)

                cur.execute(query, params)
                resultados = cur.fetchall()

                return [
                    RegistroHorario(
                        id_asistencia_biometrica=row[0],
                        id_empleado=row[1],
                        tipo=row[2],
                        fecha=row[3],
                        hora=row[4],
                        estado_asistencia=row[5],
                        turno_asistencia=row[6],
                        puesto_del_asistente=row[7],
                        vector_capturado=row[8]
                    ) for row in resultados
                ]
        except Exception as e:
            raise ValueError(f"Error al obtener registros: {e}")

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


    """
    dni_buscar = "45893639"
    empleado_encontrado = Empleado.obtener_por_dni(dni_buscar)

    if empleado_encontrado:
        print("Empleado encontrado:")
        print(f"Nombre: {empleado_encontrado.nombre} {empleado_encontrado.apellido}")
        print(f"DNI: {empleado_encontrado.dni}")
        print(f"Email: {empleado_encontrado.correo_electronico}")
    else:
        print(f"No se encontró empleado con DNI: {dni_buscar}")

#prueba de asistencia
    empleado = Empleado.obtener_por_dni("45893639")  # Usa un DNI que exista
    # O:
    """
    #empleado = Empleado.obtener_por_id("")

