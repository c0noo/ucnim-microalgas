import pandas as pd
import numpy as np

datos = pd.read_excel(
    "evaluacion_secuencias_final.xlsx",
    sheet_name="Detalle_OD"
)

resultados = []

for secuencia, g in datos.groupby("Secuencia"):
    g = g.sort_values("Fecha").copy()

    edad = g["Edad"].dropna().astype(float)
    fechas = pd.to_datetime(g["Fecha"], errors="coerce").dropna()

    if len(edad) < 2:
        continue

    diferencias_edad = np.diff(edad.to_numpy())
    diferencias_fecha = (
        fechas.diff().dt.total_seconds().dropna().to_numpy() / 86400
    )

    resultados.append({
        "Secuencia": secuencia,
        "N_OD": len(g),
        "Edades_distintas": edad.nunique(),
        "Rango_edad": edad.max() - edad.min(),
        "Dias_calendario": (fechas.max() - fechas.min()).total_seconds() / 86400,
        "Intervalo_edad_maximo": (
            np.max(diferencias_edad) if len(diferencias_edad) else np.nan
        ),
        "Intervalo_calendario_maximo": (
            np.max(diferencias_fecha) if len(diferencias_fecha) else np.nan
        ),
        "Intervalos_edad_cero": int((diferencias_edad == 0).sum()),
        "Intervalos_edad_negativos": int((diferencias_edad < 0).sum()),
        "Edad_inicial": edad.iloc[0],
        "Edad_final": edad.iloc[-1]
    })

salida = pd.DataFrame(resultados)
salida = salida.sort_values(
    ["N_OD", "Rango_edad"],
    ascending=[False, False]
)

salida.to_excel("auditoria_cobertura_curvas.xlsx", index=False)

print("SECUENCIAS AUDITADAS:", len(salida))
print(salida.round(2).to_string(index=False))
