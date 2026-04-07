from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.casa_comunal import CasaComunal
from models.gestion import GestionCasa
from models.horario import Horario
from schemas.casa_comunal import CasaComunalCreate, CasaComunalRead
from schemas.horario import HorarioCreate, HorarioRead
from security import get_current_user, require_admin

router = APIRouter(prefix="/casas", tags=["Casas Comunales"])


@router.get("", response_model=List[CasaComunalRead])
def listar_casas(
    macrodistrito: Optional[str] = Query(None),
    gestion_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = db.query(CasaComunal)
    if gestion_id:
        query = query.join(GestionCasa, GestionCasa.casa_comunal_id == CasaComunal.id)\
                     .filter(GestionCasa.gestion_id == gestion_id)
    if macrodistrito:
        query = query.filter(CasaComunal.macrodistrito.ilike(f"%{macrodistrito}%"))
    return query.all()


@router.post("", response_model=CasaComunalRead, status_code=201)
def crear_casa(data: CasaComunalCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    casa = CasaComunal(**data.model_dump())
    db.add(casa)
    db.commit()
    db.refresh(casa)
    return casa


@router.get("/{casa_id}", response_model=CasaComunalRead)
def detalle_casa(casa_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    casa = db.query(CasaComunal).filter(CasaComunal.id == casa_id).first()
    if not casa:
        raise HTTPException(status_code=404, detail="Casa comunal no encontrada")
    return casa


@router.put("/{casa_id}", response_model=CasaComunalRead)
def actualizar_casa(casa_id: int, data: CasaComunalCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    casa = db.query(CasaComunal).filter(CasaComunal.id == casa_id).first()
    if not casa:
        raise HTTPException(status_code=404, detail="Casa comunal no encontrada")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(casa, field, value)
    db.commit()
    db.refresh(casa)
    return casa


@router.get("/{casa_id}/horarios", response_model=List[HorarioRead])
def horarios_casa(casa_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Horario).filter(Horario.casa_comunal_id == casa_id).order_by(Horario.dia_semana, Horario.hora_inicio).all()


@router.post("/{casa_id}/horarios", response_model=HorarioRead, status_code=201)
def crear_horario(casa_id: int, data: HorarioCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    horario = Horario(**data.model_dump(), casa_comunal_id=casa_id)
    db.add(horario)
    db.commit()
    db.refresh(horario)
    return horario
