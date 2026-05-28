from database import supabase
from auth import hash_password

cedula_hash = hash_password("000")

# Primero verificar si ya existe
existente = supabase.table("usuarios").select("id").eq("registro", "ADMIN").execute()

if existente.data:
    # Actualizar
    supabase.table("usuarios").update({
        "cedula": cedula_hash
    }).eq("registro", "ADMIN").execute()
    print("Admin actualizado ✅")
else:
    # Insertar
    supabase.table("usuarios").insert({
        "nombre": "Administrador",
        "registro": "ADMIN",
        "correo": "admin@upea.bo",
        "cedula": cedula_hash,
        "rol": "admin",
    }).execute()
    print("Admin creado ✅")