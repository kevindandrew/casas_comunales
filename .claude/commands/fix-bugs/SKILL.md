---
name: fix-bugs
description: Escanea dinámicamente el código del proyecto FastAPI Casas Comunales, detecta problemas reales en el estado actual del código y los corrige. Úsalo cuando el usuario diga "corrige los bugs", "hay algo mal en el código", "arregla los errores", "el servidor da error", "revisa el código", o cuando quieras hacer una limpieza de calidad antes de un deploy. A diferencia de una lista fija, este skill analiza el código tal como está ahora y solo corrige lo que realmente necesita corrección.
---

# Fix Bugs — Casas Comunales

El proyecto está en `c:\Users\KEVIN\Desktop\casas comunales`.

La idea aquí es hacer lo que haría un desarrollador senior revisando el código con ojos frescos: leer cada archivo relevante, entender qué está haciendo, identificar lo que podría fallar, y arreglarlo. No seguir una lista mecánica de cambios, sino razonar sobre el código real.

## Paso 1 — Leer el estado actual del código

Lee estos archivos en paralelo para entender el estado real del proyecto:

- `security.py` — JWT, hashing, dependencias auth
- `database.py` — conexión PostgreSQL
- `models/usuario.py`, `models/taller.py`, `models/asistencia.py` — modelos críticos
- `schemas/usuario.py` — serialización de enums
- `routers/participantes.py`, `routers/facilitadores.py` — manejo de uploads
- `main.py` — registro de routers

## Paso 2 — Categorías a revisar

Para cada archivo leído, busca activamente estos problemas:

**Seguridad:**
- ¿`SECRET_KEY` tiene un valor por defecto débil o fijo? Si sí, hacer que lance error si no está en .env
- ¿Los uploads validan extensiones? Extensiones permitidas: `.jpg`, `.jpeg`, `.png`, `.pdf`
- ¿Hay credenciales hardcodeadas como fallback?

**Integridad de datos:**
- ¿Columnas que deberían ser `nullable=True` están sin esa opción?
- ¿ENUMs se serializan correctamente como string en los schemas de respuesta?
- ¿Los campos `Computed` (como `nota_final`) están bien definidos?

**Runtime:**
- ¿Los imports circulares están manejados?
- ¿Todos los routers están registrados en `main.py`?
- ¿Los modelos están todos importados en `models/__init__.py`?

**Calidad:**
- ¿Hay lógica duplicada que debería estar centralizada?
- ¿Los 404 y 400 tienen mensajes claros para el frontend?

## Paso 3 — Corregir lo que realmente está mal

Por cada problema encontrado:
1. Lee el fragmento exacto que hay que cambiar
2. Aplica la corrección mínima necesaria — no refactorices lo que funciona
3. Verifica que el cambio no rompa otras partes del código

No inventes problemas que no existen. Si el código ya está bien, dilo.

## Paso 4 — Verificar que la app arranca

```bash
cd "c:/Users/KEVIN/Desktop/casas comunales" && python -c "from main import app; print('OK -', len([r for r in app.routes if hasattr(r,'methods')]), 'endpoints')"
```

Si falla, diagnosticar el error y corregirlo.

## Paso 5 — Reporte final

```
✅ Corregido:
   security.py — SECRET_KEY ahora lanza error si no está en .env
   routers/participantes.py — validación de extensiones de archivo

⚠️  Revisado, sin cambios necesarios:
   models/taller.py — fecha_inscripcion ya tiene nullable=True
   
ℹ️  No revisado (sin acceso o fuera de scope):
   [si aplica]

🔁 Reinicia el servidor: uvicorn main:app --reload
```
