from sqlalchemy import Column, Integer, Numeric, Date, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    monto = Column(Numeric(10, 2), nullable=False)
    fecha_pago = Column(Date, nullable=False)
    metodo_pago = Column(String(20), nullable=False)  # "efectivo" | "transferencia"
    participante_id = Column(Integer, ForeignKey("participantes.id"), nullable=False)
    taller_id = Column(Integer, ForeignKey("talleres.id"), nullable=False)

    participante = relationship("Participante", backref="pagos")
    taller = relationship("Taller", backref="pagos")
