from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class Taller(Base):
    __tablename__ = "talleres"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    casa_comunal_id = Column(Integer, ForeignKey("casas_comunales.id"), nullable=True)
    facilitador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    gestion_id = Column(Integer, ForeignKey("gestiones.id"), nullable=True)
    activo = Column(Boolean, default=True)

    casa_comunal = relationship("CasaComunal", back_populates="talleres")
    facilitador = relationship("Usuario", back_populates="talleres_facilitados")
    gestion = relationship("Gestion", back_populates="talleres")
    inscripciones = relationship("InscripcionTaller", back_populates="taller")
    asistencias = relationship("AsistenciaParticipante", back_populates="taller")
    evaluaciones = relationship("Evaluacion", back_populates="taller")


class InscripcionTaller(Base):
    __tablename__ = "inscripciones_talleres"

    id = Column(Integer, primary_key=True, index=True)
    taller_id = Column(Integer, ForeignKey("talleres.id"), nullable=False)
    participante_id = Column(Integer, ForeignKey("participantes.id"), nullable=False)
    fecha_inscripcion = Column(Date, nullable=True)

    __table_args__ = (UniqueConstraint("taller_id", "participante_id", name="uq_inscripcion"),)

    taller = relationship("Taller", back_populates="inscripciones")
    participante = relationship("Participante", back_populates="inscripciones")
