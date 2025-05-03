import cv2
import face_recognition
import time
import winsound
from utilsVectores import guardar_vector

# Ingreso de nombre
nombre = input("Nombre del empleado: ").strip().replace(" ", "_")
espera_segundos = 5
contador = 0

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # ✅ Mejora rendimiento
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

print("[INFO] Mostrá tu rostro. Se capturarán 3 imágenes...")

while contador < 3:
    ret, frame = cap.read()
    if not ret:
        print("No se pudo capturar imagen.")
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    caras = face_recognition.face_locations(rgb)

    if len(caras) == 1:
        encoding = face_recognition.face_encodings(rgb, known_face_locations=caras)[0]
        guardar_vector(nombre, contador + 1, encoding)
        print(f"[OK] Imagen {contador+1} guardada.")
        winsound.Beep(1000, 500)
        contador += 1

        if contador < 3:
            print(f"[INFO] Esperando {espera_segundos} segundos...")
            time.sleep(espera_segundos)
    elif len(caras) > 1:
        print("[ALERTA] Varias caras detectadas.")
    else:
        print("[...] Buscando rostro...")

    cv2.imshow("Captura", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
