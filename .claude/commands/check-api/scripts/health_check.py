"""
Script de verificación de salud del proyecto Casas Comunales.
Ejecutar desde la carpeta raíz del proyecto:
  python .claude/commands/check-api/scripts/health_check.py
"""
import sys
import os
import importlib

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, PROJECT_DIR)
os.chdir(PROJECT_DIR)

RESULTS = []

def check(label, passed, detail=""):
    icon = "✅" if passed else "❌"
    RESULTS.append((icon, label, detail))
    print(f"  {icon} {label}" + (f" — {detail}" if detail else ""))

# ── 1. Dependencias ──────────────────────────────────────────────────────────
print("\n📦 Dependencias:")
paquetes = {
    "fastapi": "fastapi",
    "sqlalchemy": "sqlalchemy",
    "psycopg2": "psycopg2",
    "jose": "python-jose",
    "passlib": "passlib",
    "uvicorn": "uvicorn",
    "dotenv": "python-dotenv",
    "pydantic": "pydantic",
}
for modulo, paquete in paquetes.items():
    try:
        importlib.import_module(modulo)
        check(paquete, True)
    except ImportError:
        check(paquete, False, f"pip install {paquete}")

# ── 2. Variables de entorno ───────────────────────────────────────────────────
print("\n🔐 Variables de entorno (.env):")
try:
    from dotenv import load_dotenv
    load_dotenv()
    db_url = os.getenv("DATABASE_URL", "")
    secret = os.getenv("SECRET_KEY", "")
    check("DATABASE_URL", bool(db_url) and db_url.startswith("postgresql://"),
          "falta o formato incorrecto" if not db_url else "")
    check("SECRET_KEY", bool(secret) and secret != "changeme-super-secret",
          "débil o no definida" if not secret or secret == "changeme-super-secret" else "")
except Exception as e:
    check(".env cargable", False, str(e))

# ── 3. Conexión BD ────────────────────────────────────────────────────────────
print("\n🐘 Conexión PostgreSQL:")
try:
    import psycopg2
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    conn.close()
    check("Conexión exitosa", True)
except Exception as e:
    check("Conexión exitosa", False, str(e))

# ── 4. Tablas ─────────────────────────────────────────────────────────────────
print("\n🗂  Tablas en la BD:")
TABLAS = [
    "usuarios", "casas_comunales", "participantes", "talleres",
    "inscripciones_talleres", "horarios", "actividades", "actividad_casas",
    "asistencia_participantes", "evaluaciones", "control_facilitadores",
    "documentos_facilitadores"
]
try:
    import psycopg2
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
    existentes = {r[0] for r in cur.fetchall()}
    conn.close()
    for t in TABLAS:
        check(t, t in existentes)
except Exception as e:
    print(f"  ❌ No se pudo consultar tablas: {e}")

# ── 5. Import de la app ───────────────────────────────────────────────────────
print("\n🚀 App FastAPI:")
try:
    from main import app
    endpoints = [r for r in app.routes if hasattr(r, "methods")]
    check("main.py importa sin errores", True, f"{len(endpoints)} endpoints registrados")
    print("\n📋 Endpoints registrados:")
    for r in sorted(endpoints, key=lambda x: x.path):
        metodo = sorted(r.methods)[0]
        print(f"     {metodo:7} {r.path}")
except Exception as e:
    check("main.py importa sin errores", False, str(e))

# ── Resumen ───────────────────────────────────────────────────────────────────
total = len(RESULTS)
ok = sum(1 for r in RESULTS if r[0] == "✅")
print(f"\n{'═'*40}")
print(f"  Resultado: {ok}/{total} verificaciones OK")
if ok == total:
    print("\n  🎉 Todo listo. Levanta el servidor con:")
    print("     uvicorn main:app --reload")
    print("     Docs: http://localhost:8000/docs")
else:
    print(f"\n  ⚠️  {total - ok} problema(s) encontrado(s). Revisa los ❌ arriba.")
print(f"{'═'*40}\n")
