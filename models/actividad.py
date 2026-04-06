from sqlalchemy import Column, Integer, String, Text, Boolean, Date, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from database import Base


class Actividad(Base):
    __tablename__ = "actividades"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha = Column(Date, nullable=False)
    es_global = Column(Boolean, default=False)
    facilitador_responsable_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    facilitador_responsable = relationship("Usuario", back_populates="actividades_responsable")
    actividad_casas = relationship("ActividadCasa", back_populates="actividad")
    asistencias = relationship("AsistenciaParticipante", back_populates="actividad")


class ActividadCasa(Base):
    __tablename__ = "actividad_casas"

    actividad_id = Column(Integer, ForeignKey("actividades.id"), nullable=False)
    casa_comunal_id = Column(Integer, ForeignKey("casas_comunales.id"), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("actividad_id", "casa_comunal_id"),)

    actividad = relationship("Actividad", back_populates="actividad_casas")
    casa_comunal = relationship("CasaComunal", back_populates="actividad_casas")
