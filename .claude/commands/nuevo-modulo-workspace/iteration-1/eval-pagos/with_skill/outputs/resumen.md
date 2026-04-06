# Resumen — Módulo Pagos (WITH SKILL)

## Archivos creados
- `models/pago.py` — Modelo con ForeignKeys a participantes y talleres, nullable correcto
- `schemas/pago.py` — PagoCreate, PagoUpdate (campos Optional), PagoRead con ConfigDict
- `routers/pagos.py` — CRUD completo, filtro por casa_comunal para facilitadores

## Archivos a modificar

### `models/__init__.py`
```python
from models.pago import Pago
```

### `main.py`
```python
from routers import pagos
app.include_router(pagos.router)
```

## Endpoints disponibles
- GET    /pagos          — lista (facilitador filtrado por su casa)
- POST   /pagos          — crear (solo admin)
- GET    /pagos/{id}     — detalle
- PUT    /pagos/{id}     — editar (solo admin)

## Notas
- Se valida metodo_pago contra valores permitidos
- Facilitador filtra por talleres de su casa_comunal_id (subconsulta)
- ConfigDict(from_attributes=True) en PagoRead para serialización ORM correcta
