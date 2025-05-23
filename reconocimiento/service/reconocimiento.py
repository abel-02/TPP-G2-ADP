
import numpy as np

from crud.database import db
from reconocimiento.utils.utilsVectores import  UMBRAL

def identificar_persona(vector_actual):
    """
    Identifica si el rostro pertenece a una persona registrada, comparando con los vectores almacenados en la base de datos.
    """

    if vector_actual is None or not isinstance(vector_actual, np.ndarray):
        print("❌ Error: Datos inválidos en identificación facial")
        return None, None

    try:
        conn, cur = db.get_conn_cursor()

        # Obtener todos los vectores biométricos registrados
        cur.execute("SELECT id_empleado, vector_biometrico FROM dato_biometrico_facial")
        registros = cur.fetchall()

        for id_empleado, vector_guardado in registros:
            if vector_guardado is None:  # Evitamos procesar datos vacíos
                print(f"🚫 Empleado {id_empleado}: No tiene datos biométricos registrados.")
                continue

            # 🛠️ Verificación del tipo de dato antes de procesarlo
            print(f"🔍 Empleado {id_empleado} - Tipo de dato: {type(vector_guardado)} - Tamaño: {len(vector_guardado)} bytes")

            # ✅ Si PostgreSQL devuelve `str`, convertirlo a `bytes` correctamente
            if isinstance(vector_guardado, str):
                try:
                    vector_guardado = bytes.fromhex(vector_guardado[2:])  # Removemos `\x` y convertimos a binario
                except ValueError as e:
                    print(f"❌ Error al convertir `str` a `bytes` para el empleado {id_empleado}: {e}")
                    continue

            # 🛠️ Verificar tamaño antes de procesar
            buffer_size = len(vector_guardado)
            element_size = np.dtype(np.float64).itemsize

            if buffer_size % element_size != 0:
                print(f"❌ Error: Buffer corrupto para el empleado {id_empleado}. Tamaño: {buffer_size}")
                print(f"🧐 Dato recuperado: {vector_guardado[:100]}")  # Muestra primeros 100 bytes para inspección
                continue  # Ignoramos el vector dañado

            # ✅ Convertir de `BYTEA` a NumPy correctamente
            vector_db = np.frombuffer(vector_guardado, dtype=np.float64)

            # Comparación de distancia
            distancia = np.linalg.norm(vector_actual - vector_db)

            if distancia < UMBRAL:
                return id_empleado, distancia  # ✅ Persona reconocida

    except Exception as e:
        print(f"❌ Error en la identificación facial: {e}")

    finally:
        cur.close()
        conn.close()

    return None, None  # 🚫 No se encontró coincidencia

