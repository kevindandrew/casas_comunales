from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from database import get_db
from models.informe_mensual import InformeMensual
from models.usuario import Usuario
from schemas.informe_mensual import InformeCreate, InformeUpdate, InformeRead
from security import get_current_user, require_admin

router = APIRouter(prefix="/informes", tags=["Informes Mensuales"])


@router.post("", response_model=InformeRead, status_code=201)
def crear_informe(
    data: InformeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un informe mensual. El facilitador crea para sí mismo; el admin debe indicar facilitador_id."""
    if current_user.rol.value == "Administrador":
        if not data.facilitador_id:
            raise HTTPException(status_code=400, detail="El administrador debe indicar facilitador_id")
        facilitador_id = data.facilitador_id
        facilitador = db.query(Usuario).filter(Usuario.id == facilitador_id).first()
        if not facilitador:
            raise HTTPException(status_code=404, detail="Facilitador no encontrado")
    else:
        facilitador_id = current_user.id

    duplicado = db.query(InformeMensual).filter(
        InformeMensual.facilitador_id == facilitador_id,
        InformeMensual.mes == data.mes,
        InformeMensual.anio == data.anio,
    ).first()
    if duplicado:
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe un informe para el mes {data.mes}/{data.anio} de este facilitador"
        )

    informe = InformeMensual(
        facilitador_id=facilitador_id,
        mes=data.mes,
        anio=data.anio,
        carrera=data.carrera,
        universidad=data.universidad,
        definicion_actividades=data.definicion_actividades,
        como_se_hicieron=data.como_se_hicieron,
        resultados_obtenidos=data.resultados_obtenidos,
        relacion_alcaldia=data.relacion_alcaldia,
        medios_trabajo=data.medios_trabajo,
    )
    db.add(informe)
    db.commit()
    db.refresh(informe)
    return informe


@router.get("", response_model=List[InformeRead])
def listar_informes(
    facilitador_id: Optional[int] = Query(None),
    mes: Optional[int] = Query(None),
    anio: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista informes. Facilitador ve solo los suyos; admin ve todos con filtros opcionales."""
    query = db.query(InformeMensual)
    if current_user.rol.value == "Facilitador":
        query = query.filter(InformeMensual.facilitador_id == current_user.id)
    else:
        if facilitador_id:
            query = query.filter(InformeMensual.facilitador_id == facilitador_id)
    if mes:
        query = query.filter(InformeMensual.mes == mes)
    if anio:
        query = query.filter(InformeMensual.anio == anio)
    return query.order_by(InformeMensual.anio.desc(), InformeMensual.mes.desc()).all()


@router.get("/{informe_id}", response_model=InformeRead)
def ver_informe(
    informe_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Ver detalle de un informe. Facilitador solo puede ver los suyos."""
    informe = db.query(InformeMensual).filter(InformeMensual.id == informe_id).first()
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    if current_user.rol.value == "Facilitador" and informe.facilitador_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este informe")
    return informe


@router.patch("/{informe_id}", response_model=InformeRead)
def editar_informe(
    informe_id: int,
    data: InformeUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Edita un informe. Facilitador solo edita los suyos; admin puede editar cualquiera."""
    informe = db.query(InformeMensual).filter(InformeMensual.id == informe_id).first()
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    if current_user.rol.value == "Facilitador" and informe.facilitador_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este informe")

    cambios = data.model_dump(exclude_none=True)
    for campo, valor in cambios.items():
        setattr(informe, campo, valor)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ya existe un informe para ese mes/año de este facilitador"
        )

    db.refresh(informe)
    return informe


@router.delete("/{informe_id}", status_code=204)
def eliminar_informe(
    informe_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Solo el facilitador dueño del informe puede eliminarlo. El admin no puede eliminar."""
    informe = db.query(InformeMensual).filter(InformeMensual.id == informe_id).first()
    if not informe:
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    if current_user.rol.value == "Administrador":
        raise HTTPException(status_code=403, detail="Los administradores no pueden eliminar informes")
    if informe.facilitador_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este informe")
    db.delete(informe)
    db.commit()
