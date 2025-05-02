import cv2
import os
import numpy as np

# Cargar el modelo entrenado
face_recognizer = cv2.face.LBPHFaceRecognizer_create()
face_recognizer.read('modeloLBPH.xml')

# Cargar el clasificador de Haar para detectar rostros
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Definir etiquetas (ajusta con los nombres de las personas)
dataPath = 'data'
peopleList = os.listdir(dataPath)
print("Personas reconocidas:", peopleList)

cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        face_img = gray[y:y + h, x:x + w]

        # Reconocer el rostro
        label, confidence = face_recognizer.predict(face_img)

        # Mostrar el resultado
        text = f"{peopleList[label]} - {confidence:.2f}" if confidence < 60 else "Desconocido"
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("Reconocimiento Facial", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()