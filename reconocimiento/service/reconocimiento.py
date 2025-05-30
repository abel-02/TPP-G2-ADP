import numpy as np
from reconocimiento.utils.utilsVectores import cargar_vectores, UMBRAL

from reconocimiento.utils.utils_gestos import detectar_sonrisa, detectar_giro, detectar_cejas_levantadas

UMBRAL_GESTO = 0.35  # 🔧 Ajusta según pruebas

GESTOS_VALIDOS = {
    "sonrisa": detectar_sonrisa,
    "giro": detectar_giro,
    "cejas": detectar_cejas_levantadas
}

def identificar_persona(vector_actual):
    """Compara el rostro detectado con los registrados para identificar a la persona."""

    if vector_actual is None or not isinstance(vector_actual, np.ndarray):
        print("❌ Error: Datos inválidos en identificación facial")
        return None, None

    vector_actual = vector_actual.astype(np.float64)  # 👈 Asegura tipo correcto

    datos_vectores = cargar_vectores()

    for persona_id, vectores_guardados in datos_vectores.items():
        for tipo, vector_guardado in vectores_guardados.items():
            vector_guardado = vector_guardado.astype(np.float64)  # 👈 Asegura tipo correcto
            print(f"🧪 Tipos: actual={vector_actual.dtype}, guardado={vector_guardado.dtype}")
            distancia = np.linalg.norm(vector_actual - vector_guardado)
            if distancia < UMBRAL:
                return persona_id, distancia  # ✅ Persona reconocida

    return None, None  # 🚫 No se encontró coincidencia


def identificar_gesto(image_np, gesto_requerido):
    if gesto_requerido == "sonrisa":
        return detectar_sonrisa(image_np)
    elif gesto_requerido == "giro":
        return detectar_giro(image_np)
    elif gesto_requerido == "cejas":
        return detectar_cejas_levantadas(image_np)
    return False
