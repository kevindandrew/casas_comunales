from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.pago import Pago
from models.taller import Taller
from models.usuario import Usuario
from schemas.pago import PagoCreate, PagoUpdate, PagoRead
from security import get_current_user, require_admin

router = APIRouter(prefix="/pagos", tags=["Pagos"])


@router.get("", response_model=List[PagoRead])
def listar_pagos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    query = db.query(Pago)
    # Facilitador solo ve pagos de talleres en su casa comunal
    if current_user.rol.value == "Facilitador":
        talleres_casa = db.query(Taller.id).filter(
            Taller.casa_comunal_id == current_user.casa_comunal_id
        ).subquery()
        query = query.filter(Pago.taller_id.in_(talleres_casa))
    return query.offset(skip).limit(limit).all()


@router.post("", response_model=PagoRead, status_code=201)
def crear_pago(
    data: PagoCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    if data.metodo_pago not in {"efectivo", "transferencia"}:
        raise HTTPException(status_code=400, detail="metodo_pago debe ser 'efectivo' o 'transferencia'")
    pago = Pago(**data.model_dump())
    db.add(pago)
    db.commit()
    db.refresh(pago)
    return pago


@router.get("/{pago_id}", response_model=PagoRead)
def detalle_pago(pago_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return pago


@router.put("/{pago_id}", response_model=PagoRead)
def actualizar_pago(
    pago_id: int,
    data: PagoUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(pago, field, value)
    db.commit()
    db.refresh(pago)
    return pago
