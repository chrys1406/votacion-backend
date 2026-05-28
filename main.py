from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth_router, elecciones_router, categorias_router, candidatos_router, estudiantes_router, votos_router

app = FastAPI(title="Sistema de Votación UPEA", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://tu-app.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(elecciones_router.router)
app.include_router(categorias_router.router)
app.include_router(candidatos_router.router)
app.include_router(estudiantes_router.router)
app.include_router(votos_router.router)

@app.get("/")
def root():
    return {"mensaje": "API Sistema de Votación UPEA corriendo ✅"}