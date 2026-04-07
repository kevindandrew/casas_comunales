from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import date

from database import get_db
from models.gestion import Gestion, GestionCasa
from models.casa_comunal import CasaComunal
from security import get_current_user, require_admin

router = APIRouter(prefix="/gestiones", tags=["Gestiones"])


# ─── Schemas ──────────────────────────────────────────────────────────────────

class GestionCreate(BaseModel):
    anio: int
    trimestre: int
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None


class GestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    anio: int
    trimestre: int
    nombre: str
    activo: bool
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None


class GestionCasaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    direccion: str
    macrodistrito: str


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("", response_model=List[GestionRead])
def listar_gestiones(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Gestion).order_by(Gestion.anio.desc(), Gestion.trimestre.desc()).all()


@router.get("/activa", response_model=GestionRead)
def gestion_activa(db: Session = Depends(get_db), _=Depends(get_current_user)):
    gestion = db.query(Gestion).filter(Gestion.activo == True).first()
    if not gestion:
        raise HTTPException(status_code=404, detail="No hay ninguna gestión activa")
    return gestion


@router.get("/{gestion_id}", response_model=GestionRead)
def detalle_gestion(gestion_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    gestion = db.query(Gestion).filter(Gestion.id == gestion_id).first()
    if not gestion:
        raise HTTPException(status_code=404, detail="Gestión no encontrada")
    return gestion


@router.post("", response_model=GestionRead, status_code=201)
def crear_gestion(data: GestionCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if data.trimestre not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="El trimestre debe ser 1, 2 o 3")
    existe = db.query(Gestion).filter(Gestion.anio == data.anio, Gestion.trimestre == data.trimestre).first()
    if existe:
        raise HTTPException(status_code=400, detail=f"Ya existe la gestión {data.anio}-{data.trimestre}")
    gestion = Gestion(**data.model_dump())
    db.add(gestion)
    db.commit()
    db.refresh(gestion)
    return gestion


@router.patch("/{gestion_id}/activar", response_model=GestionRead)
def activar_gestion(gestion_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    """Activa una gestión y desactiva todas las demás."""
    gestion = db.query(Gestion).filter(Gestion.id == gestion_id).first()
    if not gestion:
        raise HTTPException(status_code=404, detail="Gestión no encontrada")
    db.query(Gestion).update({"activo": False})
    gestion.activo = True
    db.commit()
    db.refresh(gestion)
    return gestion


# ─── Casas por gestión ────────────────────────────────────────────────────────

@router.get("/{gestion_id}/casas", response_model=List[GestionCasaRead])
def casas_por_gestion(gestion_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Lista las casas comunales que participan en una gestión."""
    gestion = db.query(Gestion).filter(Gestion.id == gestion_id).first()
    if not gestion:
        raise HTTPException(status_code=404, detail="Gestión no encontrada")
    casas = (
        db.query(CasaComunal)
        .join(GestionCasa, GestionCasa.casa_comunal_id == CasaComunal.id)
        .filter(GestionCasa.gestion_id == gestion_id)
        .all()
    )
    return casas


@router.post("/{gestion_id}/casas/{casa_id}", status_code=201)
def agregar_casa_gestion(gestion_id: int, casa_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    """Agrega una casa comunal a una gestión."""
    if not db.query(Gestion).filter(Gestion.id == gestion_id).first():
        raise HTTPException(status_code=404, detail="Gestión no encontrada")
    if not db.query(CasaComunal).filter(CasaComunal.id == casa_id).first():
        raise HTTPException(status_code=404, detail="Casa comunal no encontrada")
    existe = db.query(GestionCasa).filter(GestionCasa.gestion_id == gestion_id, GestionCasa.casa_comunal_id == casa_id).first()
    if existe:
        raise HTTPException(status_code=400, detail="La casa ya está asignada a esta gestión")
    db.add(GestionCasa(gestion_id=gestion_id, casa_comunal_id=casa_id))
    db.commit()
    return {"mensaje": "Casa agregada a la gestión correctamente"}


@router.delete("/{gestion_id}/casas/{casa_id}")
def quitar_casa_gestion(gestion_id: int, casa_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    """Quita una casa comunal de una gestión."""
    registro = db.query(GestionCasa).filter(GestionCasa.gestion_id == gestion_id, GestionCasa.casa_comunal_id == casa_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="La casa no está asignada a esta gestión")
    db.delete(registro)
    db.commit()
    return {"mensaje": "Casa removida de la gestión correctamente"}
