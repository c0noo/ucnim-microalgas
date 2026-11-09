
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.optimize import least_squares


# ============================================================
# 1. CONFIGURACION
# ============================================================

ARCHIVO = "datos_procesados_corregidos.xlsx"

CARPETA_SALIDA = "ajustes_modelos_iniciales"

if not os.path.exists(CARPETA_SALIDA):
    os.makedirs(CARPETA_SALIDA)

SECUENCIAS = [
    "Planta__BIM-08_C12",
    "Planta__BIM-02_C04",
    "Planta__BIM-02_C01"
]


# ============================================================
# 2. CARGA Y PREPARACION DE DATOS
# ============================================================

base = pd.read_excel(ARCHIVO)

base["Ciclo_ID"] = base["Ciclo_ID"].astype(str)

base["Días cultivo"] = pd.to_numeric(
    base["Días cultivo"], errors="coerce"
)

base["OD"] = pd.to_numeric(
    base["OD"], errors="coerce"
)

resultados = []
datos_ajuste = []
diagnostico_descarte = []


# ============================================================
# 3. FUNCIONES DE LOS MODELOS
# ============================================================

def modelo_exponencial(t, log_x0, log_r):

    x0 = np.exp(log_x0)
    r = np.exp(log_r)

    return x0 * np.exp(r * t)


def modelo_baranyi(t, log_x0, log_mu, log_q0):

    x0 = np.exp(log_x0)
    mu = np.exp(log_mu)
    q0 = np.exp(log_q0)

    return x0 * (
        (1 + q0 * np.exp(mu * t)) / (1 + q0)
    )


# ============================================================
# 4. METRICAS DE AJUSTE
# ============================================================

def calcular_metricas(observado, estimado, k):

    n = len(observado)

    residuos = observado - estimado

    rss = np.sum(residuos ** 2)

    rmse = np.sqrt(rss / n)

    media = np.mean(observado)

    sst = np.sum((observado - media) ** 2)

    if sst > 0:
        r2 = 1 - rss / sst
    else:
        r2 = np.nan

    if rss > 0:
        aic = n * np.log(rss / n) + 2 * k
        aicc = aic + (2 * k * (k + 1)) / (n - k - 1)
    else:
        aicc = np.nan

    return rss, rmse, r2, aicc


# ============================================================
# 5. AJUSTE DEL MODELO EXPONENCIAL
# ============================================================

def ajustar_exponencial(t, y):

    def residuos(parametros):

        prediccion = modelo_exponencial(
            t, parametros[0], parametros[1]
        )

        return prediccion - y

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

    prediccion = modelo_exponencial(
        t, ajuste.x[0], ajuste.x[1]
    )

    return ajuste.x, prediccion


# ============================================================
# 6. AJUSTE DEL MODELO BARANYI SIMPLIFICADO
# ============================================================

def ajustar_baranyi(t, y):

    mejor_ajuste = None
    menor_rss = np.inf

    valores_iniciales_q = [
        0.01, 0.1, 1, 10, 100
    ]

    for q_inicial in valores_iniciales_q:

        def residuos(parametros):

            prediccion = modelo_baranyi(
                t,
                parametros[0],
                parametros[1],
                parametros[2]
            )

            return prediccion - y

        inicial = [
            np.log(y[0]),
            np.log(0.05),
            np.log(q_inicial)
        ]

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

        rss_actual = np.sum(ajuste.fun ** 2)

        if rss_actual < menor_rss:

            menor_rss = rss_actual
            mejor_ajuste = ajuste

    parametros = mejor_ajuste.x

    prediccion = modelo_baranyi(
        t,
        parametros[0],
        parametros[1],
        parametros[2]
    )

    return parametros, prediccion


# ============================================================
# 7. PROCESAMIENTO DE LAS SECUENCIAS
# ============================================================

for secuencia in SECUENCIAS:

    print("\n" + "=" * 70)
    print("SECUENCIA:", secuencia)
    print("=" * 70)

    datos = base[
        base["Ciclo_ID"] == secuencia
    ].copy()

    datos = datos.sort_values(
        ["Días cultivo", "Fecha"]
    )

    # Separar registros de descarte
    descarte = datos[
        datos["Estado"].astype(str).str.strip() == "Descarte"
    ].copy()

    # Excluir descarte del ajuste principal
    observaciones = datos[
        datos["Estado"].astype(str).str.strip() != "Descarte"
    ].copy()

    # Excluir registros sin OD o sin edad
    observaciones = observaciones.dropna(
        subset=["OD", "Días cultivo"]
    )

    # Excluir OD marcadas para revisión
    if "OD_Alta_Revisar" in observaciones.columns:

        observaciones = observaciones[
            observaciones["OD_Alta_Revisar"] != True
        ]

    observaciones = observaciones[
        (observaciones["OD"] > 0) &
        (observaciones["Días cultivo"] >= 0)
    ]

    observaciones = observaciones.sort_values(
        "Días cultivo"
    )

    print("Registros originales:", len(datos))
    print("Registros utilizados:", len(observaciones))
    print("Registros de descarte:", len(descarte))

    print("\nEstados originales:")

    print(datos["Estado"].value_counts(dropna=False))

    if len(observaciones) < 5:

        print("No hay suficientes observaciones para continuar.")
        continue

    # Tiempo relativo desde la primera edad observada
    edades = observaciones["Días cultivo"].to_numpy(
        dtype=float
    )

    od = observaciones["OD"].to_numpy(
        dtype=float
    )

    t = edades - edades.min()

    n = len(od)

    print("\nEdad inicial:", edades.min())
    print("Edad final:", edades.max())
    print("Observaciones OD:", n)

    # --------------------------------------------------------
    # MODELO EXPONENCIAL
    # --------------------------------------------------------

    parametros_exp, pred_exp = ajustar_exponencial(
        t, od
    )

    rss_exp, rmse_exp, r2_exp, aicc_exp = calcular_metricas(
        od, pred_exp, 2
    )

    x0_exp = np.exp(parametros_exp[0])
    r_exp = np.exp(parametros_exp[1])

    # --------------------------------------------------------
    # MODELO BARANYI
    # --------------------------------------------------------

    parametros_bar, pred_bar = ajustar_baranyi(
        t, od
    )

    rss_bar, rmse_bar, r2_bar, aicc_bar = calcular_metricas(
        od, pred_bar, 3
    )

    x0_bar = np.exp(parametros_bar[0])
    mu_bar = np.exp(parametros_bar[1])
    q0_bar = np.exp(parametros_bar[2])

    # --------------------------------------------------------
    # GUARDAR RESULTADOS
    # --------------------------------------------------------

    resultados.append({
        "Secuencia": secuencia,
        "N": n,
        "Edad_inicial": edades.min(),
        "Edad_final": edades.max(),
        "Modelo": "Exponencial",
        "X0": x0_exp,
        "r": r_exp,
        "RSS": rss_exp,
        "RMSE": rmse_exp,
        "R2": r2_exp,
        "AICc": aicc_exp
    })

    resultados.append({
        "Secuencia": secuencia,
        "N": n,
        "Edad_inicial": edades.min(),
        "Edad_final": edades.max(),
        "Modelo": "Baranyi simplificado",
        "X0": x0_bar,
        "r": np.nan,
        "mu_max": mu_bar,
        "q0": q0_bar,
        "RSS": rss_bar,
        "RMSE": rmse_bar,
        "R2": r2_bar,
        "AICc": aicc_bar
    })

    print("\nRESULTADOS EXPONENCIAL")
    print("X0:", x0_exp)
    print("r:", r_exp)
    print("RMSE:", rmse_exp)
    print("R2:", r2_exp)
    print("AICc:", aicc_exp)

    print("\nRESULTADOS BARANYI SIMPLIFICADO")
    print("X0:", x0_bar)
    print("mu_max:", mu_bar)
    print("q0:", q0_bar)
    print("RMSE:", rmse_bar)
    print("R2:", r2_bar)
    print("AICc:", aicc_bar)

    # --------------------------------------------------------
    # GUARDAR PREDICCIONES
    # --------------------------------------------------------

    for i in range(n):

        datos_ajuste.append({
            "Secuencia": secuencia,
            "Edad": edades[i],
            "OD_observada": od[i],
            "OD_exponencial": pred_exp[i],
            "OD_baranyi": pred_bar[i]
        })

    # --------------------------------------------------------
    # EVALUACION SEPARADA DE DESCARTE
    # --------------------------------------------------------

    if len(descarte) > 0:

        descarte = descarte.dropna(
            subset=["OD", "Días cultivo"]
        )

        for _, fila in descarte.iterrows():

            edad_descarte = float(fila["Días cultivo"])
            od_descarte = float(fila["OD"])

            t_descarte = edad_descarte - edades.min()

            pred_descarte_exp = modelo_exponencial(
                np.array([t_descarte]),
                parametros_exp[0],
                parametros_exp[1]
            )[0]

            pred_descarte_bar = modelo_baranyi(
                np.array([t_descarte]),
                parametros_bar[0],
                parametros_bar[1],
                parametros_bar[2]
            )[0]

            diagnostico_descarte.append({
                "Secuencia": secuencia,
                "Edad_descarte": edad_descarte,
                "OD_observada": od_descarte,
                "OD_exponencial": pred_descarte_exp,
                "OD_baranyi": pred_descarte_bar,
                "Dentro_intervalo_ajuste": (
                    edades.min() <= edad_descarte <= edades.max()
                )
            })

    # --------------------------------------------------------
    # GRAFICO
    # --------------------------------------------------------

    edades_grafico = np.linspace(
        edades.min(),
        edades.max(),
        200
    )

    t_grafico = edades_grafico - edades.min()

    curva_exp = modelo_exponencial(
        t_grafico,
        parametros_exp[0],
        parametros_exp[1]
    )

    curva_bar = modelo_baranyi(
        t_grafico,
        parametros_bar[0],
        parametros_bar[1],
        parametros_bar[2]
    )

    plt.figure(figsize=(10, 6))

    plt.scatter(
        edades,
        od,
        label="OD observada",
        s=55
    )

    plt.plot(
        edades_grafico,
        curva_exp,
        label="Modelo exponencial"
    )

    plt.plot(
        edades_grafico,
        curva_bar,
        label="Baranyi simplificado"
    )

    if len(descarte) > 0:

        descarte_grafico = descarte.dropna(
            subset=["OD", "Días cultivo"]
        )

        plt.scatter(
            descarte_grafico["Días cultivo"],
            descarte_grafico["OD"],
            marker="x",
            s=90,
            label="Registro de descarte"
        )

    plt.xlabel("Días de cultivo")
    plt.ylabel("Densidad óptica (OD)")

    plt.title(
        "Comparación de modelos - " + secuencia
    )

    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    nombre_grafico = secuencia.replace(
        "__", "_"
    ).replace(" ", "_")

    plt.savefig(
        os.path.join(
            CARPETA_SALIDA,
            nombre_grafico + ".png"
        ),
        dpi=300
    )

    plt.close()


# ============================================================
# 8. EXPORTACION DE RESULTADOS
# ============================================================

resultados_df = pd.DataFrame(resultados)

datos_df = pd.DataFrame(datos_ajuste)

descarte_df = pd.DataFrame(diagnostico_descarte)

archivo_salida = os.path.join(
    CARPETA_SALIDA,
    "comparacion_modelos_ode.xlsx"
)

with pd.ExcelWriter(archivo_salida) as writer:

    resultados_df.to_excel(
        writer,
        sheet_name="Metricas",
        index=False
    )

    datos_df.to_excel(
        writer,
        sheet_name="Predicciones",
        index=False
    )

    descarte_df.to_excel(
        writer,
        sheet_name="Descarte",
        index=False
    )

print("\n" + "=" * 70)
print("PROCESAMIENTO FINALIZADO")
print("=" * 70)

print("\nResumen de métricas:")

print(
    resultados_df[
        ["Secuencia", "Modelo", "N", "RMSE", "R2", "AICc"]
    ].to_string(index=False)
)

print("\nArchivo generado:")
print(archivo_salida)

print("\nGraficos guardados en:")
print(CARPETA_SALIDA)
