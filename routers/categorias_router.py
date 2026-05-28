from fastapi import APIRouter, HTTPException
from database import supabase
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/categorias", tags=["Categorías"])

class CategoriaCreate(BaseModel):
    nombre: str
    eleccion_id: str

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    eleccion_id: Optional[str] = None

@router.get("/")
async def get_categorias():
    result = supabase.table("categorias").select("*, elecciones(nombre)").execute()
    return result.data

@router.get("/eleccion/{eleccion_id}")
async def get_categorias_por_eleccion(eleccion_id: str):
    result = supabase.table("categorias").select("*").eq("eleccion_id", eleccion_id).execute()
    return result.data

@router.post("/")
async def crear_categoria(body: CategoriaCreate):
    result = supabase.table("categorias").insert({
        "nombre": body.nombre,
        "eleccion_id": body.eleccion_id,
    }).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear la categoría")
    return result.data[0]

@router.put("/{id}")
async def editar_categoria(id: str, body: CategoriaUpdate):
    data = {k: v for k, v in body.dict().items() if v is not None}
    result = supabase.table("categorias").update(data).eq("id", id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return result.data[0]

@router.delete("/{id}")
async def eliminar_categoria(id: str):
    result = supabase.table("categorias").delete().eq("id", id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return {"mensaje": "Categoría eliminada correctamente"}