from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, DateTime, CHAR
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Participante(Base):
    __tablename__ = "participantes"

    id = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    ci = Column(String(20), unique=True, nullable=False, index=True)
    fecha_nacimiento = Column(Date, nullable=True)
    genero = Column(CHAR(1), nullable=True)  # M, F, O
    direccion = Column(Text, nullable=True)
    telefono = Column(String(20), nullable=True)
    contacto_emergencia = Column(String(150), nullable=True)
    documento_ci_url = Column(Text, nullable=True)
    casa_comunal_id = Column(Integer, ForeignKey("casas_comunales.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    casa_comunal = relationship("CasaComunal", back_populates="participantes")
    inscripciones = relationship("InscripcionTaller", back_populates="participante")
    asistencias = relationship("AsistenciaParticipante", back_populates="participante")
    evaluaciones = relationship("Evaluacion", back_populates="participante")
