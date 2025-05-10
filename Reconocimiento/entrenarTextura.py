import cv2
import os
import numpy as np
from skimage.feature import local_binary_pattern
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
import joblib

# Configuración (puedes mover esto a tu archivo principal si lo prefieres)
DEFAULT_RADIUS = 3
DEFAULT_N_POINTS = 24


def load_images(folder_path, label):
    """Carga imágenes y asigna etiquetas (1=real, 0=spoofing)."""
    images = []
    labels = []
    for filename in os.listdir(folder_path):
        img_path = os.path.join(folder_path, filename)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            img = cv2.resize(img, (100, 100))  # Normaliza tamaño
            images.append(img)
            labels.append(label)
    return images, labels


def extract_lbp_features(images, radius=DEFAULT_RADIUS, n_points=DEFAULT_N_POINTS):
    """Extrae histogramas LBP de una lista de imágenes."""
    features = []
    for img in images:
        lbp = local_binary_pattern(img, n_points, radius, method='uniform')
        hist, _ = np.histogram(lbp, bins=n_points + 2, range=(0, n_points + 2))
        hist = hist.astype("float")
        hist /= (hist.sum() + 1e-6)  # Normalización
        features.append(hist)
    return np.array(features)


def train_texture_model(real_path, spoof_path, model_save_path='texture_model.pkl', test_size=0.2):
    """Entrena y guarda el modelo de detección de texturas."""
    #  Cargar datos
    real_images, real_labels = load_images(real_path, 1)
    spoof_images, spoof_labels = load_images(spoof_path, 0)

    #  Extraer características
    X = real_images + spoof_images
    y = real_labels + spoof_labels
    X_features = extract_lbp_features(X)

    #  Entrenar modelo
    X_train, _, y_train, _ = train_test_split(X_features, y, test_size=test_size, random_state=42)
    model = SVC(kernel='linear', probability=True, random_state=42)
    model.fit(X_train, y_train)

    #  Guardar modelo
    joblib.dump(model, model_save_path)
    return mode