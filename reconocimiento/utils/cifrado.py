import json

import numpy as np
from cryptography.fernet import Fernet



FERNET_KEY = b'mi_clave_de_fernet_aca_en_bytes'  
fernet = Fernet(FERNET_KEY)

def cifrar_vector(vector_np):
    vector_json = json.dumps(vector_np.tolist()).encode("utf-8")
    return fernet.encrypt(vector_json)

def descifrar_vector(vector_cifrado):
    vector_json = fernet.decrypt(vector_cifrado).decode("utf-8")
    return np.array(json.loads(vector_json))
