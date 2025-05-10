from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.reconocimiento import identificar_persona
from app.services.liveness import verificar_liveness
#from app.db.database import registrar_fichada

router = APIRouter()

@router.post("/fichar")
async def fichar(imagen_neutra: UploadFile = File(...), imagen_gesto: UploadFile = File(...)):

    imagen1_bytes = await imagen_neutra.read()
    imagen2_bytes = await imagen_gesto.read()


    persona_id = identificar_persona(imagen1_bytes)
    if not persona_id:
        raise HTTPException(status_code=401, detail="Persona no reconocida")


    liveness_ok = verificar_liveness(imagen1_bytes, imagen2_bytes)
    if not liveness_ok:
        raise HTTPException(status_code=403, detail="Validación de expresión fallida")


    registrar_fichada(persona_id)

    return {"status": "ok", "mensaje": "Fichaje exitoso", "persona_id": persona_id}
