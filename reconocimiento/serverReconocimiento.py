
import psycopg2

from crud.database import db
from reconocimiento.service.reconocimiento import identificar_persona

import base64
import numpy as np
import cv2
import face_recognition
from PIL import Image
from io import BytesIO
from datetime import datetime

fichajes = {}


def procesar_imagen(data):
    """Convierte la imagen recibida en un formato compatible para reconocimiento facial."""
    image_data = base64.b64decode(data["imagen"])
    image = Image.open(BytesIO(image_data))
    image = np.array(image)

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

    print(f"Rostros detectados: {len(face_locations)}")

    if not face_encodings:
        return None, "🚫 No se detectó un rostro válido"

    return face_encodings[0], None

# Metodo del prototipo
#def registrar_persona(nombre, vector):
#    """Guarda el vector facial de una nueva persona."""
#    contador = 1
#    while os.path.exists(os.path.join("../vectores", f"{nombre}_{contador}.npy")):
#        contador += 1

#    guardar_vector(nombre, contador, vector)
#    return f"✅ Persona '{nombre}' registrada exitosamente con vector {contador}"



def registrar_dato_biometrico_facial(id_empleado, vector):
    """Registra el vector biométrico asegurando que está correctamente en formato `float64`."""

    try:
        conn, cur = db.get_conn_cursor()

        # Validar `id_empleado`
        if id_empleado is None or not isinstance(id_empleado, int):
            return "❌ Error: ID del empleado no es válido."

        # Convertir el vector a `float64`
        vector_np = np.array(vector, dtype=np.float64)
        vector_bytes = vector_np.tobytes()

        # 🛠️ Verificar que el tamaño sea múltiplo de `8`
        buffer_size = vector_np.nbytes
        element_size = np.dtype(np.float64).itemsize
        if buffer_size % element_size != 0:
            return f"❌ Error: Tamaño del vector inválido ({buffer_size}), debe ser múltiplo de {element_size}."

        # Insertar en la base de datos
        query = "INSERT INTO dato_biometrico_facial (id_empleado, vector_biometrico) VALUES (%s, %s)"
        cur.execute(query, (id_empleado, psycopg2.Binary(vector_bytes)))
        conn.commit()

        return f"✅ Vector biométrico registrado correctamente para el empleado con ID '{id_empleado}'."

    except Exception as e:
        return f"❌ Error al registrar el vector biométrico: {e}"

    finally:
        cur.close()
        conn.close()


def detectar_persona(vector):
    """Identifica si el empleado ya está registrado comparando con la base de datos."""

    try:
        conn, cur = db.get_conn_cursor()
        id_empleado, distancia = identificar_persona(vector)

        if id_empleado:
            fichajes[id_empleado] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return f"✅ Empleado ID {id_empleado} fichado a las {fichajes[id_empleado]}"

        return "❌ Rostro NO reconocido"

    except Exception as e:
        return f"❌ Error en la identificación de persona: {e}"

    finally:
        cur.close()
        conn.close()


def obtener_vector(id_empleado):
    """Recupera el vector biométrico usando el ID del empleado."""

    try:
        conn, cur = db.get_conn_cursor()
        cur.execute("SELECT vector_biometrico FROM dato_biometrico_facial WHERE id_empleado = %s", (id_empleado,))
        resultado = cur.fetchone()

        if resultado:
            vector_recuperado = np.frombuffer(resultado[0], dtype=np.float64)
            return vector_recuperado

        return None

    except Exception as e:
        return f"❌ Error al obtener el vector biométrico: {e}"

    finally:
        cur.close()
        conn.close()

