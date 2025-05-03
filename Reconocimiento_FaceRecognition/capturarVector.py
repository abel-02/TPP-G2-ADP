import cv2
import face_recognition
import time
import winsound
from utilsVectores import guardar_vector

# Ingreso de nombre
nombre = input("Nombre del empleado: ").strip().replace(" ", "_")

# Tiempo de espera entre que saca las fotos
espera_segundos = 5

# Cuenta cuantas fotos saca
contador = 0

#Cuantas fotos queremos obtener de cada persona
cantidad_fotos = 3

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # ✅ Mejora rendimiento
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

print("[INFO] Mostrá tu rostro. Se capturarán 3 imágenes...")

while contador < cantidad_fotos:
    ret, frame = cap.read()
    if not ret:
        print("No se pudo capturar imagen.")
        break

    # Ajuste de frames, para mejor procesamiento
 #   frame2 = cv2.resize(frame, (0, 0), None, 0.25, 0.25)

    #Se convierte a formato rgb porque face_recognition lo necesita asi
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #Busca las caras que ve en la camara
    caras = face_recognition.face_locations(rgb)

    # Debe capturar el rostro de una persona a la vez
    if len(caras) == 1:
        encoding = face_recognition.face_encodings(rgb, known_face_locations=caras)[0]
        guardar_vector(nombre, contador + 1, encoding)
        print(f"[OK] Imagen {contador+1} guardada.")
        winsound.Beep(1000, 500)
        contador += 1

        if contador < 3:
            print(f"[INFO] Esperando {espera_segundos} segundos...")
            time.sleep(espera_segundos)

    # Si detecta más de un rostro no lo registrará
    elif len(caras) > 1:
        print("[ALERTA] Varias caras detectadas.")

    # Si no detecta rostros se queda esperando hasta captar uno
    else:
        print("[...] Buscando rostro...")

    cv2.imshow("Captura", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
