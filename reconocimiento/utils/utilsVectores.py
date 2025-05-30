import json
import os

import cv2
import face_recognition
import numpy as np
import psycopg2

from crud.database import db

# Configuración
UMBRAL = 0.5
CARPETA_VECTORES = "vectores"
os.makedirs(CARPETA_VECTORES, exist_ok=True)


TIPO_MAP = {
    "normal": "Neutro",
    "sonrisa": "Sonrisa",
    "giro": "Giro"
}


#ESTA VERSION ES LA QUE ANDABA



def guardar_vector(id_empleado: int, tipo_gesto_raw: str, vector_np):
    """
    Guarda un vector biométrico en la base de datos utilizando connection pooling.
    Si ya existe para ese id_empleado y tipo_vector, lo actualiza (ON CONFLICT DO UPDATE).
    Retorna True si la operación fue exitosa, False en caso contrario.
    """
    tipo_vector_db = TIPO_MAP.get(tipo_gesto_raw.lower())

    if tipo_vector_db is None:
        print(f"❌ Error (guardar_vector): Tipo de gesto desconocido '{tipo_gesto_raw}'.")
        return False

    try:
        conn = db.get_connection()
        cur = conn.cursor()
        vector_json = json.dumps(vector_np.tolist())

        query = """
            INSERT INTO dato_biometrico_facial (id_empleado, tipo_vector, vector_biometrico)
            VALUES (%s, %s, %s)
            ON CONFLICT (id_empleado, tipo_vector) DO UPDATE
            SET vector_biometrico = EXCLUDED.vector_biometrico
        """
        cur.execute(query, (id_empleado, tipo_vector_db, vector_json))
        conn.commit()
        print(f"✅ Vector '{tipo_vector_db}' guardado/actualizado para empleado {id_empleado}")
        return True

    except Exception as e:
        print(f"❌ Error al guardar/actualizar vector en la base de datos: {e}")
        return False

    finally:
        cur.close()
        db.return_connection(conn)




def cargar_vectores():
    """
    Carga todos los vectores biométricos de la base utilizando connection pooling.
    Devuelve un dict con la estructura:
    {
        id_empleado_1: {'neutro': vector1, 'sonrisa': vector2, ...},
        id_empleado_2: {'neutro': vector3, 'sonrisa': vector4, ...},
        ...
    }
    """
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        query = """
            SELECT id_empleado, tipo_vector, vector_biometrico
            FROM dato_biometrico_facial
        """
        cur.execute(query)
        resultados = cur.fetchall()

        todos_los_vectores = {}

        for id_empleado, tipo_vector, vector_texto in resultados:
            clave_tipo = tipo_vector.lower()

            try:
                vector_list = json.loads(vector_texto)
                vector_np = np.array([float(x) for x in vector_list], dtype=np.float64)
            except Exception as e:
                print(f"⚠️ Error convirtiendo vector para {id_empleado}, tipo {tipo_vector}: {e}")
                continue

            if id_empleado not in todos_los_vectores:
                todos_los_vectores[id_empleado] = {}

            todos_los_vectores[id_empleado][clave_tipo] = vector_np

        return todos_los_vectores

    except Exception as e:
        print(f"❌ Error al cargar vectores: {e}")
        return {}

    finally:
        cur.close()
        db.return_connection(conn)




'''
def cargar_vectores():
    """
    Carga todos los vectores .npy y los agrupa por persona (ej: Pedro_1.npy → Pedro → [v1, v2...]).
    """
    vectores = {}
    for archivo in os.listdir(CARPETA_VECTORES):
        if archivo.endswith(".npy"):
            nombre_base = archivo.split("_")[0]
            vector = np.load(os.path.join(CARPETA_VECTORES, archivo))
            vectores.setdefault(nombre_base, []).append(vector)
    return vectores


def guardar_vector(nombre, contador, vector):
    """
    Guarda un vector facial con formato {nombre}_{contador}.npy
    """
    nombre_archivo = f"{nombre}_{contador}.npy"
    ruta = os.path.join(CARPETA_VECTORES, nombre_archivo)
    np.save(ruta, vector)

def extraer_vector(imagen_bytes: bytes):
    np_arr = np.frombuffer(imagen_bytes, np.uint8)
    imagen_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    vectores = face_recognition.face_encodings(imagen_np)
    if vectores:
        return vectores[0]
    return None
'''


