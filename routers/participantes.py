from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.participante import Participante, FamiliaParticipante, DatosMedicosParticipante
from schemas.participante import (
    ParticipanteCreate, ParticipanteUpdate, ParticipanteRead,
    FamiliaCreate, FamiliaRead, DatosMedicosCreate, DatosMedicosRead,
)
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

    data_dict = data.model_dump(exclude={"familia", "datos_medicos"})
    participante = Participante(**data_dict)
    db.add(participante)
    db.flush()

    for f in data.familia:
        db.add(FamiliaParticipante(participante_id=participante.id, **f.model_dump()))

    for m in data.datos_medicos:
        db.add(DatosMedicosParticipante(participante_id=participante.id, **m.model_dump()))

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


# ─── Familia ──────────────────────────────────────────────────────────────────

@router.get("/{participante_id}/familia", response_model=List[FamiliaRead])
def listar_familia(participante_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(FamiliaParticipante).filter(FamiliaParticipante.participante_id == participante_id).all()


@router.post("/{participante_id}/familia", response_model=FamiliaRead, status_code=201)
def agregar_familiar(participante_id: int, data: FamiliaCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if not db.query(Participante).filter(Participante.id == participante_id).first():
        raise HTTPException(status_code=404, detail="Participante no encontrado")
    familiar = FamiliaParticipante(participante_id=participante_id, **data.model_dump())
    db.add(familiar)
    db.commit()
    db.refresh(familiar)
    return familiar


@router.delete("/{participante_id}/familia/{familiar_id}", status_code=204)
def eliminar_familiar(participante_id: int, familiar_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    familiar = db.query(FamiliaParticipante).filter(
        FamiliaParticipante.id == familiar_id,
        FamiliaParticipante.participante_id == participante_id,
    ).first()
    if not familiar:
        raise HTTPException(status_code=404, detail="Familiar no encontrado")
    db.delete(familiar)
    db.commit()


# ─── Datos Médicos ────────────────────────────────────────────────────────────

@router.get("/{participante_id}/datos-medicos", response_model=List[DatosMedicosRead])
def listar_datos_medicos(participante_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(DatosMedicosParticipante).filter(DatosMedicosParticipante.participante_id == participante_id).all()


@router.post("/{participante_id}/datos-medicos", response_model=DatosMedicosRead, status_code=201)
def agregar_datos_medicos(participante_id: int, data: DatosMedicosCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if not db.query(Participante).filter(Participante.id == participante_id).first():
        raise HTTPException(status_code=404, detail="Participante no encontrado")
    medico = DatosMedicosParticipante(participante_id=participante_id, **data.model_dump())
    db.add(medico)
    db.commit()
    db.refresh(medico)
    return medico


@router.delete("/{participante_id}/datos-medicos/{medico_id}", status_code=204)
def eliminar_datos_medicos(participante_id: int, medico_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    medico = db.query(DatosMedicosParticipante).filter(
        DatosMedicosParticipante.id == medico_id,
        DatosMedicosParticipante.participante_id == participante_id,
    ).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Registro médico no encontrado")
    db.delete(medico)
    db.commit()
