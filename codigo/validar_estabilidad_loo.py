
import os
import numpy as np
import pandas as pd

from scipy.optimize import least_squares


# ============================================================
# 1. CONFIGURACION
# ============================================================

ARCHIVO = "datos_procesados_corregidos.xlsx"

CARPETA = "validacion_loo"

if not os.path.exists(CARPETA):
    os.makedirs(CARPETA)

SECUENCIAS = [
    "Planta__BIM-08_C12",
    "Planta__BIM-02_C04",
    "Planta__BIM-02_C01"
]

INICIALES_Q0 = [
    0.0001,
    0.001,
    0.01,
    0.1,
    1,
    10,
    100,
    10000
]


# ============================================================
# 2. FUNCIONES DE LOS MODELOS
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
# 3. AJUSTE EXPONENCIAL
# ============================================================

def ajustar_exponencial(t, y):

    def residuos(parametros):

        prediccion = modelo_exponencial(
            t, parametros
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

    return ajuste.x


# ============================================================
# 4. AJUSTE BARANYI CON MULTIPLES INICIOS
# ============================================================

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

            prediccion = modelo_baranyi(
                t, parametros
            )

            return prediccion - y

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
# 5. CARGA DE DATOS
# ============================================================

base = pd.read_excel(ARCHIVO)

base["Ciclo_ID"] = base["Ciclo_ID"].astype(str)

base["OD"] = pd.to_numeric(
    base["OD"], errors="coerce"
)

base["Días cultivo"] = pd.to_numeric(
    base["Días cultivo"], errors="coerce"
)

resultados_loo = []
resumen = []
parametros_completos = []


# ============================================================
# 6. PROCESAMIENTO DE CADA SECUENCIA
# ============================================================

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
    )

    edades = datos["Días cultivo"].to_numpy(
        dtype=float
    )

    od = datos["OD"].to_numpy(
        dtype=float
    )

    n = len(od)

    if n < 6:

        print("No hay suficientes observaciones.")
        continue

    # Mantener el mismo origen temporal en todos los ajustes
    edad_inicial = edades.min()

    t = edades - edad_inicial

    # --------------------------------------------------------
    # AJUSTE CON TODOS LOS DATOS
    # --------------------------------------------------------

    parametros_exp = ajustar_exponencial(t, od)

    parametros_bar = ajustar_baranyi(t, od)

    pred_exp = modelo_exponencial(
        t, parametros_exp
    )

    pred_bar = modelo_baranyi(
        t, parametros_bar
    )

    x0_exp = np.exp(parametros_exp[0])
    r_exp = np.exp(parametros_exp[1])

    x0_bar = np.exp(parametros_bar[0])
    mu_bar = np.exp(parametros_bar[1])
    q0_bar = np.exp(parametros_bar[2])

    lag_bar = np.log(1 + 1 / q0_bar) / mu_bar

    parametros_completos.append({
        "Secuencia": secuencia,
        "Modelo": "Exponencial",
        "X0": x0_exp,
        "r": r_exp
    })

    parametros_completos.append({
        "Secuencia": secuencia,
        "Modelo": "Baranyi",
        "X0": x0_bar,
        "mu_max": mu_bar,
        "q0": q0_bar,
        "alpha_inicial": q0_bar / (1 + q0_bar),
        "lag_dias": lag_bar
    })

    print("\nParametros con todos los datos:")
    print("Exponencial X0:", x0_exp)
    print("Exponencial r:", r_exp)
    print("Baranyi X0:", x0_bar)
    print("Baranyi mu_max:", mu_bar)
    print("Baranyi q0:", q0_bar)
    print("Baranyi lag:", lag_bar)

    # --------------------------------------------------------
    # VALIDACION LEAVE-ONE-OUT
    # --------------------------------------------------------

    predicciones_exp = []
    predicciones_bar = []

    for i in range(n):

        indices_entrenamiento = np.arange(n) != i

        t_entrenamiento = t[indices_entrenamiento]
        y_entrenamiento = od[indices_entrenamiento]

        t_prueba = np.array([t[i]])

        # Ajuste exponencial sin la observacion i
        parametros_exp_loo = ajustar_exponencial(
            t_entrenamiento,
            y_entrenamiento
        )

        pred_exp_i = modelo_exponencial(
            t_prueba,
            parametros_exp_loo
        )[0]

        # Ajuste Baranyi sin la observacion i
        parametros_bar_loo = ajustar_baranyi(
            t_entrenamiento,
            y_entrenamiento
        )

        pred_bar_i = modelo_baranyi(
            t_prueba,
            parametros_bar_loo
        )[0]

        # Parametros de Baranyi
        x0_loo = np.exp(parametros_bar_loo[0])
        mu_loo = np.exp(parametros_bar_loo[1])
        q0_loo = np.exp(parametros_bar_loo[2])

        lag_loo = np.log(1 + 1 / q0_loo) / mu_loo

        alpha_loo = q0_loo / (1 + q0_loo)

        # Identificar proximidad a limites numericos
        q0_en_limite = (
            q0_loo < 1.1e-6 or
            q0_loo > 9e5
        )

        resultados_loo.append({
            "Secuencia": secuencia,
            "Registro_retirado": i + 1,
            "Edad_retirada": edades[i],
            "OD_observada": od[i],
            "OD_predicha_exponencial": pred_exp_i,
            "OD_predicha_baranyi": pred_bar_i,
            "Error_exponencial": od[i] - pred_exp_i,
            "Error_baranyi": od[i] - pred_bar_i,
            "X0_baranyi": x0_loo,
            "mu_max_baranyi": mu_loo,
            "q0_baranyi": q0_loo,
            "alpha_inicial": alpha_loo,
            "lag_dias": lag_loo,
            "q0_cerca_limite": q0_en_limite
        })

        predicciones_exp.append(pred_exp_i)
        predicciones_bar.append(pred_bar_i)

    # --------------------------------------------------------
    # METRICAS LOO
    # --------------------------------------------------------

    predicciones_exp = np.array(predicciones_exp)
    predicciones_bar = np.array(predicciones_bar)

    errores_exp = od - predicciones_exp
    errores_bar = od - predicciones_bar

    rmse_exp_loo = np.sqrt(
        np.mean(errores_exp ** 2)
    )

    rmse_bar_loo = np.sqrt(
        np.mean(errores_bar ** 2)
    )

    mae_exp_loo = np.mean(
        np.abs(errores_exp)
    )

    mae_bar_loo = np.mean(
        np.abs(errores_bar)
    )

    tabla_loo = pd.DataFrame([
        fila for fila in resultados_loo
        if fila["Secuencia"] == secuencia
    ])

    resumen.append({
        "Secuencia": secuencia,
        "N": n,
        "RMSE_LOO_exponencial": rmse_exp_loo,
        "RMSE_LOO_baranyi": rmse_bar_loo,
        "MAE_LOO_exponencial": mae_exp_loo,
        "MAE_LOO_baranyi": mae_bar_loo,
        "q0_minimo_LOO": tabla_loo["q0_baranyi"].min(),
        "q0_maximo_LOO": tabla_loo["q0_baranyi"].max(),
        "mu_minimo_LOO": tabla_loo["mu_max_baranyi"].min(),
        "mu_maximo_LOO": tabla_loo["mu_max_baranyi"].max(),
        "lag_minimo_LOO": tabla_loo["lag_dias"].min(),
        "lag_maximo_LOO": tabla_loo["lag_dias"].max(),
        "ajustes_q0_cerca_limite": int(
            tabla_loo["q0_cerca_limite"].sum()
        )
    })

    print("\nRESULTADOS LOO")
    print("RMSE exponencial:", rmse_exp_loo)
    print("RMSE Baranyi:", rmse_bar_loo)
    print("MAE exponencial:", mae_exp_loo)
    print("MAE Baranyi:", mae_bar_loo)

    print("\nRango q0:", tabla_loo["q0_baranyi"].min(),
          "a", tabla_loo["q0_baranyi"].max())

    print("Rango mu_max:", tabla_loo["mu_max_baranyi"].min(),
          "a", tabla_loo["mu_max_baranyi"].max())

    print("Rango lag:", tabla_loo["lag_dias"].min(),
          "a", tabla_loo["lag_dias"].max())

    print(
        "Ajustes con q0 cercano a un limite:",
        tabla_loo["q0_cerca_limite"].sum(),
        "de",
        n
    )


# ============================================================
# 7. EXPORTAR RESULTADOS
# ============================================================

loo_df = pd.DataFrame(resultados_loo)

resumen_df = pd.DataFrame(resumen)

parametros_df = pd.DataFrame(parametros_completos)

archivo_salida = os.path.join(
    CARPETA,
    "resultados_validacion_loo.xlsx"
)

with pd.ExcelWriter(archivo_salida) as writer:

    resumen_df.to_excel(
        writer,
        sheet_name="Resumen",
        index=False
    )

    loo_df.to_excel(
        writer,
        sheet_name="Detalle_LOO",
        index=False
    )

    parametros_df.to_excel(
        writer,
        sheet_name="Parametros_completos",
        index=False
    )


# ============================================================
# 8. RESULTADO FINAL
# ============================================================

print("\n" + "=" * 70)
print("VALIDACION LOO FINALIZADA")
print("=" * 70)

print("\nResumen:")

print(
    resumen_df.to_string(index=False)
)

print("\nArchivo generado:")
print(archivo_salida)
