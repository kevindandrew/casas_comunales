from sqlalchemy import Column, Integer, Boolean, Date, Time, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from database import Base


class ControlFacilitador(Base):
    __tablename__ = "control_facilitadores"

    id = Column(Integer, primary_key=True, index=True)
    facilitador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha = Column(Date)
    hora_entrada = Column(Time, nullable=True)
    hora_salida = Column(Time, nullable=True)
    latitud_entrada = Column(Numeric(9, 6), nullable=True)
    longitud_entrada = Column(Numeric(9, 6), nullable=True)
    foto_entrada_url = Column(Text, nullable=True)
    foto_salida_url = Column(Text, nullable=True)
    validado = Column(Boolean, default=False)

    facilitador = relationship("Usuario", back_populates="control_asistencia")
