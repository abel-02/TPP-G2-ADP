import cv2
import face_recognition
import numpy as np
import os
from datetime import datetime
import winsound


# CONFIGURACIÓN
UMBRAL = 0.5
CARPETA_VECTORES = "vectores"


# ----------------------- FUNCIONES -----------------------

def cargar_vectores():
    """
    Carga todos los vectores .npy de la carpeta y agrupa por persona.
    Ejemplo: "Pedro_1.npy", "Pedro_2.npy" → vectores["Pedro"] = [v1, v2]
    """
    vectores = {}
    for archivo in os.listdir(CARPETA_VECTORES):
        if archivo.endswith(".npy"):
            nombre_base = archivo.split("_")[0]
            vector = np.load(os.path.join(CARPETA_VECTORES, archivo))
            vectores.setdefault(nombre_base, []).append(vector)
    return vectores


def reconocer_persona(encoding, vectores_guardados):
    """
    Compara un encoding con todos los vectores guardados.
    Devuelve el nombre detectado o 'Desconocido'
    """
    nombre_detectado = "Desconocido"
    menor_distancia = 1.0

    for nombre, lista_vectores in vectores_guardados.items():
        for vector in lista_vectores:
            distancia = np.linalg.norm(encoding - vector)
            if distancia < menor_distancia and distancia < UMBRAL:
                menor_distancia = distancia
                nombre_detectado = nombre

    return nombre_detectado


def registrar(nombre, registro_estado, ultimos_tiempos):
    """
    Registra entrada o salida con lógica de alternancia y anti-repetición
    """
    ahora = datetime.now()
    if nombre not in registro_estado:
        registro_estado[nombre] = False

    if (nombre not in ultimos_tiempos or
        (ahora - ultimos_tiempos[nombre]).seconds > 10):

        if not registro_estado[nombre]:
            print(f"Bienvenido {nombre}, ingresaste a las {ahora.strftime('%H:%M')}")
            registro_estado[nombre] = True
        else:
            print(f"Hasta luego {nombre}, saliste a las {ahora.strftime('%H:%M')}")
            registro_estado[nombre] = False

        ultimos_tiempos[nombre] = ahora
        winsound.Beep(1000, 500)


def mostrar_etiqueta(frame, box, nombre):
    """
    Dibuja el rectángulo y el nombre sobre el rostro detectado
    """
    top, right, bottom, left = box
    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
    cv2.putText(frame, nombre, (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)


# ----------------------- PROGRAMA PRINCIPAL -----------------------

def main():
    vectores_guardados = cargar_vectores()
    print(f"[INFO] Vectores cargados: {list(vectores_guardados.keys())}")

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    registro_estado = {}
    ultimos_tiempos = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ubicaciones = face_recognition.face_locations(rgb, model="hog")
        codificaciones = face_recognition.face_encodings(rgb, known_face_locations=ubicaciones)

        for box, encoding in zip(ubicaciones, codificaciones):
            nombre = reconocer_persona(encoding, vectores_guardados)
            if nombre != "Desconocido":
                registrar(nombre, registro_estado, ultimos_tiempos)

            mostrar_etiqueta(frame, box, nombre)

        cv2.imshow("Shain Flow", frame)
        if cv2.waitKey(1) == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
