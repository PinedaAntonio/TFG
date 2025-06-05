# En tu archivo main.py de FastAPI

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers import tournament_controller

app = FastAPI()

# Configurar CORS para permitir peticiones desde localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Permite solo las peticiones desde el frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite cualquier método (GET, POST, etc.)
    allow_headers=["*"],  # Permite cualquier cabecera
)

app.include_router(tournament_controller.router)
