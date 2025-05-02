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

count = 0  # Contador de imágenes guardadas

if not cap.isOpened():
    print("Error al abrir la cámara")
else:
    # Cargar el clasificador de Haar para detección de rostros
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

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

            # Guardar imagen detectada
            face_img = frame[y:y+h, x:x+w]  # Mantiene los colores originales

            img_path = os.path.join(personPath, f"rostro_{count}.jpg")
            cv2.imwrite(img_path, face_img)

            print(f"Imagen guardada: {img_path}")
            count += 1

        cv2.imshow('Detección de Rostros', frame)

        # Salir con la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q') or count >= 50:  # Guardará 50 imágenes antes de cerrar
            break

    cap.release()
    cv2.destroyAllWindows()
