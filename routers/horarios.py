from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.horario import Horario
from models.casa_comunal import CasaComunal
from schemas.horario import HorarioGrilla
from security import get_current_user

router = APIRouter(prefix="/horarios", tags=["Horarios"])

DIAS = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes"}


@router.get("", response_model=List[HorarioGrilla])
def grilla_horarios(
    dia_semana: Optional[int] = Query(None, ge=1, le=5, description="1=Lunes, 5=Viernes"),
    macrodistrito: Optional[str] = Query(None),
    gestion_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Vista grilla semanal: devuelve TODOS los horarios con datos de casa y facilitador.
    Filtrable por día, macrodistrito y/o gestión.
    """
    query = (
        db.query(Horario)
        .join(CasaComunal, Horario.casa_comunal_id == CasaComunal.id, isouter=True)
    )

    if gestion_id is not None:
        query = query.filter(Horario.gestion_id == gestion_id)
    if dia_semana is not None:
        query = query.filter(Horario.dia_semana == dia_semana)
    if macrodistrito:
        query = query.filter(CasaComunal.macrodistrito.ilike(f"%{macrodistrito}%"))

    horarios = query.order_by(Horario.dia_semana, Horario.hora_inicio).all()

    return [
        HorarioGrilla(
            id=h.id,
            dia_semana=h.dia_semana,
            dia_nombre=DIAS.get(h.dia_semana, str(h.dia_semana)),
            hora_inicio=h.hora_inicio,
            hora_fin=h.hora_fin,
            casa_id=h.casa_comunal_id,
            casa_nombre=h.casa_comunal.nombre if h.casa_comunal else None,
            macrodistrito=h.casa_comunal.macrodistrito if h.casa_comunal else None,
            facilitador_id=h.facilitador_id,
            facilitador_nombre=h.facilitador.nombre_completo if h.facilitador else None,
            taller_id=h.taller_id,
            taller_nombre=h.taller.nombre if h.taller else None,
        )
        for h in horarios
    ]
