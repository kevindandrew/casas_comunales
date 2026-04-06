---
name: insertar-excel
description: Lee un archivo Excel (.xlsx) o CSV (.csv) y carga los datos masivamente a la base de datos PostgreSQL del proyecto Casas Comunales. Úsalo cuando el usuario diga "te paso un Excel", "tengo un archivo con datos", "quiero cargar datos masivos", "inserta desde Excel/CSV", "tengo una lista de participantes/casas/talleres en una hoja de cálculo", o cuando comparta una ruta a un archivo de datos. También úsalo cuando el usuario migre datos de otro sistema. Maneja automáticamente el mapeo de columnas, validaciones de duplicados y reporte de errores.
---

# Insertar datos desde Excel/CSV — Casas Comunales

El proyecto está en `c:\Users\KEVIN\Desktop\casas comunales`. Credenciales de BD en `.env`.

El objetivo es hacer la carga de datos lo más segura posible: mostrar al usuario qué se encontró, validar antes de tocar la BD, e insertar solo lo que es válido.

## Paso 1 — Verificar pandas

```bash
python -c "import pandas; import openpyxl; print('OK')"
```
Si falla: `pip install pandas openpyxl`

## Paso 2 — Obtener información del usuario

Si el usuario no lo dijo, preguntar en un solo mensaje:
1. ¿Ruta del archivo? (ej: `C:/Users/KEVIN/Desktop/datos.xlsx`)
2. ¿Qué tipo de datos trae? (participantes / casas comunales / talleres / usuarios)

Si ya lo dijo, continuar directamente.

## Paso 3 — Leer y previsualizar

```python
import pandas as pd

ruta = "ruta/del/archivo"
df = pd.read_csv(ruta) if ruta.lower().endswith(".csv") else pd.read_excel(ruta)

# Limpiar nombres de columnas (espacios, mayúsculas)
df.columns = df.columns.str.strip()

print(f"Total filas: {len(df)}")
print(f"Columnas encontradas: {df.columns.tolist()}")
print(df.head(3).to_string())
```

Mostrar al usuario las columnas reales del archivo y proponer el mapeo. Confirmar antes de insertar.

## Paso 4 — Mapeos de referencia

Ajustar según las columnas reales del archivo. Estos son los mapeos más comunes:

**Participantes** → tabla `participantes`
| Columna Excel (posibles nombres) | Campo BD |
|----------------------------------|----------|
| Nombres, Nombre, NOMBRE | `nombres` (obligatorio) |
| Apellidos, Apellido | `apellidos` (obligatorio) |
| CI, Cédula, Cedula, C.I. | `ci` (obligatorio, único) |
| Fecha Nac, FechaNacimiento, F. Nacimiento | `fecha_nacimiento` |
| Género, Genero, Sexo | `genero` → normalizar a M/F/O |
| Teléfono, Telefono, Cel | `telefono` |
| Casa, Casa Comunal, CasaID | `casa_comunal_id` |

**Casas Comunales** → tabla `casas_comunales`
| Columna Excel | Campo BD |
|---------------|----------|
| Nombre, Casa | `nombre` (obligatorio) |
| Dirección, Direccion | `direccion` (obligatorio) |
| Macrodistrito, Distrito | `macrodistrito` (obligatorio) |
| Representante | `representante_nombre` |
| Teléfono, Contacto | `contacto_telefono` |

## Paso 5 — Validar antes de insertar

Usar el script de validación para no sorprender al usuario:

```python
import psycopg2, os
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

duplicados = []
nulos = []

for idx, row in df.iterrows():
    fila = idx + 2  # +2 porque idx empieza en 0 y hay cabecera
    
    # Verificar campos obligatorios
    if pd.isna(row.get("ci")) or str(row.get("ci", "")).strip() == "":
        nulos.append(f"Fila {fila}: CI vacía")
        continue
    
    # Verificar duplicados en BD
    cur.execute("SELECT id FROM participantes WHERE ci = %s", (str(row["ci"]).strip(),))
    if cur.fetchone():
        duplicados.append(f"Fila {fila}: CI {row['ci']} ya existe en BD")

conn.close()
print(f"Filas válidas para insertar: {len(df) - len(duplicados) - len(nulos)}")
print(f"Duplicados: {len(duplicados)}")
print(f"Nulos en campos obligatorios: {len(nulos)}")
```

Reportar al usuario y pedir confirmación para continuar.

## Paso 6 — Insertar (solo los válidos)

Insertar fila por fila con manejo de errores individuales. Una fila que falla no cancela las demás:

```python
insertados = 0
fallidos = []

for idx, row in df_validos.iterrows():
    try:
        cur.execute("""
            INSERT INTO participantes (nombres, apellidos, ci, genero, telefono, casa_comunal_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            str(row["nombres"]).strip(),
            str(row["apellidos"]).strip(),
            str(row["ci"]).strip(),
            str(row.get("genero", "")).strip().upper()[:1] or None,
            str(row.get("telefono", "")).strip() or None,
            int(row["casa_comunal_id"]) if pd.notna(row.get("casa_comunal_id")) else None,
        ))
        insertados += 1
    except Exception as e:
        conn.rollback()
        fallidos.append(f"Fila {idx+2}: {str(e)[:80]}")
    else:
        conn.commit()

cur.close()
conn.close()
```

## Paso 7 — Reporte final

```
📊 RESULTADO DE INSERCIÓN
─────────────────────────
✅ Insertados correctamente:  N
⚠️  Omitidos (ya existían):   N
❌ Errores al insertar:       N

Detalle de errores (si hay):
  - Fila 5: valor de fecha_nacimiento inválido
  - Fila 12: casa_comunal_id 99 no existe
```
