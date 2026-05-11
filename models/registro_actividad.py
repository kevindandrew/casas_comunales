from sqlalchemy import Column, Integer, String, Text, Date, Time, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from database import Base
import enum


class TipoActividad(enum.Enum):
    taller = "Taller"
    material = "Elaboracion de Material"
    reunion = "Reunion"
    planificacion = "Planificacion"
    otro = "Otro"


class RegistroActividad(Base):
    __tablename__ = "registro_actividades"

    id = Column(Integer, primary_key=True, index=True)
    facilitador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=True)
    tipo_actividad = Column(SAEnum(TipoActividad), nullable=False)
    descripcion = Column(Text, nullable=False)
    casa_comunal_id = Column(Integer, ForeignKey("casas_comunales.id"), nullable=True)

    facilitador = relationship("Usuario", back_populates="registro_actividades")
    casa_comunal = relationship("CasaComunal", back_populates="registro_actividades")
