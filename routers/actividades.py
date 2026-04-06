from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from database import get_db
from models.actividad import Actividad, ActividadCasa
from models.asistencia import AsistenciaParticipante
from schemas.actividad import ActividadCreate, ActividadRead, AsistenciaActividadCreate
from security import get_current_user, require_admin

router = APIRouter(prefix="/actividades", tags=["Actividades"])


@router.get("", response_model=List[ActividadRead])
def listar_actividades(
    es_global: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = db.query(Actividad)
    if es_global is not None:
        query = query.filter(Actividad.es_global == es_global)
    return query.order_by(Actividad.fecha.desc()).all()


@router.post("", response_model=ActividadRead, status_code=201)
def crear_actividad(data: ActividadCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    actividad = Actividad(
        nombre=data.nombre,
        descripcion=data.descripcion,
        fecha=data.fecha,
        es_global=data.es_global,
        facilitador_responsable_id=data.facilitador_responsable_id,
    )
    db.add(actividad)
    db.flush()  # Para obtener el id antes del commit

    for casa_id in data.casa_ids:
        rel = ActividadCasa(actividad_id=actividad.id, casa_comunal_id=casa_id)
        db.add(rel)

    db.commit()
    db.refresh(actividad)
    return actividad


@router.post("/asistencia", status_code=201)
def registrar_asistencia_actividad(
    data: AsistenciaActividadCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    actividad = db.query(Actividad).filter(Actividad.id == data.actividad_id).first()
    if not actividad:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")

    creados = 0
    for pid in data.participante_ids:
        existente = db.query(AsistenciaParticipante).filter(
            AsistenciaParticipante.actividad_id == data.actividad_id,
            AsistenciaParticipante.participante_id == pid,
            AsistenciaParticipante.fecha == data.fecha,
        ).first()
        if existente:
            existente.presente = True
        else:
            db.add(AsistenciaParticipante(
                participante_id=pid,
                actividad_id=data.actividad_id,
                fecha=data.fecha,
                presente=True,
            ))
            creados += 1

    db.commit()
    return {"mensaje": f"Asistencia registrada. {creados} nuevos registros."}
