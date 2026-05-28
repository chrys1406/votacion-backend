from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from database import supabase
from typing import Optional

router = APIRouter(prefix="/candidatos", tags=["Candidatos"])

@router.get("/")
async def get_candidatos():
    result = supabase.table("candidatos").select("*, categorias(nombre), elecciones(nombre)").execute()
    return result.data

@router.get("/eleccion/{eleccion_id}")
async def get_candidatos_por_eleccion(eleccion_id: str):
    result = supabase.table("candidatos").select("*, categorias(nombre)").eq("eleccion_id", eleccion_id).execute()
    return result.data

@router.post("/")
async def crear_candidato(
    nombre: str = Form(...),
    descripcion: str = Form(...),
    categoria_id: str = Form(...),
    eleccion_id: str = Form(...),
    enlace_propuestas: Optional[str] = Form(None),
    video_url: Optional[str] = Form(None),
    foto: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    partido: Optional[str] = Form(None),
):
    foto_url = None
    video_url_final = video_url

    if foto:
        foto_bytes = await foto.read()
        foto_path = f"{eleccion_id}/{nombre}/foto.jpg"
        try:
            supabase.storage.from_("fotos-candidatos").upload(
                foto_path, foto_bytes, {"content-type": foto.content_type}
            )
            foto_url = supabase.storage.from_("fotos-candidatos").get_public_url(foto_path)
        except Exception:
            pass

    if video:
        video_bytes = await video.read()
        video_path = f"{eleccion_id}/{nombre}/video.mp4"
        try:
            supabase.storage.from_("fotos-candidatos").upload(
                video_path, video_bytes, {"content-type": video.content_type}
            )
            video_url_final = supabase.storage.from_("fotos-candidatos").get_public_url(video_path)
        except Exception:
            pass

    # INSERT fuera del if video ← aquí estaba el bug
    result = supabase.table("candidatos").insert({
        "nombre": nombre,
        "descripcion": descripcion,
        "foto_url": foto_url,
        "video_url": video_url_final,
        "enlace_propuestas": enlace_propuestas,
        "categoria_id": categoria_id,
        "eleccion_id": eleccion_id,
        "partido": partido,
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear el candidato")
    return result.data[0]
@router.put("/{id}")
async def editar_candidato(
    id: str,
    nombre: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    categoria_id: Optional[str] = Form(None),
    eleccion_id: Optional[str] = Form(None),
    enlace_propuestas: Optional[str] = Form(None),
    video_url: Optional[str] = Form(None),
    foto: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    partido: Optional[str] = Form(None),
):
    data = {}
    if nombre: data["nombre"] = nombre
    if descripcion: data["descripcion"] = descripcion
    if categoria_id: data["categoria_id"] = categoria_id
    if eleccion_id: data["eleccion_id"] = eleccion_id
    if enlace_propuestas: data["enlace_propuestas"] = enlace_propuestas
    if video_url: data["video_url"] = video_url
    if partido: data["partido"] = partido

    if foto:
        foto_bytes = await foto.read()
        foto_path = f"{id}/foto.jpg"
        try:
            supabase.storage.from_("fotos-candidatos").upload(
                foto_path, foto_bytes, {"content-type": foto.content_type}
            )
            data["foto_url"] = supabase.storage.from_("fotos-candidatos").get_public_url(foto_path)
        except Exception:
            pass

    if video:
        video_bytes = await video.read()
        video_path = f"{id}/video.mp4"
        try:
            supabase.storage.from_("fotos-candidatos").upload(
                video_path, video_bytes, {"content-type": video.content_type}
            )
            data["video_url"] = supabase.storage.from_("fotos-candidatos").get_public_url(video_path)
        except Exception:
            pass

    result = supabase.table("candidatos").update(data).eq("id", id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Candidato no encontrado")
    return result.data[0]

@router.delete("/{id}")
async def eliminar_candidato(id: str):
    result = supabase.table("candidatos").delete().eq("id", id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Candidato no encontrado")
    return {"mensaje": "Candidato eliminado correctamente"}