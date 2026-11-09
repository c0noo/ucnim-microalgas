import pandas as pd
import numpy as np

# Archivos
archivo_datos = "datos_procesados_corregidos.xlsx"
archivo_maestro = "matriz_maestra_candidatos.xlsx"
archivo_eval = "evaluacion_viabilidad_modelamiento.xlsx"

datos = pd.read_excel(archivo_datos)
maestro = pd.read_excel(archivo_maestro, sheet_name="Matriz_Maestra")
evaluacion = pd.read_excel(archivo_eval)

# Normalizar fechas y ordenar registros
datos["Fecha"] = pd.to_datetime(datos["Fecha"], errors="coerce")
datos = datos.sort_values(["Ciclo_ID", "Fecha"])

resultados = []

for _, candidato in maestro.iterrows():
    ciclo = candidato["Ciclo_ID"]

    grupo = datos[datos["Ciclo_ID"] == ciclo].copy()

    # Mediciones OD con edad, excluyendo descarte
    biologicas = grupo[
        grupo["OD"].notna()
        & grupo["Días cultivo"].notna()
        & (grupo["Estado"] != "Descarte")
    ].sort_values("Fecha")

    # Mediciones OD con edad, incluyendo descarte
    todas = grupo[
        grupo["OD"].notna()
        & grupo["Días cultivo"].notna()
    ].sort_values("Fecha")

    if len(biologicas) >= 2:
        inicial = biologicas.iloc[0]["OD"]
        final = biologicas.iloc[-1]["OD"]
        tendencia = final - inicial
        aumentos = (biologicas["OD"].diff() > 0).sum()
        descensos = (biologicas["OD"].diff() < 0).sum()
    else:
        inicial = final = tendencia = np.nan
        aumentos = descensos = 0

    if len(todas) >= 2:
        inicial_total = todas.iloc[0]["OD"]
        final_total = todas.iloc[-1]["OD"]
    else:
        inicial_total = final_total = np.nan

    resultados.append({
        "Ciclo_ID": ciclo,
        "OD_biologicas": len(biologicas),
        "OD_con_edad_incluyendo_descarte": len(todas),
        "OD_inicial_biologica": inicial,
        "OD_final_biologica": final,
        "Tendencia_biologica": tendencia,
        "Aumentos_biologicos": aumentos,
        "Descensos_biologicos": descensos,
        "OD_inicial_incluyendo_descarte": inicial_total,
        "OD_final_incluyendo_descarte": final_total,
        "Termina_en_descarte": candidato["Termina_En_Descarte"],
        "Estado_revision": candidato["Estado_Revision"]
    })

comparacion = pd.DataFrame(resultados)

# Incorporar los indicadores de la evaluación anterior
comparacion = comparacion.merge(
    evaluacion[
        ["Ciclo_ID", "N_OD", "N_Edades", "Tendencia_Neta"]
    ],
    on="Ciclo_ID",
    how="left"
)

comparacion["Diferencia_tendencia"] = (
    comparacion["Tendencia_Neta"]
    - comparacion["Tendencia_biologica"]
)

comparacion.to_excel(
    "auditoria_tendencias_candidatos.xlsx",
    index=False
)

print("\nAUDITORÍA TERMINADA")
print("Candidatos revisados:", len(comparacion))
print("Archivo generado: auditoria_tendencias_candidatos.xlsx")

print("\nDIFERENCIAS ENTRE TENDENCIA ANTERIOR Y BIOLÓGICA:")
print(
    comparacion[
        [
            "Ciclo_ID",
            "OD_biologicas",
            "N_OD",
            "Tendencia_Neta",
            "Tendencia_biologica",
            "Diferencia_tendencia"
        ]
    ].to_string(index=False)
)
