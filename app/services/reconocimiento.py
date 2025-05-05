import face_recognition
import numpy as np

from app.utils.utilsVectores import cargar_vectores, UMBRAL


def identificar_persona(imagen_np):

    if imagen_np is None:
        print("❌ Error al procesar la imagen con OpenCV")
        return None, None

    # Detectar rostro
    vectores = face_recognition.face_encodings(imagen_np)
    if not vectores:
        print("🚫 No se detectó ningún rostro")
        return None, None

    vector_actual = vectores[0]

    # Cargar los vectores de personas
    datos_vectores = cargar_vectores()

    for persona_id, vectores_guardados in datos_vectores.items():
        for vector_guardado in vectores_guardados:
            distancia = np.linalg.norm(vector_actual - vector_guardado)
            if distancia < UMBRAL:
                return persona_id, distancia  # ✅ Devuelve siempre una tupla válida

    return None, None  # Asegurar siempre una tupla de retorno



