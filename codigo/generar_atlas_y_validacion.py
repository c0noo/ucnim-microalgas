import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit
from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings("ignore")

# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

ARCHIVO_ENTRADA = "evaluacion_secuencias_final.xlsx"
CARPETA_SALIDA = "atlas_y_validacion"

SECUENCIAS = [
    "Planta__BIM-08_C12",
    "Planta__BIM-02_C01",
    "Planta__BIM-02_C04"
]

os.makedirs(CARPETA_SALIDA, exist_ok=True)
os.makedirs(os.path.join(CARPETA_SALIDA, "ajustes_individuales"), exist_ok=True)

# ============================================================
# 2. MODELOS MATEMÁTICOS
# ============================================================

def modelo_exponencial(t, a, r):
    return a * np.exp(r * t)


def modelo_logistico(t, K, r, A):
    return K / (1 + A * np.exp(-r * t))


# ============================================================
# 3. FUNCIONES DE AJUSTE Y EVALUACIÓN
# ============================================================

def calcular_rmse(real, predicho):
    return np.sqrt(mean_squared_error(real, predicho))


def calcular_aicc(real, predicho, k):
    n = len(real)
    rss = np.sum((real - predicho) ** 2)

    if rss <= 0 or n <= k + 1:
        return np.nan

    aic = n * np.log(rss / n) + 2 * k
    return aic + (2 * k * (k + 1)) / (n - k - 1)


def ajustar_exponencial(t, y):
    parametros, covarianza = curve_fit(
        modelo_exponencial,
        t,
        y,
        p0=[max(y[0], 0.001), 0.05],
        bounds=([0, -1], [np.inf, 1]),
        maxfev=50000
    )

    predicciones = modelo_exponencial(t, *parametros)

    return {
        "parametros": parametros,
        "predicciones": predicciones,
        "rmse": calcular_rmse(y, predicciones),
        "aicc": calcular_aicc(y, predicciones, 2)
    }


def ajustar_logistico(t, y):
    maximo = max(y)
    minimo = min(y)

    limite_inferior_K = maximo * 1.001
    limite_superior_K = maximo * 1000

    K_inicial = maximo * 1.5
    A_inicial = max((K_inicial / max(y[0], 0.001)) - 1, 0.01)

    parametros, covarianza = curve_fit(
        modelo_logistico,
        t,
        y,
        p0=[K_inicial, 0.05, A_inicial],
        bounds=(
            [limite_inferior_K, -1, 0.000001],
            [limite_superior_K, 1, 1000000]
        ),
        maxfev=100000
    )

    predicciones = modelo_logistico(t, *parametros)

    return {
        "parametros": parametros,
        "predicciones": predicciones,
        "rmse": calcular_rmse(y, predicciones),
        "aicc": calcular_aicc(y, predicciones, 3),
        "K_en_limite": parametros[0] >= limite_superior_K * 0.999
    }


# ============================================================
# 4. CARGA Y PREPARACIÓN DE DATOS
# ============================================================

print("Leyendo archivo...")

datos = pd.read_excel(
    ARCHIVO_ENTRADA,
    sheet_name="Detalle_OD"
)

columnas_necesarias = [
    "Secuencia", "Fecha", "Edad", "OD", "Estado"
]

for columna in columnas_necesarias:
    if columna not in datos.columns:
        raise ValueError(
            f"No se encontró la columna '{columna}' en Detalle_OD."
        )

datos["Fecha"] = pd.to_datetime(datos["Fecha"], errors="coerce")
datos["Edad"] = pd.to_numeric(datos["Edad"], errors="coerce")
datos["OD"] = pd.to_numeric(datos["OD"], errors="coerce")

# Excluir descartes y registros sin OD o edad.
datos = datos[
    (datos["Estado"] != "Descarte") &
    (datos["OD"].notna()) &
    (datos["Edad"].notna())
].copy()

datos = datos[datos["OD"] > 0].copy()

# ============================================================
# 5. AJUSTES COMPLETOS Y ATLAS DE CURVAS
# ============================================================

resultados_ajustes = []
datos_validos = {}

print("\nGenerando atlas de curvas...")

for secuencia in SECUENCIAS:

    grupo = datos[datos["Secuencia"] == secuencia].copy()

    grupo = grupo.sort_values(
        ["Edad", "Fecha"]
    ).reset_index(drop=True)

    if len(grupo) < 5:
        print(f"{secuencia}: insuficientes observaciones.")
        continue

    edad = grupo["Edad"].to_numpy(dtype=float)
    od = grupo["OD"].to_numpy(dtype=float)

    # Se desplaza la edad para comenzar en cero.
    t = edad - edad.min()

    try:
        exp = ajustar_exponencial(t, od)
    except Exception as error:
        print(f"Error exponencial en {secuencia}: {error}")
        continue

    try:
        log = ajustar_logistico(t, od)
    except Exception as error:
        print(f"Error logístico en {secuencia}: {error}")
        log = None

    # Guardar resultados.
    resultados_ajustes.append({
        "Secuencia": secuencia,
        "N_observaciones": len(od),
        "Edad_inicial": edad.min(),
        "Edad_final": edad.max(),
        "OD_inicial": od[0],
        "OD_final": od[-1],
        "Exp_a": exp["parametros"][0],
        "Exp_r": exp["parametros"][1],
        "Exp_RMSE": exp["rmse"],
        "Exp_AICc": exp["aicc"],
        "Log_K": log["parametros"][0] if log else np.nan,
        "Log_r": log["parametros"][1] if log else np.nan,
        "Log_A": log["parametros"][2] if log else np.nan,
        "Log_RMSE": log["rmse"] if log else np.nan,
        "Log_AICc": log["aicc"] if log else np.nan,
        "Log_K_en_limite": log["K_en_limite"] if log else np.nan
    })

    datos_validos[secuencia] = grupo

    # Construir curvas suaves.
    t_grafico = np.linspace(0, max(t), 200)
    edad_grafico = t_grafico + edad.min()

    od_exp = modelo_exponencial(
        t_grafico, *exp["parametros"]
    )

    # Gráfico individual.
    plt.figure(figsize=(9, 5))

    plt.scatter(
        edad, od,
        label="Mediciones reales",
        s=45
    )

    plt.plot(
        edad_grafico, od_exp,
        label=f"Exponencial (RMSE={exp['rmse']:.4f})"
    )

    if log is not None:
        od_log = modelo_logistico(
            t_grafico, *log["parametros"]
        )

        plt.plot(
            edad_grafico, od_log,
            linestyle="--",
            label=f"Logístico (RMSE={log['rmse']:.4f})"
        )

    plt.xlabel("Días de cultivo")
    plt.ylabel("Densidad óptica (OD)")
    plt.title(f"Ajuste de modelos - {secuencia}")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()

    nombre = secuencia.replace("/", "_").replace(" ", "_")
    ruta = os.path.join(
        CARPETA_SALIDA,
        "ajustes_individuales",
        f"{nombre}.png"
    )

    plt.savefig(ruta, dpi=200)
    plt.close()

# ============================================================
# 6. GRÁFICO COMPARATIVO
# ============================================================

print("Generando gráfico comparativo...")

if datos_validos:

    fig, ejes = plt.subplots(
        len(datos_validos), 1,
        figsize=(10, 4 * len(datos_validos))
    )

    if len(datos_validos) == 1:
        ejes = [ejes]

    for eje, (secuencia, grupo) in zip(
        ejes, datos_validos.items()
    ):

        edad = grupo["Edad"].to_numpy(dtype=float)
        od = grupo["OD"].to_numpy(dtype=float)
        t = edad - edad.min()

        exp = ajustar_exponencial(t, od)

        eje.scatter(
            edad, od,
            label="Mediciones reales",
            s=40
        )

        t_grafico = np.linspace(0, max(t), 200)
        edad_grafico = t_grafico + edad.min()

        eje.plot(
            edad_grafico,
            modelo_exponencial(t_grafico, *exp["parametros"]),
            label="Modelo exponencial"
        )

        try:
            log = ajustar_logistico(t, od)

            eje.plot(
                edad_grafico,
                modelo_logistico(t_grafico, *log["parametros"]),
                linestyle="--",
                label="Modelo logístico"
            )
        except Exception:
            pass

        eje.set_title(secuencia)
        eje.set_xlabel("Días de cultivo")
        eje.set_ylabel("OD")
        eje.grid(alpha=0.3)
        eje.legend()

    plt.tight_layout()

    plt.savefig(
        os.path.join(CARPETA_SALIDA, "atlas_curvas_crecimiento.png"),
        dpi=200
    )

    plt.close()

# ============================================================
# 7. VALIDACIÓN TEMPORAL: ÚLTIMAS DOS OBSERVACIONES
# ============================================================

print("\nRealizando validación temporal...")

resultados_validacion = []
detalle_validacion = []

for secuencia, grupo in datos_validos.items():

    grupo = grupo.sort_values(
        ["Edad", "Fecha"]
    ).reset_index(drop=True)

    if len(grupo) < 7:
        print(f"{secuencia}: no alcanza 7 observaciones.")
        continue

    entrenamiento = grupo.iloc[:-2].copy()
    prueba = grupo.iloc[-2:].copy()

    edad_train = entrenamiento["Edad"].to_numpy(dtype=float)
    od_train = entrenamiento["OD"].to_numpy(dtype=float)

    edad_test = prueba["Edad"].to_numpy(dtype=float)
    od_test = prueba["OD"].to_numpy(dtype=float)

    origen = edad_train.min()

    t_train = edad_train - origen
    t_test = edad_test - origen

    # Referencia: mantener el último valor observado.
    pred_base = np.repeat(od_train[-1], len(od_test))

    # Ajuste exponencial.
    try:
        exp = ajustar_exponencial(t_train, od_train)
        pred_exp = modelo_exponencial(
            t_test, *exp["parametros"]
        )
    except Exception as error:
        print(f"Error exponencial en validación {secuencia}: {error}")
        pred_exp = np.repeat(np.nan, len(od_test))

    # Ajuste logístico.
    try:
        log = ajustar_logistico(t_train, od_train)
        pred_log = modelo_logistico(
            t_test, *log["parametros"]
        )
    except Exception as error:
        print(f"Error logístico en validación {secuencia}: {error}")
        pred_log = np.repeat(np.nan, len(od_test))

    # Métricas de los dos puntos reservados.
    mae_base = mean_absolute_error(od_test, pred_base)
    rmse_base = calcular_rmse(od_test, pred_base)

    mae_exp = (
        mean_absolute_error(od_test, pred_exp)
        if np.all(np.isfinite(pred_exp)) else np.nan
    )

    rmse_exp = (
        calcular_rmse(od_test, pred_exp)
        if np.all(np.isfinite(pred_exp)) else np.nan
    )

    mae_log = (
        mean_absolute_error(od_test, pred_log)
        if np.all(np.isfinite(pred_log)) else np.nan
    )

    rmse_log = (
        calcular_rmse(od_test, pred_log)
        if np.all(np.isfinite(pred_log)) else np.nan
    )

    resultados_validacion.append({
        "Secuencia": secuencia,
        "N_entrenamiento": len(entrenamiento),
        "N_prueba": len(prueba),
        "MAE_referencia": mae_base,
        "RMSE_referencia": rmse_base,
        "MAE_exponencial": mae_exp,
        "RMSE_exponencial": rmse_exp,
        "MAE_logistico": mae_log,
        "RMSE_logistico": rmse_log
    })

    for i in range(len(prueba)):
        detalle_validacion.append({
            "Secuencia": secuencia,
            "Conjunto": "Prueba",
            "Fecha": prueba.iloc[i]["Fecha"],
            "Edad": edad_test[i],
            "OD_real": od_test[i],
            "OD_referencia": pred_base[i],
            "OD_exponencial": pred_exp[i],
            "OD_logistico": pred_log[i]
        })

    # Gráfico de validación.
    plt.figure(figsize=(9, 5))

    plt.scatter(
        edad_train, od_train,
        label="Datos de ajuste",
        s=45
    )

    plt.scatter(
        edad_test, od_test,
        label="Datos reservados (reales)",
        marker="s",
        s=65
    )

    plt.plot(
        edad_test, pred_base,
        marker="o",
        linestyle=":",
        label="Referencia: último OD"
    )

    if np.all(np.isfinite(pred_exp)):
        plt.plot(
            edad_test, pred_exp,
            marker="o",
            linestyle="--",
            label="Predicción exponencial"
        )

    if np.all(np.isfinite(pred_log)):
        plt.plot(
            edad_test, pred_log,
            marker="o",
            linestyle="--",
            label="Predicción logística"
        )

    plt.xlabel("Días de cultivo")
    plt.ylabel("Densidad óptica (OD)")
    plt.title(f"Validación temporal - {secuencia}")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()

    nombre = secuencia.replace("/", "_").replace(" ", "_")

    plt.savefig(
        os.path.join(
            CARPETA_SALIDA,
            f"validacion_{nombre}.png"
        ),
        dpi=200
    )

    plt.close()

# ============================================================
# 8. EXPORTAR RESULTADOS
# ============================================================

archivo_salida = os.path.join(
    CARPETA_SALIDA,
    "resultados_atlas_validacion.xlsx"
)

with pd.ExcelWriter(archivo_salida, engine="openpyxl") as writer:

    pd.DataFrame(resultados_ajustes).to_excel(
        writer,
        sheet_name="Ajustes_completos",
        index=False
    )

    pd.DataFrame(resultados_validacion).to_excel(
        writer,
        sheet_name="Validacion_temporal",
        index=False
    )

    pd.DataFrame(detalle_validacion).to_excel(
        writer,
        sheet_name="Predicciones",
        index=False
    )

print("\n========================================")
print("PROCESO FINALIZADO")
print("========================================")
print(f"Carpeta de resultados: {CARPETA_SALIDA}")
print(f"Archivo Excel: {archivo_salida}")
print("Gráficos individuales y comparativos generados.")
