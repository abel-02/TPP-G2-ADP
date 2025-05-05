'''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import fichaje
from app.routes import fichar

app = FastAPI(title="Shain - Fichaje Facial")

# CORS (para pruebas desde front local en React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod usá el dominio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar las rutas
app.include_router(fichar.router, prefix="/api")

'''

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import face_recognition
from app.services.reconocimiento import identificar_persona
import os

from app.utils.utilsVectores import CARPETA_VECTORES, guardar_vector, extraer_vector
from app.utils.sesion_temp import sesiones
from app.utils.registro_asistencia import registrar_fichaje, obtener_fichajes

app = FastAPI()


@app.get("/")
def saludo():
    return "Hola"

@app.post("/fichar/neutra")
async def fichar_neutra(imagen: UploadFile = File(...)):

    # Leer imagen como numpy array
    contenido = await imagen.read()
    np_arr = np.frombuffer(contenido, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)


    # Verificar si hay rostro
    ubicaciones = face_recognition.face_locations(img)
    if not ubicaciones:
        return JSONResponse(content={"mensaje": "No se detectó rostro"}, status_code=422)

    # Reconocer persona
    nombre, distancia = identificar_persona(img)
    if nombre:
        vector_neutro = extraer_vector(contenido)

        if vector_neutro is not None:
            sesiones[nombre] = vector_neutro

        return {
            "persona_reconocida": True,
            "nombre": nombre,
            "distancia": distancia,
            "mensaje": "Se detectó un rostro conocido. Por favor, realiza el gesto solicitado."
        }
    else:
        return {
            "persona_reconocida": False,
            "mensaje": "No se detectó un rostro registrado."
        }



@app.post("/registrar")
async def registrar_persona(nombre: str = Form(...), imagen: UploadFile = File(...)):
    if not imagen.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    contenido = await imagen.read()
    np_arr = np.frombuffer(contenido, np.uint8)
    imagen_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if imagen_np is None:
        raise HTTPException(status_code=400, detail="No se pudo leer la imagen")

    ubicaciones = face_recognition.face_locations(imagen_np)
    if not ubicaciones:
        raise HTTPException(status_code=422, detail="No se detectó rostro")

    vectores = face_recognition.face_encodings(imagen_np, known_face_locations=ubicaciones)
    if not vectores:
        raise HTTPException(status_code=422, detail="No se pudo codificar el rostro")

    # Determinar siguiente contador disponible para el nombre
    contador = 1
    while os.path.exists(os.path.join(CARPETA_VECTORES, f"{nombre}_{contador}.npy")):
        contador += 1

    guardar_vector(nombre, contador, vectores[0])

    return {
        "mensaje": f"Persona '{nombre}' registrada exitosamente con vector {contador}"
    }


# Para fichar debe realizar un gesto, si la imagen es la misma que la primera, se considera no valido
@app.post("/fichar/gesto")
async def fichar_gesto(imagen: UploadFile = File(...)):
    if not imagen.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    contenido = await imagen.read()
    np_arr = np.frombuffer(contenido, np.uint8)
    imagen_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if imagen_np is None:
        raise HTTPException(status_code=400, detail="No se pudo leer la imagen")

    ubicaciones = face_recognition.face_locations(imagen_np)
    if not ubicaciones:
        raise HTTPException(status_code=422, detail="No se detectó rostro")

    vectores = face_recognition.face_encodings(imagen_np, known_face_locations=ubicaciones)
    if not vectores:
        raise HTTPException(status_code=422, detail="No se pudo codificar el rostro")

    nombre, _ = identificar_persona(imagen_np)
    if not nombre:
        return {"fichaje_completo": False, "mensaje": "No se reconoció a la persona."}

    vector_gesto = extraer_vector(contenido)
    vector_neutro = sesiones.get(nombre)

    if vector_neutro is not None:
        diferencia = np.linalg.norm(vector_gesto - vector_neutro)
        if diferencia < 0.01:
            return {
                "fichaje_completo": False,
                "mensaje": "El gesto no fue detectado (imagen repetida o sin cambio visible)."
            }

    print(f"✅ Fichaje exitoso de {nombre}")
    # Se registra y guarda la hora
    fichaje = registrar_fichaje(nombre)

    return {
        "fichaje_completo": True,
        "mensaje": f"Fichaje exitoso de {nombre}",
        "registro": fichaje
    }


@app.get("/fichadas")
def obtenerFichadas():
    return obtener_fichajes()
