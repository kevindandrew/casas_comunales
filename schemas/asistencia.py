from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional, List
from decimal import Decimal


class RegistroAsistencia(BaseModel):
    participante_id: int
    presente: bool


class AsistenciaCreate(BaseModel):
    taller_id: int
    fecha: date
    registros: List[RegistroAsistencia]


class AsistenciaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    participante_id: int
    taller_id: Optional[int] = None
    actividad_id: Optional[int] = None
    fecha: date
    presente: bool


class EvaluacionUpdate(BaseModel):
    participante_id: int
    taller_id: int
    nota_1: Optional[Decimal] = None
    nota_2: Optional[Decimal] = None
    observaciones: Optional[str] = None


class EvaluacionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    participante_id: int
    taller_id: int
    nota_1: Optional[Decimal] = None
    nota_2: Optional[Decimal] = None
    nota_final: Optional[Decimal] = None
    observaciones: Optional[str] = None
