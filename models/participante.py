from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, DateTime, CHAR
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Participante(Base):
    __tablename__ = "participantes"

    id = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    apellido_paterno = Column(String(100), nullable=True)
    apellido_materno = Column(String(100), nullable=True)
    ci = Column(String(20), unique=True, nullable=False, index=True)
    fecha_nacimiento = Column(Date, nullable=True)
    genero = Column(CHAR(1), nullable=True)  # M, F, O
    estado_civil = Column(String(20), nullable=True)
    lugar_nacimiento = Column(String(100), nullable=True)
    direccion = Column(Text, nullable=True)
    macrodistrito = Column(String(50), nullable=True)
    telefono = Column(String(20), nullable=True)
    contacto_emergencia = Column(String(150), nullable=True)
    como_se_entero = Column(String(100), nullable=True)
    grado_instruccion = Column(String(50), nullable=True)
    ultimo_cargo = Column(String(100), nullable=True)
    anios_servicio = Column(Integer, nullable=True)
    documento_ci_url = Column(Text, nullable=True)
    casa_comunal_id = Column(Integer, ForeignKey("casas_comunales.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    casa_comunal = relationship("CasaComunal", back_populates="participantes")
    inscripciones = relationship("InscripcionTaller", back_populates="participante")
    asistencias = relationship("AsistenciaParticipante", back_populates="participante")
    evaluaciones = relationship("Evaluacion", back_populates="participante")
    familia = relationship("FamiliaParticipante", back_populates="participante", cascade="all, delete-orphan")
    datos_medicos = relationship("DatosMedicosParticipante", back_populates="participante", cascade="all, delete-orphan")


class FamiliaParticipante(Base):
    __tablename__ = "familia_participante"

    id = Column(Integer, primary_key=True, index=True)
    participante_id = Column(Integer, ForeignKey("participantes.id"), nullable=False)
    apellido_paterno = Column(String(100), nullable=True)
    apellido_materno = Column(String(100), nullable=True)
    nombres = Column(String(100), nullable=True)
    parentesco = Column(String(50), nullable=True)
    telefono = Column(String(20), nullable=True)
    direccion = Column(Text, nullable=True)

    participante = relationship("Participante", back_populates="familia")


class DatosMedicosParticipante(Base):
    __tablename__ = "datos_medicos_participante"

    id = Column(Integer, primary_key=True, index=True)
    participante_id = Column(Integer, ForeignKey("participantes.id"), nullable=False)
    sistema_salud = Column(String(50), nullable=True)
    enfermedad_base = Column(String(150), nullable=True)
    tratamiento_especifico = Column(Text, nullable=True)

    participante = relationship("Participante", back_populates="datos_medicos")
