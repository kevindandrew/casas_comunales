from sqlalchemy import Column, Integer, String, Numeric, Text
from sqlalchemy.orm import relationship
from database import Base


class CasaComunal(Base):
    __tablename__ = "casas_comunales"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(Text, nullable=False)
    macrodistrito = Column(String(50), nullable=False)
    representante_nombre = Column(String(150), nullable=True)
    representante_ci = Column(String(20), nullable=True)
    contacto_telefono = Column(String(20), nullable=True)
    latitud = Column(Numeric(9, 6), nullable=True)
    longitud = Column(Numeric(9, 6), nullable=True)

    usuarios = relationship("Usuario", back_populates="casa_comunal")
    participantes = relationship("Participante", back_populates="casa_comunal")
    talleres = relationship("Taller", back_populates="casa_comunal")
    horarios = relationship("Horario", back_populates="casa_comunal")
    actividad_casas = relationship("ActividadCasa", back_populates="casa_comunal")
