from fastapi import FastAPI, WebSocket
import face_recognition
import numpy as np
import base64
import cv2
from io import BytesIO
from datetime import datetime
from PIL import Image
import random

from reconocimiento.service.reconocimiento import identificar_persona, identificar_gesto
from reconocimiento.utils.utilsVectores import guardar_vector

app = FastAPI()

# Base de datos en memoria para fichajes
fichajes = {}

# eSTA ES LA VERSION QUE ANDABA

async def registrar_empleado(websocket, data_inicial, id_empleado):
    """Registra un empleado pidiendo imágenes de a una, validando gesto por gesto."""
    gestos_requeridos = [("normal", None), ("sonrisa", "sonrisa"), ("giro", "giro")]

    for tipo, gesto in gestos_requeridos:
        primer_intento = True
        while True:
            if primer_intento:
                await websocket.send_text(f"📸 Por favor, envía imagen del gesto: '{tipo}'")
                primer_intento = False  # Ya pedimos la imagen

            data = await websocket.receive_json()

            try:
                image_data = base64.b64decode(data[f"imagen_{tipo}"])
                image = np.array(Image.open(BytesIO(image_data)))
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                face_encodings = face_recognition.face_encodings(rgb_image)

                if not face_encodings:
                    await websocket.send_text(f"❌ No se detectó rostro en imagen '{tipo}', intenta de nuevo")
                    continue

                vector_actual = face_encodings[0].astype(np.float64)

                if gesto:
                    if not identificar_gesto(rgb_image, gesto):
                        await websocket.send_text(f"🚫 El gesto '{gesto}' no fue detectado correctamente, intenta de nuevo")
                        continue  # 👈 volver a pedir imagen sin mandar alerta nueva

                # ✅ Gesto validado: guardar vector
                guardar_vector(id_empleado, tipo, vector_actual)
                break  # 👉 pasar al siguiente gesto

            except Exception as e:
                await websocket.send_text(f"⚠️ Error procesando imagen '{tipo}': {e}")
                continue

    await websocket.send_text(f"✅ Persona '{id_empleado}' registrada correctamente con gestos")
    print(f"✅ Persona '{id_empleado}' registrada")


async def verificar_identidad(websocket, data):
    """Verifica identidad con reconocimiento facial y un gesto (liveness)"""
    image_data = base64.b64decode(data["imagen"])
    image = np.array(Image.open(BytesIO(image_data)))
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_encodings = face_recognition.face_encodings(rgb_image)

    if not face_encodings:
        await websocket.send_text("🚫 No se detectó un rostro válido")
        return

    vector_actual = face_encodings[0]
    vector_actual = vector_actual.astype(np.float64)  # 👈 Asegura tipo correcto

    nombre_detectado, distancia = identificar_persona(vector_actual)

    if not nombre_detectado:
        await websocket.send_text("🚫 Persona no reconocida")
        return

    # ✅ Gesto aleatorio requerido
    gesto_requerido = random.choice(["sonrisa", "giro", "cejas"])

    # 🔁 Intentar gesto varias veces
    for intento in range(3):
        await websocket.send_text(f"🔄 Por favor, realiza el gesto: {gesto_requerido}")
        nueva_data = await websocket.receive_json()

        try:
            image_data_gesto = base64.b64decode(nueva_data["imagen"])
            image_gesto = np.array(Image.open(BytesIO(image_data_gesto)))
            rgb_image_gesto = cv2.cvtColor(image_gesto, cv2.COLOR_BGR2RGB)
            face_encodings_gesto = face_recognition.face_encodings(rgb_image_gesto)

            if not face_encodings_gesto:
                await websocket.send_text("❌ No se detectó rostro en la imagen del gesto")
                continue

            if not identificar_gesto(rgb_image_gesto, gesto_requerido):
                await websocket.send_text(
                    f"🚫 El gesto '{gesto_requerido}' no fue detectado. Intenta de nuevo: realiza el gesto '{gesto_requerido}'")
                continue

            # 🎉 Gesto válido
            fichajes[nombre_detectado] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await websocket.send_text(f"✅ {nombre_detectado} fichado con verificación de liveness a las {fichajes[nombre_detectado]}")
            print(f"✅ {nombre_detectado} fichado correctamente")
            return

        except Exception as e:
            await websocket.send_text(f"⚠️ Error procesando imagen del gesto: {e}")
            continue

    # ❌ Si falló tras 3 intentos
    await websocket.send_text("🚫 Verificación fallida después de varios intentos. Intenta nuevamente.")
    print("🚫 Fichaje bloqueado por fallo de gesto")




@app.get("/fichadas")
async def obtener_fichajes():
    return fichajes