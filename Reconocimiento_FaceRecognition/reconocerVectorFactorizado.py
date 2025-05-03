import cv2
import face_recognition
import numpy as np
from datetime import datetime
import winsound
from utilsVectores import cargar_vectores, UMBRAL

def reconocer_persona(encoding, vectores_guardados):
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
    top, right, bottom, left = box
    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
    cv2.putText(frame, nombre, (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)


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
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
