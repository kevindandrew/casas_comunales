from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import datetime
from typing import Optional


class UsuarioCreate(BaseModel):
    nombre_completo: str
    email: EmailStr
    password: str
    rol: str  # "Administrador" o "Facilitador"
    ci: str
    telefono: Optional[str] = None
    casa_comunal_id: Optional[int] = None


class UsuarioUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None
    casa_comunal_id: Optional[int] = None


class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre_completo: str
    email: str
    rol: str
    ci: str
    telefono: Optional[str] = None
    activo: bool
    created_at: datetime
    casa_comunal_id: Optional[int] = None

    @field_validator("rol", mode="before")
    @classmethod
    def extract_rol_value(cls, v):
        return v.value if hasattr(v, "value") else v
