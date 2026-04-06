from sqlalchemy import Column, Integer, Boolean, Date, ForeignKey, Text, Numeric, Computed
from sqlalchemy.orm import relationship
from database import Base


class AsistenciaParticipante(Base):
    __tablename__ = "asistencia_participantes"

    id = Column(Integer, primary_key=True, index=True)
    participante_id = Column(Integer, ForeignKey("participantes.id"), nullable=False)
    taller_id = Column(Integer, ForeignKey("talleres.id"), nullable=True)
    actividad_id = Column(Integer, ForeignKey("actividades.id"), nullable=True)
    fecha = Column(Date, nullable=False)
    presente = Column(Boolean, default=False)

    participante = relationship("Participante", back_populates="asistencias")
    taller = relationship("Taller", back_populates="asistencias")
    actividad = relationship("Actividad", back_populates="asistencias")


class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    id = Column(Integer, primary_key=True, index=True)
    participante_id = Column(Integer, ForeignKey("participantes.id"), nullable=False)
    taller_id = Column(Integer, ForeignKey("talleres.id"), nullable=False)
    nota_1 = Column(Numeric(5, 2), default=0)
    nota_2 = Column(Numeric(5, 2), default=0)
    nota_final = Column(Numeric(5, 2), Computed("(nota_1 + nota_2) / 2", persisted=True))
    observaciones = Column(Text, nullable=True)

    participante = relationship("Participante", back_populates="evaluaciones")
    taller = relationship("Taller", back_populates="evaluaciones")
