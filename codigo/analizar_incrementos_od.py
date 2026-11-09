import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# 1. ARCHIVOS
# ============================================================

ARCHIVO_PRED = (
    "validacion_origen_movil/"
    "resultados_validacion_origen_movil.xlsx"
)

ARCHIVO_DATOS = "evaluacion_secuencias_final.xlsx"

CARPETA = "analisis_incrementos_od"

os.makedirs(CARPETA, exist_ok=True)
os.makedirs(os.path.join(CARPETA, "graficos"), exist_ok=True)

MODELOS = {
    "Exponencial": "OD_exponencial",
    "Logistico": "OD_logistico"
}

# ============================================================
# 2. CARGAR INFORMACIÓN
# ============================================================

print("Cargando predicciones y mediciones originales...")

pred = pd.read_excel(
    ARCHIVO_PRED,
    sheet_name="Predicciones"
)

detalle = pd.read_excel(
    ARCHIVO_DATOS,
    sheet_name="Detalle_OD"
)

pred["Fecha_real"] = pd.to_datetime(
    pred["Fecha_real"],
    errors="coerce"
)

detalle["Fecha"] = pd.to_datetime(
    detalle["Fecha"],
    errors="coerce"
)

detalle["OD"] = pd.to_numeric(
    detalle["OD"],
    errors="coerce"
)

detalle["Edad"] = pd.to_numeric(
    detalle["Edad"],
    errors="coerce"
)

# Excluir mediciones sin OD, sin edad y registros de descarte
detalle = detalle[
    detalle["OD"].notna()
    & detalle["Edad"].notna()
    & (detalle["OD"] > 0)
    & (detalle["Estado"] != "Descarte")
].copy()

detalle = detalle.sort_values(
    ["Secuencia", "Fecha", "Edad"]
).reset_index(drop=True)

# ============================================================
# 3. RECUPERAR LA MEDICIÓN ANTERIOR
# ============================================================

resultados = []

for _, fila in pred.iterrows():

    secuencia = fila["Secuencia"]

    grupo = detalle[
        detalle["Secuencia"] == secuencia
    ].copy()

    if grupo.empty:
        print("Secuencia no encontrada:", secuencia)
        continue

    # Buscar la observación que corresponde a la predicción
    coincidencias = grupo[
        np.isclose(
            grupo["OD"].astype(float),
            float(fila["OD_real"]),
            atol=0.00001
        )
    ].copy()

    if pd.notna(fila["Fecha_real"]):
        coincidencias_fecha = coincidencias[
            coincidencias["Fecha"] == fila["Fecha_real"]
        ]

        if not coincidencias_fecha.empty:
            coincidencias = coincidencias_fecha

    coincidencias_edad = coincidencias[
        np.isclose(
            coincidencias["Edad"].astype(float),
            float(fila["Edad_real"]),
            atol=0.00001
        )
    ]

    if not coincidencias_edad.empty:
        coincidencias = coincidencias_edad

    if coincidencias.empty:
        print(
            "No se encontró la medición objetivo:",
            secuencia,
            fila["Edad_real"],
            fila["OD_real"]
        )
        continue

    # Tomar la primera coincidencia cronológica
    objetivo = coincidencias.iloc[0]

    # Recuperar las mediciones anteriores a la fecha objetivo
    anteriores = grupo[
        grupo["Fecha"] < objetivo["Fecha"]
    ].copy()

    if anteriores.empty:
        print(
            "No existe medición anterior:",
            secuencia,
            fila["Edad_real"]
        )
        continue

    anterior = anteriores.iloc[-1]

    registro = {
        "Secuencia": secuencia,
        "Fecha_anterior": anterior["Fecha"],
        "Fecha_real": objetivo["Fecha"],
        "Edad_anterior": anterior["Edad"],
        "Edad_real": objetivo["Edad"],
        "OD_anterior": anterior["OD"],
        "OD_real": objetivo["OD"],
        "Cambio_edad": (
            objetivo["Edad"] - anterior["Edad"]
        ),
        "Dias_entre_mediciones": (
            objetivo["Fecha"] - anterior["Fecha"]
        ).days
    }

    # Cambio real de OD
    registro["Incremento_OD_real"] = (
        registro["OD_real"] - registro["OD_anterior"]
    )

    # Comparar los incrementos de cada modelo
    for nombre, columna in MODELOS.items():

        od_predicha = float(fila[columna])

        registro[f"OD_predicha_{nombre}"] = od_predicha

        registro[f"Incremento_predicho_{nombre}"] = (
            od_predicha - registro["OD_anterior"]
        )

        registro[f"Error_OD_{nombre}"] = (
            registro["OD_real"] - od_predicha
        )

        registro[f"Error_incremento_{nombre}"] = (
            registro["Incremento_OD_real"]
            - registro[f"Incremento_predicho_{nombre}"]
        )

        registro[f"Error_abs_incremento_{nombre}"] = abs(
            registro[f"Error_incremento_{nombre}"]
        )

    resultados.append(registro)

# ============================================================
# 4. CONSTRUIR TABLA DE RESULTADOS
# ============================================================

resultados = pd.DataFrame(resultados)

if resultados.empty:
    raise ValueError(
        "No se pudieron recuperar las mediciones anteriores. "
        "Revisar nombres de secuencias y columnas."
    )

# Clasificar cambio observado, sin atribuir fases biológicas
def clasificar_cambio(valor):

    if valor > 0.01:
        return "Aumento"

    if valor < -0.01:
        return "Descenso"

    return "Estabilidad aparente"


resultados["Comportamiento_real"] = (
    resultados["Incremento_OD_real"].apply(
        clasificar_cambio
    )
)

# ============================================================
# 5. RESUMEN DE ERRORES DE INCREMENTO
# ============================================================

resumen = []

for secuencia, grupo in resultados.groupby("Secuencia"):

    for nombre in MODELOS:

        errores = grupo[
            f"Error_incremento_{nombre}"
        ]

        resumen.append({
            "Secuencia": secuencia,
            "Modelo": nombre,
            "N": len(errores),
            "MAE_incremento": errores.abs().mean(),
            "RMSE_incremento": np.sqrt(
                np.mean(errores ** 2)
            ),
            "Sesgo_incremento": errores.mean()
        })

resumen = pd.DataFrame(resumen)

# Resumen según comportamiento real
resumen_comportamiento = []

for comportamiento, grupo in resultados.groupby(
    "Comportamiento_real"
):

    for nombre in MODELOS:

        errores = grupo[
            f"Error_incremento_{nombre}"
        ]

        resumen_comportamiento.append({
            "Comportamiento": comportamiento,
            "Modelo": nombre,
            "N": len(errores),
            "MAE_incremento": errores.abs().mean(),
            "RMSE_incremento": np.sqrt(
                np.mean(errores ** 2)
            )
        })

resumen_comportamiento = pd.DataFrame(
    resumen_comportamiento
)

# ============================================================
# 6. GRÁFICOS POR SECUENCIA
# ============================================================

for secuencia, grupo in resultados.groupby("Secuencia"):

    grupo = grupo.sort_values("Edad_real")

    plt.figure(figsize=(10, 5))

    x = np.arange(len(grupo))
    ancho = 0.25

    plt.bar(
        x - ancho,
        grupo["Incremento_OD_real"],
        width=ancho,
        label="Incremento real"
    )

    plt.bar(
        x,
        grupo["Incremento_predicho_Exponencial"],
        width=ancho,
        label="Incremento exponencial"
    )

    plt.bar(
        x + ancho,
        grupo["Incremento_predicho_Logistico"],
        width=ancho,
        label="Incremento logístico"
    )

    etiquetas = [
        str(int(edad))
        for edad in grupo["Edad_real"]
    ]

    plt.xticks(x, etiquetas)
    plt.xlabel("Edad del cultivo (días)")
    plt.ylabel("Cambio de OD")
    plt.title(f"Comparación de incrementos - {secuencia}")
    plt.axhline(0, linestyle="--")
    plt.grid(axis="y", alpha=0.3)
    plt.legend()
    plt.tight_layout()

    nombre = (
        secuencia.replace("/", "_").replace(" ", "_")
        + "_incrementos.png"
    )

    plt.savefig(
        os.path.join(CARPETA, "graficos", nombre),
        dpi=200
    )

    plt.close()

# ============================================================
# 7. EXPORTAR
# ============================================================

salida = os.path.join(
    CARPETA,
    "analisis_incrementos_od.xlsx"
)

with pd.ExcelWriter(
    salida,
    engine="openpyxl"
) as writer:

    resultados.to_excel(
        writer,
        sheet_name="Detalle_incrementos",
        index=False
    )

    resumen.to_excel(
        writer,
        sheet_name="Resumen_modelos",
        index=False
    )

    resumen_comportamiento.to_excel(
        writer,
        sheet_name="Por_comportamiento",
        index=False
    )

# ============================================================
# 8. MOSTRAR RESULTADOS
# ============================================================

print("\n========================================")
print("DETALLE DE INCREMENTOS")
print("========================================")

columnas = [
    "Secuencia",
    "Edad_anterior",
    "Edad_real",
    "OD_anterior",
    "OD_real",
    "Incremento_OD_real",
    "Incremento_predicho_Exponencial",
    "Incremento_predicho_Logistico",
    "Comportamiento_real"
]

print(
    resultados[columnas].round(5).to_string(index=False)
)

print("\n========================================")
print("ERROR DE LOS INCREMENTOS POR SECUENCIA")
print("========================================")

print(
    resumen.round(5).to_string(index=False)
)

print("\n========================================")
print("ERROR SEGÚN COMPORTAMIENTO")
print("========================================")

print(
    resumen_comportamiento.round(5).to_string(index=False)
)

print("\n========================================")
print("ARCHIVOS GENERADOS")
print("========================================")

print("Excel:", salida)
print("Gráficos:", os.path.join(CARPETA, "graficos"))
