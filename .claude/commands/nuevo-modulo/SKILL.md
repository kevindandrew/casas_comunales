---
name: nuevo-modulo
description: Crea un módulo API completo para el proyecto FastAPI de Casas Comunales — incluyendo modelo SQLAlchemy, schema Pydantic, router con endpoints y el registro en main.py. Úsalo cuando el usuario quiera agregar cualquier nueva entidad, tabla o funcionalidad a la API: "quiero agregar pagos", "necesito registrar eventos", "agrega un módulo de inventario", "crea una tabla de sugerencias", "necesito endpoints para X". Si el usuario describe algo que suena a una nueva entidad de datos o un nuevo grupo de endpoints, este skill es el indicado.
---

# Nuevo Módulo API — Casas Comunales

El proyecto está en `c:\Users\KEVIN\Desktop\casas comunales`.

La idea es que con la información del usuario puedas generar código que encaje perfectamente en el estilo del proyecto existente, sin que el usuario tenga que preocuparse por los patrones técnicos.

## Paso 1 — Entender qué necesita el usuario

Pregunta todo en un solo mensaje para no ir y venir:

> ¿Cómo se llama el módulo? (ej: "pagos", "eventos")
> ¿Qué campos tiene? (nombre del campo, tipo: texto/número/fecha/sí-no/decimal, ¿es obligatorio?)
> ¿Se relaciona con algo existente? (participantes, casas comunales, talleres, usuarios)
> ¿Qué operaciones necesita? (ver lista, ver detalle, crear, editar, desactivar)
> ¿Quién puede usarlo? (solo el administrador / el facilitador también / ambos)

Si el usuario ya dio esa información en su mensaje, úsala directamente y no preguntes de nuevo.

## Paso 2 — Crear `models/<nombre>.py`

Antes de escribir el modelo, revisa un modelo existente (ej: `models/participante.py`) para seguir exactamente el mismo estilo.

Reglas importantes del proyecto:
- Heredar de `Base` (importado de `database`)
- Campos opcionales siempre con `nullable=True` — si no está, PostgreSQL puede rechazar INSERTs
- ForeignKeys a otras tablas con `nullable=True` si la relación no es obligatoria
- Si el módulo tiene estados o categorías fijas, usar Python `enum.Enum` con `create_type=False` porque el tipo ya existe en PostgreSQL
- Agregar `relationship()` con `back_populates` para mantener consistencia con el modelo relacionado

## Paso 3 — Crear `schemas/<nombre>.py`

Siempre tres clases:
- `<Nombre>Create` — lo que el usuario envía al crear (sin id, sin timestamps)
- `<Nombre>Update` — todos los campos opcionales con `Optional[...]` para ediciones parciales
- `<Nombre>Read` — la respuesta completa, con `model_config = ConfigDict(from_attributes=True)` para que Pydantic entienda objetos SQLAlchemy

## Paso 4 — Crear `routers/<nombre>.py`

```python
router = APIRouter(prefix="/<nombres>", tags=["<Nombre>"])
```

Por cada operación solicitada:
- **Listar** → paginación con `skip`/`limit`, filtros útiles como `casa_id` o `activo`
- **Detalle** → 404 claro si no existe
- **Crear** → validar unicidad si hay campos únicos (email, CI, etc.)
- **Editar** → `model_dump(exclude_none=True)` para no pisar campos que no se enviaron
- **Desactivar** → nunca DELETE real, solo `activo = False`

Control de acceso (importar de `security.py`):
- Solo admin → `Depends(require_admin)`
- Cualquier usuario autenticado → `Depends(get_current_user)`
- Facilitador ve solo su casa → filtrar con `if current_user.rol.value == "Facilitador": query = query.filter(...casa_comunal_id == current_user.casa_comunal_id)`

## Paso 5 — Actualizar los archivos existentes

**`models/__init__.py`** — agregar el import del nuevo modelo para que SQLAlchemy lo registre:
```python
from models.<nombre> import <Nombre>
```

**`main.py`** — agregar el router:
```python
from routers import <nombre>
app.include_router(<nombre>.router)
```

También actualizar el modelo relacionado (si lo hay) para agregar el `back_populates` correspondiente.

## Paso 6 — Confirmar con un resumen limpio

```
✅ Archivos creados:
   models/<nombre>.py
   schemas/<nombre>.py
   routers/<nombre>.py

✅ Archivos modificados:
   models/__init__.py — import agregado
   main.py — router registrado
   models/<relacionado>.py — relationship agregada (si aplica)

📋 Endpoints disponibles:
   GET    /<nombres>          — lista con paginación
   POST   /<nombres>          — crear
   GET    /<nombres>/{id}     — detalle
   PUT    /<nombres>/{id}     — editar
   PATCH  /<nombres>/{id}/desactivar

🔁 Reinicia el servidor: uvicorn main:app --reload
```
