# Resumen — Módulo Pagos (WITHOUT SKILL)

## Archivos creados
- `models/pago.py`
- `schemas/pago.py`  
- `routers/pagos.py`

## Para activar
Agregar en main.py:
```python
from routers.pagos import router as pagos_router
app.include_router(pagos_router)
```

## Endpoints
- GET /pagos/
- POST /pagos/
