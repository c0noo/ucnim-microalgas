import pandas as pd
import numpy as np

datos = pd.read_excel("datos_procesados_corregidos.xlsx")
maestro = pd.read_excel(
    "matriz_maestra_candidatos.xlsx",
    sheet_name="Matriz_Maestra"
)
segmentos = pd.read_excel(
    "segmentacion_analitica_reinicios.xlsx",
    sheet_name="Registros_segmentados"
)

datos["Fecha"] = pd.to_datetime(datos["Fecha"], errors="coerce")

# Identificar los ciclos que tienen segmentación analítica
ciclos_segmentados = segmentos["Ciclo_ID"].dropna().unique()

# Asociar cada registro original a su segmento, usando su fila de Excel
mapa = segmentos[
    ["Fila_Excel_Original", "Segmento_Analitico"]
].drop_duplicates("Fila_Excel_Original")

datos = datos.merge(
    mapa,
    on="Fila_Excel_Original",
    how="left"
)

# Los ciclos sin reinicio analítico conservan su identificador original
datos["Secuencia"] = datos["Segmento_Analitico"]
datos.loc[
    ~datos["Ciclo_ID"].isin(ciclos_segmentados),
    "Secuencia"
] = datos.loc[
    ~datos["Ciclo_ID"].isin(ciclos_segmentados),
    "Ciclo_ID"
]

resultados = []
detalles = []

for _, candidato in maestro.iterrows():
    ciclo = candidato["Ciclo_ID"]

    grupo = datos[datos["Ciclo_ID"] == ciclo].copy()

    for secuencia, g in grupo.groupby("Secuencia", dropna=False):
        # Registros útiles para analizar OD frente a edad
        validos = g[
            g["OD"].notna()
            & g["Días cultivo"].notna()
            & (g["Estado"] != "Descarte")
        ].copy()

        validos = validos.sort_values("Fecha")

        if validos.empty:
            continue

        edades = validos["Días cultivo"]
        od = validos["OD"]
        fechas = validos["Fecha"]

        intervalos = fechas.diff().dt.total_seconds() / 86400
        cambios_edad = edades.diff()

        aumentos = int((od.diff() > 0).sum())
        descensos = int((od.diff() < 0).sum())
        estables = int((od.diff() == 0).sum())

        n_od = len(validos)
        n_edades = edades.nunique()
        rango_edad = edades.max() - edades.min()

        # Alertas observadas en esta secuencia
        intervalos_largos = int((intervalos > 7).sum())
        edades_repetidas = int(edades.duplicated().sum())
        od_alta = (
            validos["OD_Alta_Revisar"].fillna(False).astype(bool).any()
            if "OD_Alta_Revisar" in validos.columns else False
        )

        tendencia = od.iloc[-1] - od.iloc[0] if n_od >= 2 else np.nan

        # Clasificación orientativa de suficiencia de datos
        if n_od < 5 or n_edades < 5:
            clasificacion = "Insuficiente para caracterizar"
        elif od_alta or intervalos_largos > 0 or edades_repetidas > 0:
            clasificacion = "Exploratorio con revisión"
        elif n_od >= 7 and n_edades >= 7:
            clasificacion = "Prioritario para caracterización"
        else:
            clasificacion = "Caracterización exploratoria"

        resultados.append({
            "Ciclo_ID": ciclo,
            "Secuencia": secuencia,
            "Estado_revision_ciclo": candidato["Estado_Revision"],
            "N_OD_con_edad": n_od,
            "N_edades_distintas": n_edades,
            "Edad_min": edades.min(),
            "Edad_max": edades.max(),
            "Rango_edad": rango_edad,
            "Fecha_inicio": fechas.min(),
            "Fecha_fin": fechas.max(),
            "OD_min": od.min(),
            "OD_max": od.max(),
            "OD_inicial": od.iloc[0],
            "OD_final": od.iloc[-1],
            "Tendencia_neta": tendencia,
            "Aumentos": aumentos,
            "Descensos": descensos,
            "Estables": estables,
            "Intervalos_mayores_7_dias": intervalos_largos,
            "Edades_repetidas": edades_repetidas,
            "Tiene_OD_alta_marcada": od_alta,
            "Clasificacion": clasificacion
        })

        for _, fila in validos.iterrows():
            detalles.append({
                "Ciclo_ID": ciclo,
                "Secuencia": secuencia,
                "Fecha": fila["Fecha"],
                "Edad": fila["Días cultivo"],
                "OD": fila["OD"],
                "Estado": fila["Estado"],
                "OD_Alta_Revisar": fila.get("OD_Alta_Revisar", False)
            })

resumen = pd.DataFrame(resultados)
detalle = pd.DataFrame(detalles)

# Ordenar secuencias con mayor cantidad de datos primero
resumen = resumen.sort_values(
    ["N_OD_con_edad", "N_edades_distintas"],
    ascending=False
)

criterios = pd.DataFrame([
    ["Insuficiente para caracterizar",
     "Menos de 5 OD con edad o menos de 5 edades distintas."],
    ["Exploratorio con revisión",
     "Tiene al menos 5 OD y edades distintas, pero presenta alertas."],
    ["Caracterización exploratoria",
     "Tiene entre 5 y 6 OD con edades distintas y sin alertas detectadas."],
    ["Prioritario para caracterización",
     "Tiene al menos 7 OD y 7 edades distintas, sin alertas detectadas."]
], columns=["Clasificacion", "Criterio"])

with pd.ExcelWriter("evaluacion_secuencias_final.xlsx") as writer:
    resumen.to_excel(writer, sheet_name="Resumen_secuencias", index=False)
    detalle.to_excel(writer, sheet_name="Detalle_OD", index=False)
    criterios.to_excel(writer, sheet_name="Criterios", index=False)

print("\nEVALUACIÓN TERMINADA")
print("Secuencias evaluadas:", len(resumen))
print("Archivo: evaluacion_secuencias_final.xlsx")

print("\nCLASIFICACIÓN:")
print(resumen["Clasificacion"].value_counts().to_string())

print("\nSECUENCIAS CON MAYOR CANTIDAD DE MEDICIONES:")
columnas = [
    "Ciclo_ID", "Secuencia", "N_OD_con_edad",
    "N_edades_distintas", "Rango_edad",
    "Tendencia_neta", "Clasificacion"
]
print(resumen[columnas].head(20).to_string(index=False))
