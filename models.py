from pydantic import BaseModel
from typing import Optional

class RegisterRequest(BaseModel):
    nombre: str
    registro: str
    correo: str
    cedula: str

class LoginRequest(BaseModel):
    registro: str
    cedula: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    nombre: str
    usuario_id: str