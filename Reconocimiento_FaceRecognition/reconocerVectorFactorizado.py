import cv2
import dlib
import face_recognition
import joblib
import numpy as np
from datetime import datetime
import winsound
from skimage.feature import local_binary_pattern

from Reconocimiento.entrenarGesto import detector
from utilsVectores import cargar_vectores, UMBRAL


# Devuelve el nombre de la persona que encontró la coincidencia
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

# Registra el horario de entrada o salida
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

# Muestra el rectangulo con el nombre de la persona que encontro (o desconocido)
def mostrar_etiqueta(frame, box, nombre):
    top, right, bottom, left = box
    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
    cv2.putText(frame, nombre, (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)


def validar_textura(face_roi, texture_model):
    """Verifica si el rostro es real (no una foto) usando LBP."""
    gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
    lbp = local_binary_pattern(gray, 8, 1, method="uniform")
    hist, _ = np.histogram(lbp, bins=256, range=(0, 256))
    es_real = texture_model.predict([hist])[0] == 1
    return es_real


def detectar_gesto(face_roi, predictor, gestos_model):
    """Identifica sonrisa o guiño con landmarks faciales."""
    gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    if len(faces) == 0:
        return None

    landmarks = predictor(gray, faces[0])
    landmarks_np = np.array([[p.x, p.y] for p in landmarks.parts()])

    # Ejemplo simplificado: Sonrisa si la boca está abierta
    mouth_open = (landmarks_np[66][1] - landmarks_np[62][1]) > 20  # Puntos de la boca
    return "sonrisa" if mouth_open else "neutro"


def main():
    # Cargar modelos
    vectores_guardados = cargar_vectores()
    texture_model = joblib.load("texture_model.pkl")  # Modelo de texturas
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    gestos_model = joblib.load("gestos_model.pkl")  # Modelo de gestos (SVM)

    cap = cv2.VideoCapture(0)
    registro_estado = {}
    ultimos_tiempos = {}
    foto_counter = 0  # Contador para alternar entre foto 1 y 2

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ubicaciones = face_recognition.face_locations(rgb, model="hog")
        codificaciones = face_recognition.face_encodings(rgb, known_face_locations=ubicaciones)

        for box, encoding in zip(ubicaciones, codificaciones):
            top, right, bottom, left = box
            face_roi = frame[top:bottom, left:right]

            # Foto 1: Reconocimiento biométrico + textura
            if foto_counter == 0:
                nombre = reconocer_persona(encoding, vectores_guardados)
                es_real = validar_textura(face_roi, texture_model)

                if nombre != "Desconocido" and es_real:
                    print(f"Biometría OK: {nombre}")
                    foto_counter = 1  # Pasamos a la segunda foto

            # Foto 2: Gestos + textura
            elif foto_counter == 1:
                gesto = detectar_gesto(face_roi, predictor, gestos_model)
                es_real = validar_textura(face_roi, texture_model)

                if gesto == "sonrisa" and es_real:
                    print("Gestos OK: Sonrisa detectada")
                    registrar(nombre, registro_estado, ultimos_tiempos)
                    foto_counter = 0  # Reiniciamos el ciclo

            mostrar_etiqueta(frame, box, nombre if foto_counter == 0 else "Verificando gesto...")

        cv2.imshow("Shain Flow", frame)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
