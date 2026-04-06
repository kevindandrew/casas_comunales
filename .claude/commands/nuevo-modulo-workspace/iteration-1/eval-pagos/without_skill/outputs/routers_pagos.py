from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.pago import Pago
from schemas.pago import PagoCreate, PagoRead
from security import get_current_user

router = APIRouter(prefix="/pagos", tags=["Pagos"])


@router.get("/", response_model=List[PagoRead])
def listar_pagos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Pago).all()


@router.post("/", response_model=PagoRead)
def crear_pago(data: PagoCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    pago = Pago(**data.dict())
    db.add(pago)
    db.commit()
    db.refresh(pago)
    return pago
