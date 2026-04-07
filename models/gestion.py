from sqlalchemy import Column, Integer, Boolean, Date, String, UniqueConstraint, ForeignKey, CheckConstraint, Computed
from sqlalchemy.orm import relationship
from database import Base


class Gestion(Base):
    __tablename__ = "gestiones"

    id = Column(Integer, primary_key=True, index=True)
    anio = Column(Integer, nullable=False)
    trimestre = Column(Integer, nullable=False)
    nombre = Column(String(10), Computed("anio::text || '-'::text || trimestre::text", persisted=True))
    activo = Column(Boolean, default=False)
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)

    __table_args__ = (
        UniqueConstraint("anio", "trimestre", name="uq_gestion"),
        CheckConstraint("trimestre IN (1, 2, 3)", name="ck_trimestre"),
    )

    talleres = relationship("Taller", back_populates="gestion")
    horarios = relationship("Horario", back_populates="gestion")
    actividades = relationship("Actividad", back_populates="gestion")
    gestion_casas = relationship("GestionCasa", back_populates="gestion")


class GestionCasa(Base):
    __tablename__ = "gestion_casas"

    gestion_id = Column(Integer, ForeignKey("gestiones.id"), primary_key=True)
    casa_comunal_id = Column(Integer, ForeignKey("casas_comunales.id"), primary_key=True)

    gestion = relationship("Gestion", back_populates="gestion_casas")
    casa_comunal = relationship("CasaComunal", back_populates="gestion_casas")
