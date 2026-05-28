from fastapi import APIRouter, HTTPException
from database import supabase
from pydantic import BaseModel
from typing import Optional
from datetime import date

router = APIRouter(prefix="/elecciones", tags=["Elecciones"])

class EleccionCreate(BaseModel):
    nombre: str
    facultad: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    activa: Optional[bool] = False

class EleccionUpdate(BaseModel):
    nombre: Optional[str] = None
    facultad: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    activa: Optional[bool] = None

@router.get("/")
async def get_elecciones():
    result = supabase.table("elecciones").select("*").order("created_at", desc=True).execute()
    return result.data

@router.get("/{id}")
async def get_eleccion(id: str):
    result = supabase.table("elecciones").select("*").eq("id", id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Elección no encontrada")
    return result.data

@router.post("/")
async def crear_eleccion(body: EleccionCreate):
    activas = supabase.table("elecciones").select("id").eq("activa", True).execute()
    if len(activas.data) >= 5:
        raise HTTPException(status_code=400, detail="No puede haber más de 5 elecciones activas")

    result = supabase.table("elecciones").insert({
        "nombre": body.nombre,
        "facultad": body.facultad,
        "fecha_inicio": str(body.fecha_inicio) if body.fecha_inicio else None,
        "fecha_fin": str(body.fecha_fin) if body.fecha_fin else None,
        "activa": body.activa,
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear la elección")
    return result.data[0]

@router.put("/{id}")
async def editar_eleccion(id: str, body: EleccionUpdate):
    data = {k: v for k, v in body.dict().items() if v is not None}
    if "fecha_inicio" in data:
        data["fecha_inicio"] = str(data["fecha_inicio"])
    if "fecha_fin" in data:
        data["fecha_fin"] = str(data["fecha_fin"])

    result = supabase.table("elecciones").update(data).eq("id", id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Elección no encontrada")
    return result.data[0]

@router.patch("/{id}/toggle")
async def toggle_eleccion(id: str):
    eleccion = supabase.table("elecciones").select("activa").eq("id", id).single().execute()
    if not eleccion.data:
        raise HTTPException(status_code=404, detail="Elección no encontrada")

    nueva_activa = not eleccion.data["activa"]

    if nueva_activa:
        activas = supabase.table("elecciones").select("id").eq("activa", True).execute()
        if len(activas.data) >= 5:
            raise HTTPException(status_code=400, detail="No puede haber más de 5 elecciones activas")

    result = supabase.table("elecciones").update({"activa": nueva_activa}).eq("id", id).execute()
    return result.data[0]

@router.delete("/{id}")
async def eliminar_eleccion(id: str):
    result = supabase.table("elecciones").delete().eq("id", id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Elección no encontrada")
    return {"mensaje": "Elección eliminada correctamente"}