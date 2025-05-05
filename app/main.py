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

from app.utils.utilsVectores import CARPETA_VECTORES, guardar_vector

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