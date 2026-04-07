from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional, List


# ─── Familia ──────────────────────────────────────────────────────────────────

class FamiliaCreate(BaseModel):
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    nombres: Optional[str] = None
    parentesco: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None


class FamiliaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    nombres: Optional[str] = None
    parentesco: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None


# ─── Datos Médicos ────────────────────────────────────────────────────────────

class DatosMedicosCreate(BaseModel):
    sistema_salud: Optional[str] = None
    enfermedad_base: Optional[str] = None
    tratamiento_especifico: Optional[str] = None


class DatosMedicosRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sistema_salud: Optional[str] = None
    enfermedad_base: Optional[str] = None
    tratamiento_especifico: Optional[str] = None


# ─── Participante ─────────────────────────────────────────────────────────────

class ParticipanteCreate(BaseModel):
    nombres: str
    apellidos: str
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    ci: str
    fecha_nacimiento: Optional[date] = None
    genero: Optional[str] = None         # M, F, O
    estado_civil: Optional[str] = None
    lugar_nacimiento: Optional[str] = None
    direccion: Optional[str] = None
    macrodistrito: Optional[str] = None
    telefono: Optional[str] = None
    contacto_emergencia: Optional[str] = None
    como_se_entero: Optional[str] = None
    grado_instruccion: Optional[str] = None
    ultimo_cargo: Optional[str] = None
    anios_servicio: Optional[int] = None
    casa_comunal_id: Optional[int] = None
    familia: List[FamiliaCreate] = []
    datos_medicos: List[DatosMedicosCreate] = []


class ParticipanteUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    genero: Optional[str] = None
    estado_civil: Optional[str] = None
    lugar_nacimiento: Optional[str] = None
    direccion: Optional[str] = None
    macrodistrito: Optional[str] = None
    telefono: Optional[str] = None
    contacto_emergencia: Optional[str] = None
    como_se_entero: Optional[str] = None
    grado_instruccion: Optional[str] = None
    ultimo_cargo: Optional[str] = None
    anios_servicio: Optional[int] = None
    casa_comunal_id: Optional[int] = None


class ParticipanteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombres: str
    apellidos: str
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    ci: str
    fecha_nacimiento: Optional[date] = None
    genero: Optional[str] = None
    estado_civil: Optional[str] = None
    lugar_nacimiento: Optional[str] = None
    direccion: Optional[str] = None
    macrodistrito: Optional[str] = None
    telefono: Optional[str] = None
    contacto_emergencia: Optional[str] = None
    como_se_entero: Optional[str] = None
    grado_instruccion: Optional[str] = None
    ultimo_cargo: Optional[str] = None
    anios_servicio: Optional[int] = None
    documento_ci_url: Optional[str] = None
    casa_comunal_id: Optional[int] = None
    created_at: datetime
    familia: List[FamiliaRead] = []
    datos_medicos: List[DatosMedicosRead] = []
