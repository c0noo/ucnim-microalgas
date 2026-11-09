
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.optimize import least_squares


# ============================================================
# 1. CONFIGURACION
# ============================================================

ARCHIVO_DATOS = "datos_procesados_corregidos.xlsx"

ARCHIVO_LOO = (
    "validacion_loo/resultados_validacion_loo.xlsx"
)

CARPETA = "analisis_residuos_loo"

os.makedirs(CARPETA, exist_ok=True)

SECUENCIAS = [
    "Planta__BIM-08_C12",
    "Planta__BIM-02_C04",
    "Planta__BIM-02_C01"
]

INICIALES_Q0 = [
    0.0001, 0.001, 0.01, 0.1,
    1, 10, 100, 10000
]


# ============================================================
# 2. MODELOS
# ============================================================

def modelo_exponencial(t, parametros):

    x0 = np.exp(parametros[0])
    r = np.exp(parametros[1])

    return x0 * np.exp(r * t)


def modelo_baranyi(t, parametros):

    x0 = np.exp(parametros[0])
    mu = np.exp(parametros[1])
    q0 = np.exp(parametros[2])

    return x0 * (
        (1 + q0 * np.exp(mu * t)) / (1 + q0)
    )


# ============================================================
# 3. AJUSTES CON TODOS LOS DATOS
# ============================================================

def ajustar_exponencial(t, y):

    def residuos(parametros):

        return modelo_exponencial(t, parametros) - y

    inicial = [
        np.log(y[0]),
        np.log(0.05)
    ]

    ajuste = least_squares(
        residuos,
        inicial,
        bounds=(
            [np.log(0.001), np.log(0.00001)],
            [np.log(10), np.log(0.5)]
        ),
        max_nfev=20000
    )

    return ajuste.x


def ajustar_baranyi(t, y):

    mejor_ajuste = None
    menor_rss = np.inf

    for q_inicial in INICIALES_Q0:

        inicial = [
            np.log(y[0]),
            np.log(0.05),
            np.log(q_inicial)
        ]

        def residuos(parametros):

            return modelo_baranyi(t, parametros) - y

        ajuste = least_squares(
            residuos,
            inicial,
            bounds=(
                [
                    np.log(0.001),
                    np.log(0.00001),
                    np.log(0.000001)
                ],
                [
                    np.log(10),
                    np.log(0.5),
                    np.log(1000000)
                ]
            ),
            max_nfev=30000
        )

        rss = np.sum(ajuste.fun ** 2)

        if rss < menor_rss:

            menor_rss = rss
            mejor_ajuste = ajuste

    return mejor_ajuste.x


# ============================================================
# 4. CARGAR RESULTADOS LOO
# ============================================================

base = pd.read_excel(ARCHIVO_DATOS)

loo = pd.read_excel(
    ARCHIVO_LOO,
    sheet_name="Detalle_LOO"
)

base["Ciclo_ID"] = base["Ciclo_ID"].astype(str)

base["OD"] = pd.to_numeric(
    base["OD"], errors="coerce"
)

base["Días cultivo"] = pd.to_numeric(
    base["Días cultivo"], errors="coerce"
)

base["Fecha"] = pd.to_datetime(
    base["Fecha"], errors="coerce"
)


# ============================================================
# 5. ANALISIS POR SECUENCIA
# ============================================================

detalles = []
metricas = []
resumen_errores = []

for secuencia in SECUENCIAS:

    print("\n" + "=" * 70)
    print("SECUENCIA:", secuencia)
    print("=" * 70)

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

    datos = datos.sort_values(
        ["Días cultivo", "Fecha"]
    ).reset_index(drop=True)

    datos["Registro_retirado"] = (
        np.arange(len(datos)) + 1
    )

    edades = datos["Días cultivo"].to_numpy(
        dtype=float
    )

    od = datos["OD"].to_numpy(
        dtype=float
    )

    n = len(datos)

    if n < 6:

        print("Secuencia omitida: pocos registros.")
        continue

    t = edades - edades.min()

    # --------------------------------------------------------
    # AJUSTE COMPLETO
    # --------------------------------------------------------

    parametros_exp = ajustar_exponencial(t, od)
    parametros_bar = ajustar_baranyi(t, od)

    pred_exp = modelo_exponencial(
        t, parametros_exp
    )

    pred_bar = modelo_baranyi(
        t, parametros_bar
    )

    residuos_exp = od - pred_exp
    residuos_bar = od - pred_bar

    # --------------------------------------------------------
    # RECUPERAR PREDICCIONES LOO
    # --------------------------------------------------------

    loo_seq = loo[
        loo["Secuencia"] == secuencia
    ].copy()

    datos = datos.merge(
    loo_seq,
    on="Registro_retirado",
    how="left")

    # Errores con signo:
    # positivo = modelo subestima OD
    # negativo = modelo sobreestima OD

    datos["Residuo_completo_exp"] = residuos_exp
    datos["Residuo_completo_bar"] = residuos_bar

    datos["Error_absoluto_LOO_exp"] = (
        datos["Error_exponencial"].abs()
    )

    datos["Error_absoluto_LOO_bar"] = (
        datos["Error_baranyi"].abs()
    )

    datos["Modelo_LOO_mejor"] = np.where(
        datos["Error_absoluto_LOO_exp"] <
        datos["Error_absoluto_LOO_bar"],
        "Exponencial",
        np.where(
            datos["Error_absoluto_LOO_exp"] >
            datos["Error_absoluto_LOO_bar"],
            "Baranyi",
            "Empate"
        )
    )

    detalles.append(datos)

    # --------------------------------------------------------
    # METRICAS DE RESIDUOS
    # --------------------------------------------------------

    for modelo, residuo_completo, error_loo in [
        (
            "Exponencial",
            residuos_exp,
            datos["Error_exponencial"].to_numpy()
        ),
        (
            "Baranyi",
            residuos_bar,
            datos["Error_baranyi"].to_numpy()
        )
    ]:

        metricas.append({
            "Secuencia": secuencia,
            "Modelo": modelo,
            "RMSE_ajuste": np.sqrt(
                np.mean(residuo_completo ** 2)
            ),
            "Sesgo_ajuste": np.mean(
                residuo_completo
            ),
            "RMSE_LOO": np.sqrt(
                np.mean(error_loo ** 2)
            ),
            "MAE_LOO": np.mean(
                np.abs(error_loo)
            ),
            "Error_LOO_maximo": np.max(
                np.abs(error_loo)
            ),
            "Observaciones_LOO_subestimadas": int(
                np.sum(error_loo > 0)
            ),
            "Observaciones_LOO_sobreestimadas": int(
                np.sum(error_loo < 0)
            )
        })

    # --------------------------------------------------------
    # IDENTIFICAR MAYORES ERRORES
    # --------------------------------------------------------

    for modelo, columna in [
        ("Exponencial", "Error_absoluto_LOO_exp"),
        ("Baranyi", "Error_absoluto_LOO_bar")
    ]:

        mayores = datos.nlargest(
            3, columna
        )

        for _, fila in mayores.iterrows():

            resumen_errores.append({
                "Secuencia": secuencia,
                "Modelo": modelo,
                "Fecha": fila["Fecha"],
                "Edad": fila["Días cultivo"],
                "OD_observada": fila["OD"],
                "OD_predicha": (
                    fila["OD_predicha_exponencial"]
                    if modelo == "Exponencial"
                    else fila["OD_predicha_baranyi"]
                ),
                "Error_LOO": (
                    fila["Error_exponencial"]
                    if modelo == "Exponencial"
                    else fila["Error_baranyi"]
                ),
                "Estado": fila["Estado"],
                "Observaciones": fila.get(
                    "Observaciones", ""
                )
            })

    # --------------------------------------------------------
    # GRAFICO 1: OBSERVADO Y PREDICCIONES
    # --------------------------------------------------------

    plt.figure(figsize=(10, 6))

    plt.scatter(
        edades, od,
        label="OD observada",
        color="black",
        zorder=5
    )

    plt.plot(
        edades, pred_exp,
        marker="o",
        label="Exponencial: ajuste completo"
    )

    plt.plot(
        edades, pred_bar,
        marker="s",
        label="Baranyi: ajuste completo"
    )

    plt.scatter(
        edades,
        datos["OD_predicha_exponencial"],
        marker="x",
        s=65,
        label="Exponencial: predicción LOO"
    )

    plt.scatter(
        edades,
        datos["OD_predicha_baranyi"],
        marker="^",
        s=55,
        label="Baranyi: predicción LOO"
    )

    plt.xlabel("Días de cultivo")
    plt.ylabel("Densidad óptica (OD)")
    plt.title(
        "Observaciones y predicciones - " + secuencia
    )

    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            CARPETA,
            secuencia + "_predicciones.png"
        ),
        dpi=200
    )

    plt.close()

    # --------------------------------------------------------
    # GRAFICO 2: ERRORES LOO
    # --------------------------------------------------------

    plt.figure(figsize=(10, 5))

    plt.axhline(
        0,
        linestyle="--",
        linewidth=1
    )

    plt.plot(
        edades,
        datos["Error_exponencial"],
        marker="o",
        label="Exponencial"
    )

    plt.plot(
        edades,
        datos["Error_baranyi"],
        marker="s",
        label="Baranyi"
    )

    plt.xlabel("Días de cultivo")
    plt.ylabel("Residuo LOO (OD observada - predicha)")
    plt.title(
        "Errores de predicción LOO - " + secuencia
    )

    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            CARPETA,
            secuencia + "_errores_loo.png"
        ),
        dpi=200
    )

    plt.close()

    print("\nMayores errores absolutos LOO:")

    print(
        datos[
            [
                "Fecha",
                "Días cultivo",
                "OD",
                "Error_exponencial",
                "Error_baranyi",
                "Estado"
            ]
        ].assign(
            Error_exp_abs=lambda x:
            x["Error_exponencial"].abs(),
            Error_bar_abs=lambda x:
            x["Error_baranyi"].abs()
        ).sort_values(
            "Error_exp_abs",
            ascending=False
        ).head(3).to_string(index=False)
    )


# ============================================================
# 6. EXPORTAR EXCEL
# ============================================================

detalle_df = pd.concat(
    detalles,
    ignore_index=True
)

metricas_df = pd.DataFrame(metricas)

mayores_df = pd.DataFrame(resumen_errores)

archivo_salida = os.path.join(
    CARPETA,
    "analisis_residuos_y_predicciones.xlsx"
)

with pd.ExcelWriter(archivo_salida) as writer:

    metricas_df.to_excel(
        writer,
        sheet_name="Metricas",
        index=False
    )

    detalle_df.to_excel(
        writer,
        sheet_name="Detalle_observaciones",
        index=False
    )

    mayores_df.to_excel(
        writer,
        sheet_name="Mayores_errores",
        index=False
    )


# ============================================================
# 7. RESUMEN FINAL
# ============================================================

print("\n" + "=" * 70)
print("ANALISIS DE RESIDUOS FINALIZADO")
print("=" * 70)

print("\nMetricas:")

print(
    metricas_df.to_string(index=False)
)

print("\nMayores errores:")

print(
    mayores_df.to_string(index=False)
)

print("\nArchivo generado:")
print(archivo_salida)

print("\nGraficos guardados en:")
print(CARPETA)
