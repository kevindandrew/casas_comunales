from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from database import get_db
from models.participante import Participante
from models.asistencia import AsistenciaParticipante, Evaluacion
from models.taller import InscripcionTaller, Taller
from models.actividad import Actividad, ActividadCasa
from models.usuario import Usuario
from models.casa_comunal import CasaComunal
from security import get_current_user

router = APIRouter(prefix="/reportes", tags=["Reportes"])

PORCENTAJE_ASISTENCIA_MINIMO = 70.0


# ─── Dashboard ────────────────────────────────────────────────────────────────

@router.get("/estadisticas")
def estadisticas_dashboard(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    """Datos para el panel principal. Facilitador ve solo su casa."""
    es_facilitador = current_user.rol.value == "Facilitador"
    casa_id = current_user.casa_comunal_id if es_facilitador else None

    q_participantes = db.query(func.count(Participante.id))
    if casa_id:
        q_participantes = q_participantes.filter(Participante.casa_comunal_id == casa_id)
    total_participantes = q_participantes.scalar()

    total_casas = db.query(func.count(CasaComunal.id)).scalar()
    total_talleres = db.query(func.count(Taller.id)).filter(Taller.activo == True).scalar()

    por_genero = db.query(Participante.genero, func.count(Participante.id)).group_by(Participante.genero).all()
    genero_dict = {g or "No especificado": count for g, count in por_genero}

    por_macrodistrito = (
        db.query(CasaComunal.macrodistrito, func.count(Participante.id))
        .join(Participante, Participante.casa_comunal_id == CasaComunal.id, isouter=True)
        .group_by(CasaComunal.macrodistrito)
        .all()
    )

    return {
        "total_participantes": total_participantes,
        "total_casas_comunales": total_casas,
        "total_talleres_activos": total_talleres,
        "participantes_por_genero": genero_dict,
        "participantes_por_macrodistrito": [
            {"macrodistrito": m, "total": t} for m, t in por_macrodistrito
        ],
    }


# ─── Asistencia por participante ──────────────────────────────────────────────

@router.get("/asistencia-participante/{participante_id}")
def reporte_asistencia_participante(
    participante_id: int,
    taller_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Historial completo de asistencia de un participante, con porcentaje por taller."""
    participante = db.query(Participante).filter(Participante.id == participante_id).first()
    if not participante:
        raise HTTPException(status_code=404, detail="Participante no encontrado")

    # Talleres inscritos
    inscripciones = db.query(InscripcionTaller).filter(InscripcionTaller.participante_id == participante_id)
    if taller_id:
        inscripciones = inscripciones.filter(InscripcionTaller.taller_id == taller_id)
    inscripciones = inscripciones.all()

    detalle_talleres = []
    for ins in inscripciones:
        taller = db.query(Taller).filter(Taller.id == ins.taller_id).first()

        total_clases = db.query(func.count(AsistenciaParticipante.id)).filter(
            AsistenciaParticipante.taller_id == ins.taller_id
        ).scalar() or 0

        asistidas = db.query(func.count(AsistenciaParticipante.id)).filter(
            AsistenciaParticipante.taller_id == ins.taller_id,
            AsistenciaParticipante.participante_id == participante_id,
            AsistenciaParticipante.presente == True,
        ).scalar() or 0

        porcentaje = round((asistidas / total_clases * 100) if total_clases > 0 else 0, 1)

        detalle_talleres.append({
            "taller_id": ins.taller_id,
            "taller_nombre": taller.nombre if taller else None,
            "total_clases": total_clases,
            "clases_asistidas": asistidas,
            "porcentaje_asistencia": porcentaje,
            "cumple_minimo": porcentaje >= PORCENTAJE_ASISTENCIA_MINIMO,
        })

    return {
        "participante_id": participante_id,
        "nombre": f"{participante.nombres} {participante.apellidos}",
        "ci": participante.ci,
        "talleres": detalle_talleres,
    }


# ─── Asistencia general por casa ──────────────────────────────────────────────

@router.get("/asistencia-casa/{casa_id}")
def reporte_asistencia_casa(
    casa_id: int,
    taller_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Resumen de asistencia de todos los talleres de una casa comunal."""
    casa = db.query(CasaComunal).filter(CasaComunal.id == casa_id).first()
    if not casa:
        raise HTTPException(status_code=404, detail="Casa comunal no encontrada")

    talleres_q = db.query(Taller).filter(Taller.casa_comunal_id == casa_id, Taller.activo == True)
    if taller_id:
        talleres_q = talleres_q.filter(Taller.id == taller_id)
    talleres = talleres_q.all()

    resumen = []
    for t in talleres:
        inscritos = db.query(func.count(InscripcionTaller.id)).filter(InscripcionTaller.taller_id == t.id).scalar()

        total_registros = db.query(func.count(AsistenciaParticipante.id)).filter(
            AsistenciaParticipante.taller_id == t.id
        ).scalar() or 0

        presentes = db.query(func.count(AsistenciaParticipante.id)).filter(
            AsistenciaParticipante.taller_id == t.id,
            AsistenciaParticipante.presente == True,
        ).scalar() or 0

        porcentaje = round((presentes / total_registros * 100) if total_registros > 0 else 0, 1)

        resumen.append({
            "taller_id": t.id,
            "taller_nombre": t.nombre,
            "participantes_inscritos": inscritos,
            "total_registros_asistencia": total_registros,
            "total_presentes": presentes,
            "porcentaje_asistencia_general": porcentaje,
        })

    return {
        "casa_id": casa_id,
        "casa_nombre": casa.nombre,
        "macrodistrito": casa.macrodistrito,
        "talleres": resumen,
    }


# ─── Evaluaciones promedio por taller ────────────────────────────────────────

@router.get("/evaluaciones/{taller_id}")
def reporte_evaluaciones_taller(taller_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Promedio de notas y distribución de resultados del taller."""
    taller = db.query(Taller).filter(Taller.id == taller_id).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")

    evaluaciones = db.query(Evaluacion).filter(Evaluacion.taller_id == taller_id).all()
    if not evaluaciones:
        return {"taller": taller.nombre, "total_evaluaciones": 0, "promedio_nota_final": None}

    notas = [float(e.nota_final) for e in evaluaciones if e.nota_final is not None]
    aprobados = sum(1 for n in notas if n >= 51)

    return {
        "taller_id": taller_id,
        "taller_nombre": taller.nombre,
        "total_evaluaciones": len(evaluaciones),
        "promedio_nota_final": round(sum(notas) / len(notas), 2) if notas else None,
        "aprobados": aprobados,
        "reprobados": len(notas) - aprobados,
        "detalle": [
            {
                "participante_id": e.participante_id,
                "nota_1": float(e.nota_1) if e.nota_1 else None,
                "nota_2": float(e.nota_2) if e.nota_2 else None,
                "nota_final": float(e.nota_final) if e.nota_final else None,
            }
            for e in evaluaciones
        ],
    }


# ─── Participación en actividades ─────────────────────────────────────────────

@router.get("/actividades/{actividad_id}")
def reporte_actividad(actividad_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Reporte de asistencia de una actividad extracurricular."""
    actividad = db.query(Actividad).filter(Actividad.id == actividad_id).first()
    if not actividad:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")

    asistencias = db.query(AsistenciaParticipante).filter(
        AsistenciaParticipante.actividad_id == actividad_id
    ).all()

    total = len(asistencias)
    presentes = sum(1 for a in asistencias if a.presente)

    casas = db.query(ActividadCasa).filter(ActividadCasa.actividad_id == actividad_id).all()
    casa_ids = [c.casa_comunal_id for c in casas]

    return {
        "actividad_id": actividad_id,
        "actividad_nombre": actividad.nombre,
        "fecha": actividad.fecha,
        "es_global": actividad.es_global,
        "casas_participantes": casa_ids,
        "total_registros": total,
        "total_presentes": presentes,
        "porcentaje_asistencia": round((presentes / total * 100) if total > 0 else 0, 1),
    }


# ─── Certificados ─────────────────────────────────────────────────────────────

@router.get("/certificados/{participante_id}")
def verificar_certificado(
    participante_id: int,
    taller_id: int = Query(...),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    participante = db.query(Participante).filter(Participante.id == participante_id).first()
    if not participante:
        raise HTTPException(status_code=404, detail="Participante no encontrado")

    taller = db.query(Taller).filter(Taller.id == taller_id).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")

    inscripcion = db.query(InscripcionTaller).filter(
        InscripcionTaller.participante_id == participante_id,
        InscripcionTaller.taller_id == taller_id,
    ).first()
    if not inscripcion:
        return {"apto": False, "razon": "El participante no está inscrito en este taller"}

    total_clases = db.query(func.count(AsistenciaParticipante.id)).filter(
        AsistenciaParticipante.taller_id == taller_id
    ).scalar() or 0

    clases_asistidas = db.query(func.count(AsistenciaParticipante.id)).filter(
        AsistenciaParticipante.taller_id == taller_id,
        AsistenciaParticipante.participante_id == participante_id,
        AsistenciaParticipante.presente == True,
    ).scalar() or 0

    porcentaje_asistencia = (clases_asistidas / total_clases * 100) if total_clases > 0 else 0

    evaluacion = db.query(Evaluacion).filter(
        Evaluacion.participante_id == participante_id,
        Evaluacion.taller_id == taller_id,
    ).first()

    nota_final = float(evaluacion.nota_final) if evaluacion and evaluacion.nota_final else None
    aprobado_nota = nota_final is not None and nota_final >= 51

    apto = porcentaje_asistencia >= PORCENTAJE_ASISTENCIA_MINIMO and aprobado_nota

    return {
        "participante": f"{participante.nombres} {participante.apellidos}",
        "ci": participante.ci,
        "taller": taller.nombre,
        "asistencia": {
            "total_clases": total_clases,
            "clases_asistidas": clases_asistidas,
            "porcentaje": round(porcentaje_asistencia, 1),
            "cumple_minimo": porcentaje_asistencia >= PORCENTAJE_ASISTENCIA_MINIMO,
        },
        "evaluacion": {
            "nota_final": nota_final,
            "aprobado": aprobado_nota,
        },
        "apto_para_certificado": apto,
    }
