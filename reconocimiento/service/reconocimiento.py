
import numpy as np

from crud.database import db
from reconocimiento.utils.utilsVectores import  UMBRAL

import numpy as np


def identificar_persona(vector_actual):
    """
    Identifica si el rostro pertenece a una persona registrada, comparando con los vectores almacenados en la base de datos.
    """

    if vector_actual is None or not isinstance(vector_actual, np.ndarray):
        return None, None  # 🚫 Datos inválidos

    try:
        conn, cur = db.get_conn_cursor()

        # Obtener todos los vectores biométricos registrados
        cur.execute("SELECT id_empleado, vector_biometrico FROM dato_biometrico_facial")
        registros = cur.fetchall()

        for id_empleado, vector_guardado in registros:
            if vector_guardado is None:
                continue  # 🚫 Ignorar empleados sin datos biométricos

            # ✅ Convertir `BYTEA` a `bytes` si PostgreSQL lo devuelve como `str`
            if isinstance(vector_guardado, str):
                try:
                    vector_guardado = bytes.fromhex(vector_guardado[2:])
                except ValueError:
                    continue  # 🚫 Ignorar datos inválidos sin imprimir error

            # ✅ Convertir de `BYTEA` a NumPy correctamente
            vector_db = np.frombuffer(vector_guardado, dtype=np.float64)

            # Comparación de distancia
            if np.linalg.norm(vector_actual - vector_db) < UMBRAL:
                return id_empleado, None  # ✅ Persona reconocida

    except Exception:
        return None, None  # 🚫 Error en la identificación

    finally:
        cur.close()
        conn.close()

    return None, None  # 🚫 No se encontró coincidencia


