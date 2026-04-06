from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal


class CasaComunalCreate(BaseModel):
    nombre: str
    direccion: str
    macrodistrito: str
    representante_nombre: Optional[str] = None
    representante_ci: Optional[str] = None
    contacto_telefono: Optional[str] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None


class CasaComunalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    direccion: str
    macrodistrito: str
    representante_nombre: Optional[str] = None
    representante_ci: Optional[str] = None
    contacto_telefono: Optional[str] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
