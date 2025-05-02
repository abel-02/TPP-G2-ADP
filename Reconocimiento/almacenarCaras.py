#Creo carpetas donde guardo las imagenes
import os

person = 'usuario'
dataPath= 'data'
personPath = dataPath + '/' + person

# Crear carpeta si no existe
if not os.path.exists(personPath):
    print('Carpeta creada: ', personPath)
    os.makedirs(personPath)

#obs: (se guardaria las caras de cada persona en cada carpeta)