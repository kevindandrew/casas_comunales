from pydantic import BaseModel, ConfigDict
from datetime import time
from typing import Optional


class HorarioCreate(BaseModel):
    casa_comunal_id: Optional[int] = None
    facilitador_id: Optional[int] = None
    dia_semana: int  # 1=Lunes ... 5=Viernes
    hora_inicio: time
    hora_fin: time
    gestion_id: Optional[int] = None


class HorarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    casa_comunal_id: Optional[int] = None
    facilitador_id: Optional[int] = None
    dia_semana: int
    hora_inicio: time
    hora_fin: time
    gestion_id: Optional[int] = None


class HorarioGrilla(BaseModel):
    """Schema enriquecido para la vista de grilla semanal del frontend."""
    id: int
    dia_semana: int
    dia_nombre: str          # "Lunes", "Martes", etc.
    hora_inicio: time
    hora_fin: time
    casa_id: Optional[int] = None
    casa_nombre: Optional[str] = None
    macrodistrito: Optional[str] = None
    facilitador_id: Optional[int] = None
    facilitador_nombre: Optional[str] = None
