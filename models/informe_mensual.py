from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class InformeMensual(Base):
    __tablename__ = "informes_mensuales"

    id = Column(Integer, primary_key=True, index=True)
    facilitador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    mes = Column(Integer, nullable=False)
    anio = Column(Integer, nullable=False)
    carrera = Column(String(200), nullable=False)
    universidad = Column(String(200), nullable=False)
    definicion_actividades = Column(Text, nullable=False)
    como_se_hicieron = Column(Text, nullable=False)
    resultados_obtenidos = Column(Text, nullable=False)
    relacion_alcaldia = Column(Text, nullable=False)
    medios_trabajo = Column(Text, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("facilitador_id", "mes", "anio", name="uq_informe_facilitador_mes_anio"),
    )

    facilitador = relationship("Usuario", back_populates="informes_mensuales")
