import math
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.control_facilitador import ControlFacilitador
from models.documento import DocumentoFacilitador, EstadoDoc
from models.casa_comunal import CasaComunal
from models.horario import Horario
from models.usuario import Usuario
from schemas.facilitador import (
    CheckInCreate, CheckOutCreate, ControlFacilitadorRead,
    DocumentoEstadoUpdate, DocumentoRead, ValidarControlRequest,
)
from security import get_current_user, require_admin

router = APIRouter(prefix="/facilitadores", tags=["Facilitadores"])

from cloudinary_config import subir_archivo

RADIO_PERMITIDO_METROS = 100


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia en metros entre dos coordenadas GPS."""
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@router.post("/check-in")
def check_in(
    latitud: float = Form(...),
    longitud: float = Form(...),
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if not current_user.casa_comunal_id:
        raise HTTPException(status_code=400, detail="El facilitador no tiene una casa comunal asignada")

    casa = db.query(CasaComunal).filter(CasaComunal.id == current_user.casa_comunal_id).first()
    if not casa or casa.latitud is None or casa.longitud is None:
        raise HTTPException(status_code=400, detail="La casa comunal no tiene coordenadas GPS registradas")

    # Validar proximidad GPS
    distancia = _haversine(latitud, longitud, float(casa.latitud), float(casa.longitud))
    if distancia > RADIO_PERMITIDO_METROS:
        raise HTTPException(
            status_code=400,
            detail=f"Estás a {distancia:.0f}m de la casa comunal. Máximo permitido: {RADIO_PERMITIDO_METROS}m"
        )

    # Validar coincidencia con horario del día (1=Lunes ... 5=Viernes, Python: 0=Lunes)
    dia_hoy = datetime.today().weekday() + 1  # Convertir a 1-5
    tiene_horario_hoy = db.query(Horario).filter(
        Horario.facilitador_id == current_user.id,
        Horario.casa_comunal_id == current_user.casa_comunal_id,
        Horario.dia_semana == dia_hoy,
    ).first()
    # Si no tiene horario hoy, se registra pero queda como no validado (no bloquea el flujo)
    validado_auto = tiene_horario_hoy is not None

    # Guardar foto en Cloudinary
    foto_url = subir_archivo(foto.file, carpeta="casas_comunales/fotos_checkin", public_id=f"entrada_{current_user.id}_{date.today()}")

    control = ControlFacilitador(
        facilitador_id=current_user.id,
        fecha=date.today(),
        hora_entrada=datetime.now().time(),
        latitud_entrada=latitud,
        longitud_entrada=longitud,
        foto_entrada_url=foto_url,
        validado=validado_auto,
    )
    db.add(control)
    db.commit()
    db.refresh(control)

    mensaje = f"Check-in registrado. Distancia: {distancia:.0f}m."
    if not validado_auto:
        mensaje += " AVISO: No tienes horario asignado para hoy. Pendiente de validación por administrador."

    return {
        "status": "success" if validado_auto else "pendiente",
        "mensaje": mensaje,
        "control_id": control.id,
        "validado": validado_auto,
    }


@router.post("/check-out")
def check_out(
    control_id: int = Form(...),
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    control = db.query(ControlFacilitador).filter(
        ControlFacilitador.id == control_id,
        ControlFacilitador.facilitador_id == current_user.id,
    ).first()
    if not control:
        raise HTTPException(status_code=404, detail="Registro de check-in no encontrado")
    if control.hora_salida:
        raise HTTPException(status_code=400, detail="Ya se registró el check-out para este turno")

    foto_url = subir_archivo(foto.file, carpeta="casas_comunales/fotos_checkin", public_id=f"salida_{current_user.id}_{date.today()}")

    control.hora_salida = datetime.now().time()
    control.foto_salida_url = foto_url
    db.commit()
    return {"status": "success", "mensaje": "Check-out registrado correctamente"}


# ─── Control Admin ────────────────────────────────────────────────────────────

@router.get("/control", response_model=List[ControlFacilitadorRead])
def listar_controles(
    facilitador_id: Optional[int] = Query(None),
    fecha: Optional[date] = Query(None),
    validado: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista registros de check-in/check-out. Admin ve todos; facilitador solo los suyos."""
    query = db.query(ControlFacilitador)
    if current_user.rol.value == "Facilitador":
        query = query.filter(ControlFacilitador.facilitador_id == current_user.id)
    else:
        if facilitador_id:
            query = query.filter(ControlFacilitador.facilitador_id == facilitador_id)
    if fecha:
        query = query.filter(ControlFacilitador.fecha == fecha)
    if validado is not None:
        query = query.filter(ControlFacilitador.validado == validado)
    return query.order_by(ControlFacilitador.fecha.desc()).all()


@router.patch("/control/{control_id}/validar", response_model=ControlFacilitadorRead)
def validar_control(
    control_id: int,
    data: ValidarControlRequest,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Admin valida o rechaza manualmente un registro de asistencia de facilitador."""
    control = db.query(ControlFacilitador).filter(ControlFacilitador.id == control_id).first()
    if not control:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    control.validado = data.validado
    db.commit()
    db.refresh(control)
    return control


# ─── Documentos ───────────────────────────────────────────────────────────────

@router.get("/documentos", response_model=List[DocumentoRead])
def listar_documentos(
    facilitador_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    query = db.query(DocumentoFacilitador)
    if current_user.rol.value == "Facilitador":
        query = query.filter(DocumentoFacilitador.facilitador_id == current_user.id)
    elif facilitador_id:
        query = query.filter(DocumentoFacilitador.facilitador_id == facilitador_id)
    return query.all()


@router.post("/documentos", response_model=DocumentoRead, status_code=201)
def subir_documento(
    tipo_documento: str,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    url = subir_archivo(archivo.file, carpeta="casas_comunales/documentos_facilitadores", public_id=f"{current_user.id}_{tipo_documento}")

    doc = DocumentoFacilitador(
        facilitador_id=current_user.id,
        tipo_documento=tipo_documento,
        url_archivo=url,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.patch("/documentos/{doc_id}", response_model=DocumentoRead)
def actualizar_estado_documento(
    doc_id: int,
    data: DocumentoEstadoUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    doc = db.query(DocumentoFacilitador).filter(DocumentoFacilitador.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    try:
        doc.estado = EstadoDoc(data.estado)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Usa: {[e.value for e in EstadoDoc]}")

    if data.observaciones is not None:
        doc.observaciones = data.observaciones

    db.commit()
    db.refresh(doc)
    return doc
