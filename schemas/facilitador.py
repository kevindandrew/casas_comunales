from pydantic import BaseModel, ConfigDict, field_serializer
from datetime import date, time
from typing import Optional
from decimal import Decimal


class CheckInCreate(BaseModel):
    latitud: Decimal
    longitud: Decimal


class CheckOutCreate(BaseModel):
    control_id: int


class ControlFacilitadorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    facilitador_id: int
    fecha: Optional[date] = None
    hora_entrada: Optional[time] = None
    hora_salida: Optional[time] = None
    latitud_entrada: Optional[Decimal] = None
    longitud_entrada: Optional[Decimal] = None
    foto_entrada_url: Optional[str] = None
    foto_salida_url: Optional[str] = None
    validado: Optional[bool] = None

    @field_serializer("hora_entrada", "hora_salida")
    def _fmt_hora_utc(self, v: Optional[time]) -> Optional[str]:
        if v is None:
            return None
        return v.strftime("%H:%M:%S") + "Z"


class DocumentoCreate(BaseModel):
    tipo_documento: Optional[str] = None


class DocumentoEstadoUpdate(BaseModel):
    estado: str  # "Aprobado" o "Observado"
    observaciones: Optional[str] = None


class ValidarControlRequest(BaseModel):
    validado: bool
    observaciones: Optional[str] = None


class DocumentoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    facilitador_id: int
    tipo_documento: Optional[str] = None
    url_archivo: str
    estado: str
    observaciones: Optional[str] = None
