from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from database import supabase
from auth import hash_password, verify_password, create_token
from models import LoginRequest, TokenResponse
import json
import httpx
import uuid as uuid_lib
import base64

router = APIRouter(prefix="/auth", tags=["Auth"])

IA_URL = "https://christian1406-votacion-microservicio-ia.hf.space"


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    result = supabase.table("usuarios") \
        .select("*") \
        .eq("registro", body.registro) \
        .single() \
        .execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    usuario = result.data

    if not verify_password(body.cedula, usuario["cedula"]):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    token = create_token({
        "sub": usuario["id"],
        "registro": usuario["registro"],
        "rol": usuario["rol"],
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "rol": usuario["rol"],
        "nombre": usuario["nombre"],
        "usuario_id": usuario["id"],
    }


@router.post("/registro")
async def registro(
    nombre: str = Form(...),
    registro: str = Form(...),
    correo: str = Form(...),
    cedula: str = Form(...),
    embedding: str = Form(...),
    foto: UploadFile = File(...),
):
    # 1. Verificar que no exista ya
    existente = supabase.table("usuarios") \
        .select("id") \
        .or_(f"registro.eq.{registro},correo.eq.{correo},cedula.eq.{cedula}") \
        .execute()

    if existente.data:
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese registro, correo o cédula")

    # 2. Obtener todos los embeddings de la BD para comparación 1:N
    embeddings_bd = supabase.table("reconocimientos") \
        .select("usuario_id, embedding") \
        .execute()

    # 3. Si hay embeddings, comparar contra el nuevo para detectar duplicados
    if embeddings_bd.data:
        embedding_nuevo = json.loads(embedding)
        lista_embeddings = [
            {
                "usuario_id": r["usuario_id"],
                "embedding": r["embedding"]
            }
            for r in embeddings_bd.data
        ]

        async with httpx.AsyncClient() as client:
            ia_res = await client.post(
                f"{IA_URL}/compare-1vN-embedding",
                json={
                    "embedding_nuevo": embedding_nuevo,
                    "embeddings_bd": lista_embeddings,
                },
                timeout=30,
            )

        if ia_res.status_code == 200:
            ia_data = ia_res.json()
            if ia_data.get("duplicado"):
                raise HTTPException(
                    status_code=400,
                    detail="Este rostro ya está registrado en el sistema con otra cuenta"
                )

    # 4. Subir foto a Supabase Storage
    foto_bytes = await foto.read()
    foto_path = f"{registro}/foto.jpg"

    try:
        supabase.storage.from_("fotos-estudiantes").upload(
            foto_path,
            foto_bytes,
            {"content-type": foto.content_type}
        )
    except Exception:
        pass

    foto_url = supabase.storage.from_("fotos-estudiantes") \
        .get_public_url(foto_path)

    # 5. Hashear cédula y guardar usuario
    cedula_hash = hash_password(cedula)

    nuevo = supabase.table("usuarios").insert({
        "nombre": nombre,
        "registro": registro,
        "correo": correo,
        "cedula": cedula_hash,
        "rol": "estudiante",
        "foto_url": foto_url,
    }).execute()

    if not nuevo.data:
        raise HTTPException(status_code=500, detail="Error al crear el usuario")

    usuario_id = nuevo.data[0]["id"]

    # 6. Guardar embedding en BD
    embedding_parsed = json.loads(embedding)
    supabase.table("reconocimientos").insert({
        "usuario_id": usuario_id,
        "embedding": embedding_parsed,
    }).execute()

    return {
        "mensaje": "Usuario registrado correctamente",
        "usuario_id": usuario_id,
    }


@router.get("/me")
async def me(usuario_id: str):
    result = supabase.table("usuarios") \
        .select("id, nombre, registro, correo, rol") \
        .eq("id", usuario_id) \
        .single() \
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return result.data
@router.get("/embedding/{usuario_id}")
async def get_embedding(usuario_id: str):
    result = supabase.table("reconocimientos") \
        .select("embedding") \
        .eq("usuario_id", usuario_id) \
        .single() \
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="No se encontró registro facial")

    return {"embedding": result.data["embedding"]}