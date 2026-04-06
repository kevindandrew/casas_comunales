from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional


class ParticipanteCreate(BaseModel):
    nombres: str
    apellidos: str
    ci: str
    fecha_nacimiento: Optional[date] = None
    genero: Optional[str] = None  # M, F, O
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    contacto_emergencia: Optional[str] = None
    casa_comunal_id: Optional[int] = None


class ParticipanteUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    genero: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    contacto_emergencia: Optional[str] = None
    casa_comunal_id: Optional[int] = None


class ParticipanteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombres: str
    apellidos: str
    ci: str
    fecha_nacimiento: Optional[date] = None
    genero: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    contacto_emergencia: Optional[str] = None
    documento_ci_url: Optional[str] = None
    casa_comunal_id: Optional[int] = None
    created_at: datetime
