from sqlalchemy import Column, Integer, ForeignKey, Time, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base


class Horario(Base):
    __tablename__ = "horarios"

    id = Column(Integer, primary_key=True, index=True)
    casa_comunal_id = Column(Integer, ForeignKey("casas_comunales.id"), nullable=True)
    facilitador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    dia_semana = Column(Integer, nullable=False)  # 1=Lunes, 5=Viernes
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)

    __table_args__ = (CheckConstraint("dia_semana BETWEEN 1 AND 5", name="ck_dia_semana"),)

    casa_comunal = relationship("CasaComunal", back_populates="horarios")
    facilitador = relationship("Usuario", back_populates="horarios")
