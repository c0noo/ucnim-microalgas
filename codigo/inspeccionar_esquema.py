import pandas as pd
from pathlib import Path

ARCHIVOS = [
    "matriz_diagnostico_operacional/matriz_diagnostico_ambiental_operacional.xlsx",
    "analisis_residuos_loo/analisis_residuos_y_predicciones.xlsx",
    "validacion_loo/resultados_validacion_loo.xlsx",
]

pd.set_option("display.width", 200, "display.max_columns", 60, "display.max_colwidth", 30)

for f in ARCHIVOS:
    p = Path(f)
    print("=" * 100, f"\n{f}  (existe: {p.exists()})")
    if not p.exists():
        continue
    for hoja, df in pd.read_excel(p, sheet_name=None).items():
        print(f"\n--- hoja '{hoja}': {df.shape[0]} filas x {df.shape[1]} columnas")
        print("columnas:", list(df.columns))
        print(df.head(3).to_string())
