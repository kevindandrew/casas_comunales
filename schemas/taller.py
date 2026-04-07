from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


class TallerCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    casa_comunal_id: Optional[int] = None
    facilitador_id: Optional[int] = None
    gestion_id: Optional[int] = None


class TallerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: Optional[str] = None
    casa_comunal_id: Optional[int] = None
    facilitador_id: Optional[int] = None
    gestion_id: Optional[int] = None
    activo: bool


class TallerUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    facilitador_id: Optional[int] = None
    gestion_id: Optional[int] = None


class InscripcionCreate(BaseModel):
    taller_id: int
    participante_id: int


class InscripcionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    taller_id: int
    participante_id: int
    fecha_inscripcion: Optional[date] = None
