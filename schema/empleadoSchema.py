from typing import Optional
from datetime import date
from pydantic import BaseModel

#Schema completo
class EmpleadoSchema(BaseModel):
    id_empleado : Optional[int]
    nombre: str
    apellido: str
    dni : int
    fecha_nacimiento: Optional[date]
    correo_electronico : str
    telefono : Optional[str]
    direccion : Optional[str]
    genero : Optional[str] #Posible enum
    nacionalidad : Optional[str]
    estado_civil: Optional[str] #Enum (tengo que crear la clase)
