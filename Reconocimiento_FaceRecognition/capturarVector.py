import cv2
import face_recognition
import numpy as np
import os
import time
import winsound

# CONFIGURACIÓN
CAPTURAS_REQUERIDAS = 3
ESPERA_SEGUNDOS = 5
CARPETA_VECTORES = "vectores"


# ----------------------- FUNCIONES -----------------------

def inicializar_directorio():
    """Crea la carpeta de vectores si no existe."""
    os.makedirs(CARPETA_VECTORES, exist_ok=True)


def pedir_nombre():
    """Solicita al usuario el nombre del empleado y lo normaliza."""
    nombre = input("Nombre del empleado: ").strip().replace(" ", "_")
    return nombre


def capturar_rostro(frame):
    """Detecta y codifica el rostro en el frame si hay exactamente uno."""
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #Ojo aca, depende del modelo, si no ponemos "hog" usara el "cnn" (mas lento pero mas preciso)
    caras = face_recognition.face_locations(rgb,model="hog")

    if len(caras) == 1:
        encoding = face_recognition.face_encodings(rgb, known_face_locations=caras)[0]
        return encoding
    elif len(caras) > 1:
        print("[ALERTA] Se detectaron varias caras. Mostrá solo una.")
    else:
        print("[...] Buscando rostro...")
    return None


def guardar_vector(encoding, nombre, contador):
    """Guarda el encoding en un archivo .npy con nombre e índice."""
    nombre_archivo = f"{nombre}_{contador + 1}.npy"
    ruta = os.path.join(CARPETA_VECTORES, nombre_archivo)
    np.save(ruta, encoding)
    print(f"[OK] Imagen {contador + 1} guardada como {nombre_archivo}")
    winsound.Beep(1000, 500)


# ----------------------- PROGRAMA PRINCIPAL -----------------------

def main():
    inicializar_directorio()
    nombre = pedir_nombre()

    cap = cv2.VideoCapture(0)
    print("[INFO] Mostrá tu rostro. Se capturarán 3 imágenes en momentos distintos...")

    contador = 0

    while contador < CAPTURAS_REQUERIDAS:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] No se pudo capturar imagen desde la cámara.")
            break

        encoding = capturar_rostro(frame)
        if encoding is not None:
            guardar_vector(encoding, nombre, contador)
            contador += 1
            if contador < CAPTURAS_REQUERIDAS:
                print(f"[INFO] Esperando {ESPERA_SEGUNDOS} segundos para la siguiente captura...")
                time.sleep(ESPERA_SEGUNDOS)

        cv2.imshow("Captura", frame)
        if cv2.waitKey(1) == 27:  # ESC
            print("[SALIDA] Cancelado por el usuario.")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
