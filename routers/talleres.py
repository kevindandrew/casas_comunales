from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.taller import Taller, InscripcionTaller
from models.participante import Participante
from models.usuario import Usuario
from schemas.taller import TallerCreate, TallerRead, TallerUpdate, InscripcionCreate, InscripcionRead
from schemas.participante import ParticipanteRead
from security import get_current_user, require_admin
from datetime import date

router = APIRouter(prefix="/talleres", tags=["Talleres"])


@router.get("", response_model=List[TallerRead])
def listar_talleres(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return db.query(Taller).filter(Taller.activo == True).all()


@router.post("", response_model=TallerRead, status_code=201)
def crear_taller(data: TallerCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    taller = Taller(**data.model_dump())
    db.add(taller)
    db.commit()
    db.refresh(taller)
    return taller


@router.get("/{taller_id}", response_model=TallerRead)
def detalle_taller(taller_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    taller = db.query(Taller).filter(Taller.id == taller_id).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    return taller


@router.put("/{taller_id}", response_model=TallerRead)
def actualizar_taller(taller_id: int, data: TallerUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    taller = db.query(Taller).filter(Taller.id == taller_id).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(taller, field, value)
    db.commit()
    db.refresh(taller)
    return taller


@router.patch("/{taller_id}/desactivar", response_model=TallerRead)
def desactivar_taller(taller_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    taller = db.query(Taller).filter(Taller.id == taller_id).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    taller.activo = False
    db.commit()
    db.refresh(taller)
    return taller


@router.get("/{taller_id}/participantes", response_model=List[ParticipanteRead])
def participantes_taller(taller_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    taller = db.query(Taller).filter(Taller.id == taller_id).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    inscripciones = db.query(InscripcionTaller).filter(InscripcionTaller.taller_id == taller_id).all()
    participante_ids = [i.participante_id for i in inscripciones]
    return db.query(Participante).filter(Participante.id.in_(participante_ids)).all()


@router.post("/inscribir", response_model=InscripcionRead, status_code=201)
def inscribir_participante(data: InscripcionCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    existente = db.query(InscripcionTaller).filter(
        InscripcionTaller.taller_id == data.taller_id,
        InscripcionTaller.participante_id == data.participante_id,
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="El participante ya está inscrito en este taller")

    inscripcion = InscripcionTaller(
        taller_id=data.taller_id,
        participante_id=data.participante_id,
        fecha_inscripcion=date.today(),
    )
    db.add(inscripcion)
    db.commit()
    db.refresh(inscripcion)
    return inscripcion


@router.delete("/inscribir/{inscripcion_id}", status_code=204)
def desinscribir_participante(inscripcion_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    inscripcion = db.query(InscripcionTaller).filter(InscripcionTaller.id == inscripcion_id).first()
    if not inscripcion:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    db.delete(inscripcion)
    db.commit()
