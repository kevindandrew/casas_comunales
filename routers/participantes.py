from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.participante import Participante
from schemas.participante import ParticipanteCreate, ParticipanteUpdate, ParticipanteRead
from security import get_current_user
from cloudinary_config import subir_archivo

router = APIRouter(prefix="/participantes", tags=["Participantes"])


@router.get("", response_model=List[ParticipanteRead])
def listar_participantes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    nombre: Optional[str] = Query(None),
    casa_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = db.query(Participante)
    if nombre:
        query = query.filter(
            (Participante.nombres.ilike(f"%{nombre}%")) | (Participante.apellidos.ilike(f"%{nombre}%"))
        )
    if casa_id:
        query = query.filter(Participante.casa_comunal_id == casa_id)
    return query.offset(skip).limit(limit).all()


@router.get("/ci/{ci}", response_model=ParticipanteRead)
def buscar_por_ci(ci: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    participante = db.query(Participante).filter(Participante.ci == ci).first()
    if not participante:
        raise HTTPException(status_code=404, detail="Participante no encontrado")
    return participante


@router.get("/{participante_id}", response_model=ParticipanteRead)
def detalle_participante(participante_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    participante = db.query(Participante).filter(Participante.id == participante_id).first()
    if not participante:
        raise HTTPException(status_code=404, detail="Participante no encontrado")
    return participante


@router.post("", response_model=ParticipanteRead, status_code=201)
def crear_participante(data: ParticipanteCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if db.query(Participante).filter(Participante.ci == data.ci).first():
        raise HTTPException(status_code=400, detail="Ya existe un participante con esa CI")
    participante = Participante(**data.model_dump())
    db.add(participante)
    db.commit()
    db.refresh(participante)
    return participante


@router.put("/{participante_id}", response_model=ParticipanteRead)
def actualizar_participante(
    participante_id: int,
    data: ParticipanteUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    participante = db.query(Participante).filter(Participante.id == participante_id).first()
    if not participante:
        raise HTTPException(status_code=404, detail="Participante no encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(participante, field, value)
    db.commit()
    db.refresh(participante)
    return participante


@router.post("/{participante_id}/documento-ci", response_model=ParticipanteRead)
def subir_documento_ci(
    participante_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    participante = db.query(Participante).filter(Participante.id == participante_id).first()
    if not participante:
        raise HTTPException(status_code=404, detail="Participante no encontrado")

    url = subir_archivo(archivo.file, carpeta="casas_comunales/documentos_ci", public_id=f"ci_{participante_id}")

    participante.documento_ci_url = url
    db.commit()
    db.refresh(participante)
    return participante
