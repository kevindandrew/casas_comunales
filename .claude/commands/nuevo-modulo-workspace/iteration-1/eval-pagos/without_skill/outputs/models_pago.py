from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base


class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True)
    monto = Column(Float)
    fecha_pago = Column(Date)
    metodo_pago = Column(String)
    participante_id = Column(Integer, ForeignKey("participantes.id"))
    taller_id = Column(Integer, ForeignKey("talleres.id"))
