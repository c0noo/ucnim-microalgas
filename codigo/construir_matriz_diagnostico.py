
import os
import pandas as pd
import numpy as np


# ============================================================
# 1. CONFIGURACION
# ============================================================

ARCHIVO = (
    "analisis_residuos_loo/"
    "analisis_residuos_y_predicciones.xlsx"
)

CARPETA = "matriz_diagnostico_operacional"

os.makedirs(CARPETA, exist_ok=True)

SALIDA = os.path.join(
    CARPETA,
    "matriz_diagnostico_ambiental_operacional.xlsx"
)


# ============================================================
# 2. CARGAR DATOS
# ============================================================

datos = pd.read_excel(
    ARCHIVO,
    sheet_name="Detalle_observaciones"
)

if "Secuencia" not in datos.columns:
    datos["Secuencia"] = datos["Ciclo_ID"]

datos["Fecha"] = pd.to_datetime(
    datos["Fecha"], errors="coerce"
)

# Variables numéricas que queremos revisar
variables_numericas = [
    "OD",
    "pH",
    "Temperatura (°C)",
    "EC",
    "Volumen (L)",
    "Días cultivo"
]

for variable in variables_numericas:

    if variable in datos.columns:

        datos[variable] = pd.to_numeric(
            datos[variable],
            errors="coerce"
        )


# ============================================================
# 3. ORDENAR REGISTROS
# ============================================================

datos = datos.sort_values(
    ["Secuencia", "Días cultivo", "Fecha"]
).reset_index(drop=True)


# ============================================================
# 4. CALCULAR CAMBIOS ENTRE OBSERVACIONES
# ============================================================

variables_cambio = [
    "pH",
    "Temperatura (°C)",
    "EC",
    "Volumen (L)"
]

for variable in variables_cambio:

    if variable in datos.columns:

        nombre_cambio = "Cambio_" + variable

        datos[nombre_cambio] = (
            datos.groupby("Secuencia")[variable]
            .diff()
        )


# ============================================================
# 5. CALCULAR MAGNITUD Y DIRECCION DEL ERROR
# ============================================================

datos["Error_abs_exp"] = (
    datos["Error_exponencial"].abs()
)

datos["Error_abs_baranyi"] = (
    datos["Error_baranyi"].abs()
)

datos["Direccion_error_exp"] = np.where(
    datos["Error_exponencial"] > 0,
    "Subestimación",
    np.where(
        datos["Error_exponencial"] < 0,
        "Sobreestimación",
        "Sin error"
    )
)

datos["Direccion_error_baranyi"] = np.where(
    datos["Error_baranyi"] > 0,
    "Subestimación",
    np.where(
        datos["Error_baranyi"] < 0,
        "Sobreestimación",
        "Sin error"
    )
)

datos["Ranking_error_exp"] = (
    datos.groupby("Secuencia")["Error_abs_exp"]
    .rank(method="min", ascending=False)
)

datos["Ranking_error_baranyi"] = (
    datos.groupby("Secuencia")["Error_abs_baranyi"]
    .rank(method="min", ascending=False)
)


# ============================================================
# 6. CONSTRUIR MATRIZ DE DIAGNOSTICO
# ============================================================

columnas = [
    "Secuencia",
    "Fecha",
    "Días cultivo",
    "OD",
    "OD_predicha_exponencial",
    "OD_predicha_baranyi",
    "Error_exponencial",
    "Error_baranyi",
    "Error_abs_exp",
    "Error_abs_baranyi",
    "Direccion_error_exp",
    "Direccion_error_baranyi",
    "Ranking_error_exp",
    "Ranking_error_baranyi",
    "pH",
    "Cambio_pH",
    "Temperatura (°C)",
    "Cambio_Temperatura (°C)",
    "EC",
    "Cambio_EC",
    "Volumen (L)",
    "Cambio_Volumen (L)",
    "Luces encendidas",
    "Cantidad luces",
    "Aire encendido",
    "Estado",
    "Ritmo",
    "Observaciones"
]

columnas_disponibles = [
    columna for columna in columnas
    if columna in datos.columns
]

matriz = datos[columnas_disponibles].copy()


# ============================================================
# 7. RESUMEN DE VARIABLES POR SECUENCIA
# ============================================================

resumen_variables = []

for secuencia, grupo in datos.groupby("Secuencia"):

    for variable in variables_numericas:

        if variable not in grupo.columns:
            continue

        valores = grupo[variable].dropna()

        resumen_variables.append({
            "Secuencia": secuencia,
            "Variable": variable,
            "N_registros": len(grupo),
            "N_disponibles": len(valores),
            "N_faltantes": grupo[variable].isna().sum(),
            "Media": valores.mean(),
            "Desviacion_estandar": valores.std(),
            "Minimo": valores.min(),
            "Maximo": valores.max()
        })

resumen_variables = pd.DataFrame(
    resumen_variables
)


# ============================================================
# 8. IDENTIFICAR MAYORES ERRORES
# ============================================================

mayores_errores = []

for secuencia, grupo in matriz.groupby("Secuencia"):

    for modelo, columna_error, columna_ranking in [
        (
            "Exponencial",
            "Error_abs_exp",
            "Ranking_error_exp"
        ),
        (
            "Baranyi",
            "Error_abs_baranyi",
            "Ranking_error_baranyi"
        )
    ]:

        seleccion = grupo[
            grupo[columna_ranking] <= 3
        ].copy()

        for _, fila in seleccion.iterrows():

            registro = fila.to_dict()

            registro["Modelo"] = modelo

            mayores_errores.append(registro)

mayores_errores = pd.DataFrame(
    mayores_errores
)


# ============================================================
# 9. EXPORTAR EXCEL
# ============================================================

with pd.ExcelWriter(SALIDA) as writer:

    matriz.to_excel(
        writer,
        sheet_name="Matriz_diagnostico",
        index=False
    )

    resumen_variables.to_excel(
        writer,
        sheet_name="Resumen_variables",
        index=False
    )

    mayores_errores.to_excel(
        writer,
        sheet_name="Mayores_errores",
        index=False
    )


# ============================================================
# 10. MOSTRAR RESULTADOS
# ============================================================

print("\n" + "=" * 70)
print("MATRIZ DE DIAGNOSTICO GENERADA")
print("=" * 70)

print("\nRegistros por secuencia:")

print(
    matriz.groupby("Secuencia").size().to_string()
)

print("\nDisponibilidad de variables:")

print(
    resumen_variables[
        [
            "Secuencia",
            "Variable",
            "N_disponibles",
            "N_faltantes"
        ]
    ].to_string(index=False)
)

print("\nMayores errores:")

print(
    mayores_errores[
        [
            "Secuencia",
            "Modelo",
            "Fecha",
            "Días cultivo",
            "OD",
            "Error_exponencial",
            "Error_baranyi",
            "pH",
            "Temperatura (°C)",
            "EC",
            "Volumen (L)",
            "Estado"
        ]
    ].to_string(index=False))

print("\nArchivo generado:")
print(SALIDA)

