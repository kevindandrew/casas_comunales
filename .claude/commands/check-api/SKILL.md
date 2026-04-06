---
name: check-api
description: Verifica que el proyecto FastAPI de Casas Comunales esté correctamente configurado y listo para correr. Úsalo cuando el usuario diga "verifica la API", "chequea que todo esté bien", "por qué no arranca el servidor", "revisa la configuración", "quiero hacer deploy", o cuando el servidor dé un error al iniciar. Comprueba dependencias, .env, conexión a BD, tablas y que la app importe sin errores — todo en un solo comando.
---

# Check API — Casas Comunales

El proyecto está en `c:\Users\KEVIN\Desktop\casas comunales`.

La forma más rápida de verificar todo es correr el script incluido. Solo si hay algún problema específico, usa las verificaciones manuales de abajo.

## Verificación rápida (recomendada)

Corre el script de salud desde la carpeta del proyecto:

```bash
cd "c:/Users/KEVIN/Desktop/casas comunales"
python .claude/commands/check-api/scripts/health_check.py
```

El script verifica en orden: dependencias → variables .env → conexión BD → tablas → import de la app → lista de endpoints.

Si todo está ✅ al final, el servidor está listo.

## Verificaciones manuales (si el script falla o quieres más detalle)

### Si hay error de import en main.py

Lee el traceback completo. Los errores más comunes son:
- `ModuleNotFoundError` → falta una dependencia, instalar con pip
- `ImportError circular` → algún modelo se importa antes de estar definido
- `KeyError` / `RuntimeError` → variable de entorno faltante en .env

Solución estándar:
```bash
cd "c:/Users/KEVIN/Desktop/casas comunales"
python -c "from main import app" 2>&1
```

### Si la BD no conecta

Verificar que PostgreSQL esté corriendo y que las credenciales en `.env` sean correctas:
```
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/casas_comunales
```

### Si falta alguna tabla

Significa que la BD no tiene el schema aplicado. Correr:
```bash
python -c "from main import app"  # esto ejecuta Base.metadata.create_all
```

O crear las tablas manualmente usando el SQL del proyecto.

## Reporte esperado

```
══════════════════════════════════════
  CHECK API — Casas Comunales
══════════════════════════════════════
  Resultado: 20/20 verificaciones OK

  🎉 Todo listo. Levanta el servidor con:
     uvicorn main:app --reload
     Docs: http://localhost:8000/docs
══════════════════════════════════════
```

Si hay ❌, el script indica exactamente qué falla y cómo arreglarlo.
