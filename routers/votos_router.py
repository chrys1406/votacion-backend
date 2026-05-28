from fastapi import APIRouter, HTTPException
from database import supabase
from pydantic import BaseModel

router = APIRouter(prefix="/votos", tags=["Votos"])

class VotoCreate(BaseModel):
    usuario_id: str
    candidato_id: str
    categoria_id: str
    eleccion_id: str

@router.post("/")
async def emitir_voto(body: VotoCreate):
    existente = supabase.table("votos").select("id").eq("usuario_id", body.usuario_id).eq("categoria_id", body.categoria_id).eq("eleccion_id", body.eleccion_id).execute()
    if existente.data:
        raise HTTPException(status_code=400, detail="Ya votaste en esta categoría")

    result = supabase.table("votos").insert({
        "usuario_id": body.usuario_id,
        "candidato_id": body.candidato_id,
        "categoria_id": body.categoria_id,
        "eleccion_id": body.eleccion_id,
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Error al registrar el voto")
    return {"mensaje": "Voto registrado correctamente"}

@router.get("/resultados/{eleccion_id}")
async def get_resultados(eleccion_id: str):
    result = supabase.table("votos").select("candidato_id, candidatos(nombre, foto_url), categoria_id, categorias(nombre)").eq("eleccion_id", eleccion_id).execute()

    conteo = {}
    for voto in result.data:
        cat_id = voto["categoria_id"]
        cat_nombre = voto["categorias"]["nombre"]
        cand_id = voto["candidato_id"]
        cand_nombre = voto["candidatos"]["nombre"]

        if cat_id not in conteo:
            conteo[cat_id] = {"categoria": cat_nombre, "candidatos": {}}

        if cand_id not in conteo[cat_id]["candidatos"]:
            conteo[cat_id]["candidatos"][cand_id] = {"nombre": cand_nombre, "votos": 0}

        conteo[cat_id]["candidatos"][cand_id]["votos"] += 1

    return list(conteo.values())

@router.get("/ha-votado/{usuario_id}/{eleccion_id}")
async def ha_votado(usuario_id: str, eleccion_id: str):
    result = supabase.table("votos").select("id").eq("usuario_id", usuario_id).eq("eleccion_id", eleccion_id).execute()
    return {"ha_votado": len(result.data) > 0}

@router.get("/total")
async def get_total_votos():
    result = supabase.table("votos").select("id").execute()
    return {"total": len(result.data)}



@router.get("/ha-votado-lista/{usuario_id}")
async def ha_votado_lista(usuario_id: str):
    result = supabase.table("votos").select("eleccion_id").eq("usuario_id", usuario_id).execute()
    elecciones_votadas = list(set([v["eleccion_id"] for v in result.data]))
    return {"elecciones_votadas": elecciones_votadas}