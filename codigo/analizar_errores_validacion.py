import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

ARCHIVO = (
    "validacion_origen_movil/"
    "resultados_validacion_origen_movil.xlsx"
)

CARPETA = "analisis_errores_validacion"

os.makedirs(CARPETA, exist_ok=True)
os.makedirs(os.path.join(CARPETA, "graficos"), exist_ok=True)

MODELOS = {
    "Referencia": "OD_referencia",
    "Exponencial": "OD_exponencial",
    "Logistico": "OD_logistico"
}

# ============================================================
# 2. CARGAR PREDICCIONES
# ============================================================

print("Cargando predicciones...")

datos = pd.read_excel(
    ARCHIVO,
    sheet_name="Predicciones"
)

datos["Fecha_real"] = pd.to_datetime(
    datos["Fecha_real"],
    errors="coerce"
)

datos = datos.sort_values(
    ["Secuencia", "Edad_real"]
).reset_index(drop=True)

# ============================================================
# 3. CALCULAR CAMBIOS REALES DE OD
# ============================================================

datos["OD_anterior"] = (
    datos.groupby("Secuencia")["OD_real"].shift(1)
)

datos["Cambio_OD_real"] = (
    datos["OD_real"] - datos["OD_anterior"]
)

def clasificar_comportamiento(cambio):

    if pd.isna(cambio):
        return "Sin referencia anterior"

    if cambio > 0.01:
        return "Aumento"

    if cambio < -0.01:
        return "Descenso"

    return "Estabilidad aparente"


datos["Comportamiento"] = datos[
    "Cambio_OD_real"
].apply(clasificar_comportamiento)

# ============================================================
# 4. CALCULAR ERRORES
# ============================================================

for nombre, columna in MODELOS.items():

    datos[f"Error_{nombre}"] = (
        datos["OD_real"] - datos[columna]
    )

    datos[f"ErrorAbs_{nombre}"] = (
        datos[f"Error_{nombre}"].abs()
    )

    datos[f"ErrorPorcentual_{nombre}"] = (
        datos[f"ErrorAbs_{nombre}"] /
        datos["OD_real"].abs() * 100
    )

# ============================================================
# 5. RESUMEN POR MODELO Y SECUENCIA
# ============================================================

resumen_modelos = []

for secuencia, grupo in datos.groupby("Secuencia"):

    for nombre, columna in MODELOS.items():

        validos = grupo[
            grupo[columna].notna()
        ].copy()

        if validos.empty:
            continue

        errores = validos[f"Error_{nombre}"]

        resumen_modelos.append({
            "Secuencia": secuencia,
            "Modelo": nombre,
            "N_predicciones": len(validos),
            "Error_medio": errores.mean(),
            "Error_absoluto_medio": errores.abs().mean(),
            "Error_maximo_absoluto": errores.abs().max(),
            "Error_porcentual_medio": (
                validos[f"ErrorPorcentual_{nombre}"].mean()
            )
        })

resumen_modelos = pd.DataFrame(resumen_modelos)

# ============================================================
# 6. ERROR SEGÚN COMPORTAMIENTO REAL
# ============================================================

resumen_comportamiento = []

for comportamiento, grupo in datos.groupby("Comportamiento"):

    for nombre, columna in MODELOS.items():

        validos = grupo[
            grupo[columna].notna()
        ]

        if validos.empty:
            continue

        resumen_comportamiento.append({
            "Comportamiento": comportamiento,
            "Modelo": nombre,
            "N_predicciones": len(validos),
            "MAE": validos[f"ErrorAbs_{nombre}"].mean(),
            "RMSE": np.sqrt(
                np.mean(validos[f"Error_{nombre}"] ** 2)
            ),
            "Sesgo": validos[f"Error_{nombre}"].mean()
        })

resumen_comportamiento = pd.DataFrame(
    resumen_comportamiento
)

# ============================================================
# 7. GRÁFICO DE OD REAL Y PREDICHA
# ============================================================

print("Generando gráficos...")

for secuencia, grupo in datos.groupby("Secuencia"):

    plt.figure(figsize=(11, 6))

    plt.plot(
        grupo["Edad_real"],
        grupo["OD_real"],
        marker="o",
        linewidth=2,
        label="OD real"
    )

    for nombre, columna in MODELOS.items():

        plt.plot(
            grupo["Edad_real"],
            grupo[columna],
            marker="s",
            linestyle="--",
            label=f"Predicción {nombre}"
        )

    plt.xlabel("Días de cultivo")
    plt.ylabel("Densidad óptica (OD)")
    plt.title(f"OD real vs predicha - {secuencia}")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()

    archivo = (
        secuencia.replace("/", "_").replace(" ", "_")
        + "_comparacion.png"
    )

    plt.savefig(
        os.path.join(CARPETA, "graficos", archivo),
        dpi=200
    )

    plt.close()

# ============================================================
# 8. GRÁFICO DE RESIDUOS
# ============================================================

for nombre in ["Exponencial", "Logistico"]:

    plt.figure(figsize=(10, 5))

    for secuencia, grupo in datos.groupby("Secuencia"):

        plt.scatter(
            grupo["OD_real"],
            grupo[f"Error_{nombre}"],
            label=secuencia,
            s=55
        )

    plt.axhline(
        0,
        linestyle="--"
    )

    plt.xlabel("OD real")
    plt.ylabel("Residuo (OD real - OD predicha)")
    plt.title(f"Análisis de residuos - Modelo {nombre}")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            CARPETA,
            "graficos",
            f"residuos_{nombre.lower()}.png"
        ),
        dpi=200
    )

    plt.close()

# ============================================================
# 9. GRÁFICO DEL ERROR ABSOLUTO
# ============================================================

plt.figure(figsize=(11, 6))

for nombre in MODELOS:

    plt.plot(
        datos["Edad_real"],
        datos[f"ErrorAbs_{nombre}"],
        marker="o",
        linestyle="-",
        label=nombre
    )

plt.xlabel("Días de cultivo")
plt.ylabel("Error absoluto (OD)")
plt.title("Error absoluto por edad del cultivo")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    os.path.join(
        CARPETA,
        "graficos",
        "error_absoluto_por_edad.png"
    ),
    dpi=200
)

plt.close()

# ============================================================
# 10. EXPORTAR RESULTADOS
# ============================================================

salida = os.path.join(
    CARPETA,
    "analisis_errores_validacion.xlsx"
)

with pd.ExcelWriter(
    salida,
    engine="openpyxl"
) as writer:

    datos.to_excel(
        writer,
        sheet_name="Detalle_errores",
        index=False
    )

    resumen_modelos.to_excel(
        writer,
        sheet_name="Resumen_modelos",
        index=False
    )

    resumen_comportamiento.to_excel(
        writer,
        sheet_name="Error_comportamiento",
        index=False
    )

# ============================================================
# 11. MOSTRAR RESULTADOS
# ============================================================

print("\n========================================")
print("RESUMEN POR SECUENCIA Y MODELO")
print("========================================")

print(
    resumen_modelos.round(5).to_string(index=False)
)

print("\n========================================")
print("ERROR SEGÚN COMPORTAMIENTO")
print("========================================")

print(
    resumen_comportamiento.round(5).to_string(index=False)
)

print("\n========================================")
print("PREDICCIONES Y CAMBIOS DE OD")
print("========================================")

columnas = [
    "Secuencia",
    "Edad_real",
    "OD_real",
    "Cambio_OD_real",
    "Comportamiento",
    "Error_Exponencial",
    "Error_Logistico"
]

print(
    datos[columnas].round(5).to_string(index=False)
)

print("\n========================================")
print("PROCESO FINALIZADO")
print("========================================")

print("Excel:", salida)
print("Gráficos:", os.path.join(CARPETA, "graficos"))

