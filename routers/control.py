from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from database import get_db
from models.asistencia import AsistenciaParticipante, Evaluacion
from schemas.asistencia import AsistenciaCreate, AsistenciaRead, EvaluacionUpdate, EvaluacionRead
from security import get_current_user

router = APIRouter(prefix="/control", tags=["Asistencia y Evaluaciones"])


@router.post("/asistencia", status_code=201)
def registrar_asistencia(data: AsistenciaCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    creados = 0
    for registro in data.registros:
        existente = db.query(AsistenciaParticipante).filter(
            AsistenciaParticipante.taller_id == data.taller_id,
            AsistenciaParticipante.participante_id == registro.participante_id,
            AsistenciaParticipante.fecha == data.fecha,
        ).first()
        if existente:
            existente.presente = registro.presente
        else:
            db.add(AsistenciaParticipante(
                participante_id=registro.participante_id,
                taller_id=data.taller_id,
                fecha=data.fecha,
                presente=registro.presente,
            ))
            creados += 1
    db.commit()
    return {"mensaje": f"Asistencia registrada. {creados} nuevos registros."}


@router.get("/asistencia/{taller_id}", response_model=List[AsistenciaRead])
def historial_asistencia(
    taller_id: int,
    fecha: Optional[date] = Query(None, description="Filtrar por fecha específica"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = db.query(AsistenciaParticipante).filter(AsistenciaParticipante.taller_id == taller_id)
    if fecha:
        query = query.filter(AsistenciaParticipante.fecha == fecha)
    return query.order_by(AsistenciaParticipante.fecha).all()


@router.put("/evaluaciones", response_model=EvaluacionRead)
def cargar_evaluacion(data: EvaluacionUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    evaluacion = db.query(Evaluacion).filter(
        Evaluacion.participante_id == data.participante_id,
        Evaluacion.taller_id == data.taller_id,
    ).first()

    if not evaluacion:
        evaluacion = Evaluacion(
            participante_id=data.participante_id,
            taller_id=data.taller_id,
        )
        db.add(evaluacion)

    if data.nota_1 is not None:
        evaluacion.nota_1 = data.nota_1
    if data.nota_2 is not None:
        evaluacion.nota_2 = data.nota_2
    if data.observaciones is not None:
        evaluacion.observaciones = data.observaciones

    db.commit()
    db.refresh(evaluacion)
    return evaluacion


@router.get("/evaluaciones/taller/{taller_id}", response_model=List[EvaluacionRead])
def evaluaciones_por_taller(taller_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Lista todas las evaluaciones de un taller (para ver notas de todos los participantes)."""
    return db.query(Evaluacion).filter(Evaluacion.taller_id == taller_id).all()


@router.get("/evaluaciones/participante/{participante_id}", response_model=List[EvaluacionRead])
def evaluaciones_por_participante(participante_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Lista todas las evaluaciones de un participante en todos sus talleres."""
    return db.query(Evaluacion).filter(Evaluacion.participante_id == participante_id).all()
