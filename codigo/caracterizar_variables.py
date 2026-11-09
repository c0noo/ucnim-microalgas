import pandas as pd
import numpy as np

ARCHIVO = "datos_procesados_corregidos.xlsx"
SALIDA = "caracterizacion_variables_secuencias.xlsx"

secuencias = [
    "Planta__BIM-08_C12",
    "Planta__BIM-02_C01",
    "Planta__BIM-02_C04",
    "Planta__BIM-02_C06",
    "Planta__BIM-09_C07",
    "Planta__BIM-01_C06",
    "Planta__BIM-04_C04",
    "Planta__BIM-04_C07",
    "Planta__BIM-09_C09",
    "Planta__BIM-10_C07"
]

variables_numericas = [
    "OD",
    "pH",
    "Temperatura (°C)",
    "EC",
    "Volumen (L)",
    "Cantidad luces",
    "Días cultivo",
    "μ (d⁻¹)",
    "Micro (1-5)",
    "Macro (1-5)"
]

variables_categoricas = [
    "Luces encendidas",
    "Aire encendido",
    "Estado",
    "Ritmo"
]

df = pd.read_excel(ARCHIVO)
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

# Seleccionar los ciclos de interés desde los datos originales
datos = df[df["Ciclo_ID"].isin(secuencias)].copy()

# Excluir descartes de los análisis de condiciones del cultivo.
# Se conservan en el detalle y se contabilizan por separado.
biologicos = datos[
    datos["Estado"].astype(str).str.strip().str.lower() != "descarte"
].copy()

for col in variables_numericas:
    if col in biologicos.columns:
        biologicos[col] = pd.to_numeric(biologicos[col], errors="coerce")

# 1. Resumen por secuencia
resumen = []

for sec in secuencias:
    g = datos[datos["Ciclo_ID"] == sec].copy()
    gb = biologicos[biologicos["Ciclo_ID"] == sec].copy()

    fechas = gb["Fecha"].dropna().sort_values()

    resumen.append({
        "Secuencia": sec,
        "N_registros_originales": len(g),
        "N_registros_sin_descarte": len(gb),
        "N_registros_descarte": (g["Estado"] == "Descarte").sum(),
        "Fecha_inicio": fechas.min() if len(fechas) else pd.NaT,
        "Fecha_fin": fechas.max() if len(fechas) else pd.NaT,
        "Dias_calendario": (
            (fechas.max() - fechas.min()).total_seconds() / 86400
            if len(fechas) >= 2 else np.nan
        ),
        "N_OD": gb["OD"].notna().sum(),
        "N_pH": gb["pH"].notna().sum(),
        "N_temperatura": gb["Temperatura (°C)"].notna().sum(),
        "N_EC": gb["EC"].notna().sum(),
        "N_volumen": gb["Volumen (L)"].notna().sum(),
        "N_luces": gb["Luces encendidas"].notna().sum(),
        "N_aire": gb["Aire encendido"].notna().sum(),
        "N_mu": gb["μ (d⁻¹)"].notna().sum(),
        "N_micro": gb["Micro (1-5)"].notna().sum(),
        "N_macro": gb["Macro (1-5)"].notna().sum()
    })

resumen = pd.DataFrame(resumen)

# 2. Disponibilidad y estadísticos por variable
disponibilidad = []

for sec in secuencias:
    g = biologicos[biologicos["Ciclo_ID"] == sec].copy()
    n = len(g)

    for col in variables_numericas:
        if col not in g.columns:
            continue

        x = pd.to_numeric(g[col], errors="coerce").dropna()

        disponibilidad.append({
            "Secuencia": sec,
            "Variable": col,
            "Tipo": "Numerica",
            "N_registros": n,
            "N_disponibles": len(x),
            "Porcentaje_disponible": round(100 * len(x) / n, 1) if n else np.nan,
            "Valores_distintos": x.nunique(),
            "Minimo": x.min() if len(x) else np.nan,
            "Mediana": x.median() if len(x) else np.nan,
            "Maximo": x.max() if len(x) else np.nan,
            "Desviacion_estandar": x.std() if len(x) >= 2 else np.nan,
            "Frecuencias": ""
        })

    for col in variables_categoricas:
        if col not in g.columns:
            continue

        x = g[col].dropna().astype(str).str.strip()
        frecuencias = x.value_counts().to_dict()

        disponibilidad.append({
            "Secuencia": sec,
            "Variable": col,
            "Tipo": "Categorica",
            "N_registros": n,
            "N_disponibles": len(x),
            "Porcentaje_disponible": round(100 * len(x) / n, 1) if n else np.nan,
            "Valores_distintos": x.nunique(),
            "Minimo": np.nan,
            "Mediana": np.nan,
            "Maximo": np.nan,
            "Desviacion_estandar": np.nan,
            "Frecuencias": str(frecuencias)
        })

disponibilidad = pd.DataFrame(disponibilidad)

# 3. Detalle de registros originales
detalle = datos.sort_values(
    ["Ciclo_ID", "Fecha"]
).copy()

with pd.ExcelWriter(SALIDA, engine="openpyxl") as writer:
    resumen.to_excel(writer, sheet_name="Resumen_secuencias", index=False)
    disponibilidad.to_excel(writer, sheet_name="Disponibilidad_variables", index=False)
    detalle.to_excel(writer, sheet_name="Detalle_registros", index=False)

print("\nAUDITORÍA TERMINADA")
print("Archivo:", SALIDA)
print("\nResumen de secuencias:")
print(resumen.to_string(index=False))

print("\nDisponibilidad de variables:")
print(
    disponibilidad[
        ["Variable", "N_disponibles", "N_registros", "Porcentaje_disponible"]
    ].groupby("Variable").agg({
        "N_disponibles": "sum",
        "N_registros": "sum",
        "Porcentaje_disponible": "mean"
    }).round(1).to_string()
)
