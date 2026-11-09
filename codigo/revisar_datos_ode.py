import pandas as pd
import numpy as np

archivo = "datos_procesados_corregidos.xlsx"

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

df = pd.read_excel(archivo)
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

variables = [
    "OD", "Días cultivo", "pH", "Temperatura (°C)",
    "Volumen (L)", "Luces encendidas", "Aire encendido"
]

df = df[
    df["Ciclo_ID"].isin(secuencias) &
    (df["Estado"].astype(str).str.lower() != "descarte")
].copy()

for c in variables:
    df[c] = pd.to_numeric(df[c], errors="coerce") if c not in [
        "Luces encendidas", "Aire encendido"
    ] else df[c]

df["Datos_completos"] = df[variables].notna().all(axis=1)

print("\nCOBERTURA SIMULTÁNEA")
print("=" * 65)

for sec, g in df.groupby("Ciclo_ID"):
    completos = g["Datos_completos"].sum()
    print(
        f"{sec}: {completos}/{len(g)} registros completos "
        f"({100*completos/len(g):.1f}%)"
    )

print("\nREGISTROS DISPONIBLES PARA EL PRIMER AJUSTE")
print("=" * 65)

seleccion = df[
    df["Ciclo_ID"].isin([
        "Planta__BIM-08_C12",
        "Planta__BIM-02_C01",
        "Planta__BIM-02_C04"
    ])
].sort_values(["Ciclo_ID", "Fecha"])

for sec, g in seleccion.groupby("Ciclo_ID"):
    print("\n", sec)
    print(g[["Fecha"] + variables].to_string(index=False))
