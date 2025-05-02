#Creo carpetas donde guardo las imagenes
import os
import cv2

person = 'usuario'
dataPath= 'data'
personPath = dataPath + '/' + person

#obs: (se guardaria las caras de cada persona en cada carpeta)

# Crear carpeta si no existe
if not os.path.exists(personPath):
    print('Carpeta creada: ', personPath)
    os.makedirs(personPath)



#Abre frame que muestra la camara y sale con q

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error al abrir la cámara")
else:


    # Cargar el clasificador de Haar para detección de rostros
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Iniciar la captura de video
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectar rostros en la imagen
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

        # Dibujar rectángulos alrededor de los rostros detectados
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.imshow('Detección de Rostros', frame)

        # Salir con la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()