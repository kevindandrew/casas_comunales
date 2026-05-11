import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class UserRole(enum.Enum):
    Administrador = "Administrador"
    Facilitador = "Facilitador"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(150), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    rol = Column(Enum(UserRole, name="user_role", create_type=False), nullable=False)
    ci = Column(String(20), unique=True, nullable=False)
    telefono = Column(String(20), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    casa_comunal_id = Column(Integer, ForeignKey("casas_comunales.id"), nullable=True)

    casa_comunal = relationship("CasaComunal", back_populates="usuarios")
    horarios = relationship("Horario", back_populates="facilitador")
    control_asistencia = relationship("ControlFacilitador", back_populates="facilitador")
    documentos = relationship("DocumentoFacilitador", back_populates="facilitador")
    actividades_responsable = relationship("Actividad", back_populates="facilitador_responsable")
    registro_actividades = relationship("RegistroActividad", back_populates="facilitador")
