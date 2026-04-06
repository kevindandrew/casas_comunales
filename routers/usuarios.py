from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.usuario import Usuario, UserRole
from schemas.usuario import UsuarioCreate, UsuarioRead, UsuarioUpdate
from security import get_current_user, require_admin, hash_password

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get("/me", response_model=UsuarioRead)
def get_me(current_user: Usuario = Depends(get_current_user)):
    return current_user


@router.get("", response_model=List[UsuarioRead])
def listar_usuarios(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(Usuario).all()


@router.post("", response_model=UsuarioRead, status_code=201)
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(Usuario).filter(Usuario.email == data.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    if db.query(Usuario).filter(Usuario.ci == data.ci).first():
        raise HTTPException(status_code=400, detail="La CI ya está registrada")

    try:
        rol_enum = UserRole(data.rol)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Rol inválido. Usa: {[r.value for r in UserRole]}")

    usuario = Usuario(
        nombre_completo=data.nombre_completo,
        email=data.email,
        password_hash=hash_password(data.password),
        rol=rol_enum,
        ci=data.ci,
        telefono=data.telefono,
        casa_comunal_id=data.casa_comunal_id,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.patch("/{user_id}/desactivar", response_model=UsuarioRead)
def desactivar_usuario(user_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.activo = False
    db.commit()
    db.refresh(usuario)
    return usuario


@router.put("/{user_id}", response_model=UsuarioRead)
def actualizar_usuario(user_id: int, data: UsuarioUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(usuario, field, value)
    db.commit()
    db.refresh(usuario)
    return usuario
