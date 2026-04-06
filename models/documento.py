import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class EstadoDoc(enum.Enum):
    Pendiente = "Pendiente"
    Aprobado = "Aprobado"
    Observado = "Observado"


class DocumentoFacilitador(Base):
    __tablename__ = "documentos_facilitadores"

    id = Column(Integer, primary_key=True, index=True)
    facilitador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo_documento = Column(String(50), nullable=True)
    url_archivo = Column(Text, nullable=False)
    estado = Column(Enum(EstadoDoc, name="estado_doc", create_type=False), default=EstadoDoc.Pendiente)
    observaciones = Column(Text, nullable=True)
    fecha_subida = Column(DateTime, default=datetime.utcnow)

    facilitador = relationship("Usuario", back_populates="documentos")
