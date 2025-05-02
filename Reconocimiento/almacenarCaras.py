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
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al obtener el frame")
            break

        cv2.imshow("Captura", frame)

        # Salir con la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()