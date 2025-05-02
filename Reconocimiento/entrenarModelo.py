import cv2
import os
import numpy as np


dataPath = 'data'  # Carpeta donde tienes los rostros
peopleList = os.listdir(dataPath)

if not peopleList:
    print("Error: No hay datos para entrenar, la carpeta data esta vacia")
    exit()

labels = []
facesData = []
label = 0

# Leer imágenes de entrenamiento
for person in peopleList:
    personPath = dataPath + '/' + person
    for fileName in os.listdir(personPath):
        imagePath = personPath + '/' + fileName
        image = cv2.imread(imagePath, cv2.IMREAD_GRAYSCALE)
        facesData.append(image)
        labels.append(label)
    label += 1

# Crear y entrenar el modelo
face_recognizer = cv2.face.LBPHFaceRecognizer.create()
face_recognizer.train(facesData, np.array(labels))

# Guardar el modelo entrenado
face_recognizer.write('modeloLBPH.xml')
print("Modelo entrenado y guardado.")