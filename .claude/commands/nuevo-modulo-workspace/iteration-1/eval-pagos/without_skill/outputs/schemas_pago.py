from pydantic import BaseModel
from datetime import date
from typing import Optional


class PagoBase(BaseModel):
    monto: float
    fecha_pago: date
    metodo_pago: str
    participante_id: int
    taller_id: int

    class Config:
        orm_mode = True


class PagoCreate(PagoBase):
    pass


class PagoRead(PagoBase):
    id: int
