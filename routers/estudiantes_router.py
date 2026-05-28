from fastapi import APIRouter, HTTPException
from database import supabase

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])

@router.get("/")
async def get_estudiantes():
    result = supabase.table("usuarios").select("id, nombre, registro, correo, created_at").eq("rol", "estudiante").execute()
    return result.data

@router.get("/buscar")
async def buscar_estudiante(q: str):
    result = supabase.table("usuarios").select("id, nombre, registro, correo").eq("rol", "estudiante").or_(
        f"nombre.ilike.%{q}%,registro.ilike.%{q}%"
    ).execute()
    return result.data

@router.delete("/{id}")
async def eliminar_estudiante(id: str):
    result = supabase.table("usuarios").delete().eq("id", id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return {"mensaje": "Estudiante eliminado correctamente"}