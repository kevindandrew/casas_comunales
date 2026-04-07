from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base
import models  # Registra todos los modelos con SQLAlchemy

from routers import (
    auth, usuarios, casas, horarios,
    talleres, participantes, control,
    facilitadores, actividades, reportes, gestiones,
)

app = FastAPI(
    title="Casas Comunales API",
    description="Sistema de gestión para casas comunales del municipio",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, reemplazar con el dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# Archivos estáticos (uploads)
import os
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(casas.router)
app.include_router(horarios.router)
app.include_router(talleres.router)
app.include_router(participantes.router)
app.include_router(control.router)
app.include_router(facilitadores.router)
app.include_router(actividades.router)
app.include_router(reportes.router)
app.include_router(gestiones.router)


@app.get("/", tags=["Root"])
def root():
    return {"mensaje": "Casas Comunales API funcionando", "docs": "/docs"}
