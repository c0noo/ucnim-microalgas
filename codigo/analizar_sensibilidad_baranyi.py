
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.optimize import least_squares


# ============================================================
# 1. CONFIGURACION
# ============================================================

ARCHIVO = "datos_procesados_corregidos.xlsx"

CARPETA = "sensibilidad_baranyi"

if not os.path.exists(CARPETA):
    os.makedirs(CARPETA)

SECUENCIAS = [
    "Planta__BIM-08_C12",
    "Planta__BIM-02_C04",
    "Planta__BIM-02_C01"
]

# Valores de q0 que se evaluaran
VALORES_Q0 = np.logspace(-4, 6, 80)


# ============================================================
# 2. CARGA DE DATOS
# ============================================================

base = pd.read_excel(ARCHIVO)

base["Ciclo_ID"] = base["Ciclo_ID"].astype(str)

base["OD"] = pd.to_numeric(
    base["OD"], errors="coerce"
)

base["Días cultivo"] = pd.to_numeric(
    base["Días cultivo"], errors="coerce"
)

resultados = []


# ============================================================
# 3. MODELO BARANYI CON q0 FIJO
# ============================================================

def modelo_baranyi(t, log_x0, log_mu, q0):

    x0 = np.exp(log_x0)
    mu = np.exp(log_mu)

    return x0 * (
        (1 + q0 * np.exp(mu * t)) / (1 + q0)
    )


# ============================================================
# 4. ANALISIS POR SECUENCIA
# ============================================================

for secuencia in SECUENCIAS:

    print("\n" + "=" * 65)
    print("SECUENCIA:", secuencia)
    print("=" * 65)

    datos = base[
        base["Ciclo_ID"] == secuencia
    ].copy()

    datos = datos[
        datos["Estado"].astype(str).str.strip() != "Descarte"
    ]

    datos = datos.dropna(
        subset=["OD", "Días cultivo"]
    )

    if "OD_Alta_Revisar" in datos.columns:

        datos = datos[
            datos["OD_Alta_Revisar"] != True
        ]

    datos = datos[
        (datos["OD"] > 0) &
        (datos["Días cultivo"] >= 0)
    ]

    datos = datos.sort_values("Días cultivo")

    edades = datos["Días cultivo"].to_numpy(dtype=float)
    od = datos["OD"].to_numpy(dtype=float)

    if len(od) < 5:
        print("Datos insuficientes.")
        continue

    t = edades - edades.min()

    n = len(od)

    resultados_secuencia = []

    # --------------------------------------------------------
    # EVALUAR LOS DISTINTOS VALORES DE q0
    # --------------------------------------------------------

    for q0 in VALORES_Q0:

        def residuos(parametros):

            prediccion = modelo_baranyi(
                t,
                parametros[0],
                parametros[1],
                q0
            )

            return prediccion - od

        inicial = [
            np.log(od[0]),
            np.log(0.05)
        ]

        ajuste = least_squares(
            residuos,
            inicial,
            bounds=(
                [
                    np.log(0.001),
                    np.log(0.00001)
                ],
                [
                    np.log(10),
                    np.log(0.5)
                ]
            ),
            max_nfev=20000
        )

        prediccion = modelo_baranyi(
            t,
            ajuste.x[0],
            ajuste.x[1],
            q0
        )

        rss = np.sum((od - prediccion) ** 2)

        rmse = np.sqrt(rss / n)

        x0 = np.exp(ajuste.x[0])
        mu = np.exp(ajuste.x[1])

        alpha0 = q0 / (1 + q0)

        # Tiempo de adaptación teórico del modelo
        lag = np.log(1 + 1 / q0) / mu

        fila = {
            "Secuencia": secuencia,
            "q0": q0,
            "X0": x0,
            "mu_max": mu,
            "alpha_inicial": alpha0,
            "lag_estimado_dias": lag,
            "RSS": rss,
            "RMSE": rmse
        }

        resultados_secuencia.append(fila)
        resultados.append(fila)

    tabla = pd.DataFrame(resultados_secuencia)

    # --------------------------------------------------------
    # IDENTIFICAR EL MEJOR VALOR DEL PERFIL
    # --------------------------------------------------------

    mejor = tabla.loc[tabla["RMSE"].idxmin()]

    rmse_minimo = mejor["RMSE"]

    tabla["Diferencia_RMSE"] = (
        tabla["RMSE"] - rmse_minimo
    )

    print("\nMejor ajuste del perfil:")

    print(mejor.to_string())

    # Valores de q0 con RMSE cercano al minimo
    tabla["Dentro_1_por_ciento"] = (
        tabla["RMSE"] <= rmse_minimo * 1.01
    )

    cantidad_cercana = tabla[
        "Dentro_1_por_ciento"
    ].sum()

    print(
        "\nValores de q0 dentro del 1% del RMSE minimo:",
        cantidad_cercana,
        "de",
        len(tabla)
    )

    # --------------------------------------------------------
    # GRAFICO DEL PERFIL
    # --------------------------------------------------------

    plt.figure(figsize=(9, 5))

    plt.plot(
        tabla["q0"],
        tabla["RMSE"],
        marker="o",
        markersize=3
    )

    plt.axhline(
        rmse_minimo * 1.01,
        linestyle="--",
        label="RMSE minimo + 1%"
    )

    plt.xscale("log")

    plt.xlabel("q0")
    plt.ylabel("RMSE")

    plt.title(
        "Sensibilidad de q0 - " + secuencia
    )

    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    nombre = secuencia.replace(
        "__", "_"
    ).replace(" ", "_")

    plt.savefig(
        os.path.join(
            CARPETA,
            nombre + "_perfil_q0.png"
        ),
        dpi=300
    )

    plt.close()


# ============================================================
# 5. EXPORTAR RESULTADOS
# ============================================================

resultados_df = pd.DataFrame(resultados)

archivo_salida = os.path.join(
    CARPETA,
    "sensibilidad_parametro_q0.xlsx"
)

resultados_df.to_excel(
    archivo_salida,
    index=False
)

print("\n" + "=" * 65)
print("ANALISIS FINALIZADO")
print("=" * 65)

print("\nArchivo generado:")
print(archivo_salida)

print("\nGraficos guardados en:")
print(CARPETA)
