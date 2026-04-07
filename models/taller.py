from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class Taller(Base):
    __tablename__ = "talleres"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)

    horarios = relationship("Horario", back_populates="taller")
    inscripciones = relationship("InscripcionTaller", back_populates="taller")
    asistencias = relationship("AsistenciaParticipante", back_populates="taller")
    evaluaciones = relationship("Evaluacion", back_populates="taller")
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
