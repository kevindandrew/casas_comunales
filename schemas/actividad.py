from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional, List


class ActividadCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    fecha: date
    es_global: bool = False
    facilitador_responsable_id: Optional[int] = None
    gestion_id: Optional[int] = None
    casa_ids: List[int] = []  # Casas donde aplica (si no es global)


class ActividadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: Optional[str] = None
    fecha: date
    es_global: bool
    facilitador_responsable_id: Optional[int] = None
    gestion_id: Optional[int] = None


class AsistenciaActividadCreate(BaseModel):
    actividad_id: int
    participante_ids: List[int]  # IDs de participantes presentes
    fecha: date
