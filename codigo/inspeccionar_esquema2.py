import pandas as pd
pd.set_option("display.width", 200, "display.max_columns", 60, "display.max_colwidth", 30)
for f in ["datos_procesados_corregidos.xlsx", "evaluacion_secuencias_final.xlsx"]:
    print("=" * 100, f)
    for hoja, df in pd.read_excel(f, sheet_name=None).items():
        print(f"\n--- hoja '{hoja}': {df.shape[0]} filas x {df.shape[1]} columnas")
        print("columnas:", list(df.columns))
        print(df.head(3).to_string())
