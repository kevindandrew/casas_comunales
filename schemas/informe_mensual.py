from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional


class InformeCreate(BaseModel):
    facilitador_id: Optional[int] = None  # ignorado si el que crea es Facilitador
    mes: int
    anio: int
    carrera: str
    universidad: str
    definicion_actividades: str
    como_se_hicieron: str
    resultados_obtenidos: str
    relacion_alcaldia: str
    medios_trabajo: str

    @field_validator("mes")
    @classmethod
    def mes_valido(cls, v: int) -> int:
        if not 1 <= v <= 12:
            raise ValueError("El mes debe estar entre 1 y 12")
        return v

    @field_validator("anio")
    @classmethod
    def anio_valido(cls, v: int) -> int:
        if v < 2000 or v > 2100:
            raise ValueError("El año debe estar entre 2000 y 2100")
        return v


class InformeUpdate(BaseModel):
    mes: Optional[int] = None
    anio: Optional[int] = None
    carrera: Optional[str] = None
    universidad: Optional[str] = None
    definicion_actividades: Optional[str] = None
    como_se_hicieron: Optional[str] = None
    resultados_obtenidos: Optional[str] = None
    relacion_alcaldia: Optional[str] = None
    medios_trabajo: Optional[str] = None

    @field_validator("mes")
    @classmethod
    def mes_valido(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not 1 <= v <= 12:
            raise ValueError("El mes debe estar entre 1 y 12")
        return v

    @field_validator("anio")
    @classmethod
    def anio_valido(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 2000 or v > 2100):
            raise ValueError("El año debe estar entre 2000 y 2100")
        return v


class InformeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    facilitador_id: int
    mes: int
    anio: int
    carrera: str
    universidad: str
    definicion_actividades: str
    como_se_hicieron: str
    resultados_obtenidos: str
    relacion_alcaldia: str
    medios_trabajo: str
    creado_en: datetime
