from pydantic import BaseModel, ConfigDict
from datetime import date
from decimal import Decimal
from typing import Optional


class PagoCreate(BaseModel):
    monto: Decimal
    fecha_pago: date
    metodo_pago: str  # "efectivo" | "transferencia"
    participante_id: int
    taller_id: int


class PagoUpdate(BaseModel):
    monto: Optional[Decimal] = None
    fecha_pago: Optional[date] = None
    metodo_pago: Optional[str] = None


class PagoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    monto: Decimal
    fecha_pago: date
    metodo_pago: str
    participante_id: int
    taller_id: int
