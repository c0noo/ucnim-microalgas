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

ARCHIVO = "evaluacion_secuencias_final.xlsx"
CARPETA = "validacion_origen_movil"

SECUENCIAS = [
    "Planta__BIM-08_C12",
    "Planta__BIM-02_C01",
    "Planta__BIM-02_C04"
]

MINIMO_ENTRENAMIENTO = 5

os.makedirs(CARPETA, exist_ok=True)
os.makedirs(os.path.join(CARPETA, "graficos"), exist_ok=True)


# ============================================================
# 2. MODELOS
# ============================================================

def exponencial(t, a, r):
    return a * np.exp(r * t)


def logistico(t, K, r, A):
    return K / (1 + A * np.exp(-r * t))


# ============================================================
# 3. AJUSTES
# ============================================================

def ajustar_exponencial(t, y):

    parametros, _ = curve_fit(
        exponencial,
        t,
        y,
        p0=[max(y[0], 0.001), 0.05],
        bounds=([0.000001, -1], [np.inf, 1]),
        maxfev=50000
    )

    return parametros


def ajustar_logistico(t, y):

    maximo = max(y)

    K_inicial = maximo * 1.5
    A_inicial = max(
        (K_inicial / max(y[0], 0.001)) - 1,
        0.01
    )

    parametros, _ = curve_fit(
        logistico,
        t,
        y,
        p0=[K_inicial, 0.05, A_inicial],
        bounds=(
            [maximo * 1.001, -1, 0.000001],
            [maximo * 1000, 1, 1000000]
        ),
        maxfev=100000
    )

    return parametros


# ============================================================
# 4. CARGA Y PREPARACIÓN
# ============================================================

print("Cargando datos...")

datos = pd.read_excel(
    ARCHIVO,
    sheet_name="Detalle_OD"
)

datos["Fecha"] = pd.to_datetime(
    datos["Fecha"],
    errors="coerce"
)

datos["Edad"] = pd.to_numeric(
    datos["Edad"],
    errors="coerce"
)

datos["OD"] = pd.to_numeric(
    datos["OD"],
    errors="coerce"
)

datos = datos[
    (datos["Estado"] != "Descarte") &
    datos["Edad"].notna() &
    datos["OD"].notna() &
    (datos["OD"] > 0)
].copy()


# ============================================================
# 5. VALIDACIÓN DE ORIGEN MÓVIL
# ============================================================

predicciones = []

print("\nIniciando validación temporal...\n")

for secuencia in SECUENCIAS:

    grupo = datos[
        datos["Secuencia"] == secuencia
    ].copy()

    grupo = grupo.sort_values(
        ["Edad", "Fecha"],
        kind="stable"
    ).reset_index(drop=True)

    n = len(grupo)

    print(f"{secuencia}: {n} observaciones")

    if n <= MINIMO_ENTRENAMIENTO:
        print("  No hay suficientes observaciones.")
        continue

    # Cada iteración utiliza todas las observaciones
    # anteriores para predecir exactamente la siguiente.

    for corte in range(MINIMO_ENTRENAMIENTO, n):

        entrenamiento = grupo.iloc[:corte]
        observacion = grupo.iloc[corte]

        edad_train = entrenamiento["Edad"].to_numpy(float)
        od_train = entrenamiento["OD"].to_numpy(float)

        edad_real = float(observacion["Edad"])
        od_real = float(observacion["OD"])

        edad_origen = edad_train.min()

        t_train = edad_train - edad_origen
        t_futuro = edad_real - edad_origen

        # Referencia: último valor observado.
        pred_referencia = od_train[-1]

        # Modelo exponencial.
        try:
            parametros_exp = ajustar_exponencial(
                t_train,
                od_train
            )

            pred_exp = float(
                exponencial(t_futuro, *parametros_exp)
            )

        except Exception:
            pred_exp = np.nan

        # Modelo logístico.
        try:
            parametros_log = ajustar_logistico(
                t_train,
                od_train
            )

            pred_log = float(
                logistico(t_futuro, *parametros_log)
            )

        except Exception:
            pred_log = np.nan

        predicciones.append({
            "Secuencia": secuencia,
            "N_entrenamiento": corte,
            "Edad_real": edad_real,
            "Fecha_real": observacion["Fecha"],
            "OD_real": od_real,
            "OD_referencia": pred_referencia,
            "OD_exponencial": pred_exp,
            "OD_logistico": pred_log,
            "Error_referencia": od_real - pred_referencia,
            "Error_exponencial": (
                od_real - pred_exp
                if np.isfinite(pred_exp) else np.nan
            ),
            "Error_logistico": (
                od_real - pred_log
                if np.isfinite(pred_log) else np.nan
            )
        })

        print(
            f"  Entrenamiento: {corte} | "
            f"Edad predicha: {edad_real} | "
            f"OD real: {od_real:.4f} | "
            f"Exp: {pred_exp:.4f} | "
            f"Log: {pred_log:.4f}"
            if np.isfinite(pred_exp) and np.isfinite(pred_log)
            else
            f"  Entrenamiento: {corte} | "
            f"Edad predicha: {edad_real} | "
            f"OD real: {od_real:.4f} | "
            f"Exp: {pred_exp} | Log: {pred_log}"
        )


# ============================================================
# 6. TABLA DETALLADA DE PREDICCIONES
# ============================================================

detalle = pd.DataFrame(predicciones)

if detalle.empty:
    raise ValueError(
        "No se generaron predicciones. Revisa las secuencias."
    )


# ============================================================
# 7. MÉTRICAS POR SECUENCIA
# ============================================================

def calcular_metricas(grupo, columna):

    validos = grupo[
        grupo[columna].notna()
    ]

    if len(validos) == 0:
        return np.nan, np.nan, 0

    real = validos["OD_real"]
    predicho = validos[columna]

    mae = mean_absolute_error(real, predicho)
    rmse = np.sqrt(mean_squared_error(real, predicho))

    return mae, rmse, len(validos)


resumen = []

for secuencia, grupo in detalle.groupby("Secuencia"):

    fila = {"Secuencia": secuencia}

    for nombre, columna in [
        ("Referencia", "OD_referencia"),
        ("Exponencial", "OD_exponencial"),
        ("Logistico", "OD_logistico")
    ]:

        mae, rmse, n = calcular_metricas(
            grupo,
            columna
        )

        fila[f"MAE_{nombre}"] = mae
        fila[f"RMSE_{nombre}"] = rmse
        fila[f"N_{nombre}"] = n

    resumen.append(fila)

resumen = pd.DataFrame(resumen)


# ============================================================
# 8. MÉTRICAS GLOBALES
# ============================================================

globales = []

for nombre, columna in [
    ("Referencia", "OD_referencia"),
    ("Exponencial", "OD_exponencial"),
    ("Logistico", "OD_logistico")
]:

    mae, rmse, n = calcular_metricas(
        detalle,
        columna
    )

    globales.append({
        "Modelo": nombre,
        "N_predicciones": n,
        "MAE": mae,
        "RMSE": rmse
    })

globales = pd.DataFrame(globales)


# ============================================================
# 9. GRÁFICOS POR SECUENCIA
# ============================================================

print("\nGenerando gráficos...")

for secuencia, grupo_pred in detalle.groupby("Secuencia"):

    grupo_original = datos[
        datos["Secuencia"] == secuencia
    ].sort_values(
        ["Edad", "Fecha"],
        kind="stable"
    )

    plt.figure(figsize=(10, 6))

    # Todas las mediciones reales.
    plt.scatter(
        grupo_original["Edad"],
        grupo_original["OD"],
        label="Mediciones reales",
        s=45
    )

    # Predicciones sucesivas.
    plt.plot(
        grupo_pred["Edad_real"],
        grupo_pred["OD_exponencial"],
        marker="o",
        linestyle="--",
        label="Predicción exponencial"
    )

    plt.plot(
        grupo_pred["Edad_real"],
        grupo_pred["OD_logistico"],
        marker="s",
        linestyle="--",
        label="Predicción logística"
    )

    plt.plot(
        grupo_pred["Edad_real"],
        grupo_pred["OD_referencia"],
        marker="x",
        linestyle=":",
        label="Referencia: último OD"
    )

    plt.xlabel("Días de cultivo")
    plt.ylabel("Densidad óptica (OD)")
    plt.title(f"Validación de origen móvil - {secuencia}")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()

    nombre = secuencia.replace("/", "_").replace(" ", "_")

    plt.savefig(
        os.path.join(
            CARPETA,
            "graficos",
            f"validacion_{nombre}.png"
        ),
        dpi=200
    )

    plt.close()


# ============================================================
# 10. EXPORTAR RESULTADOS
# ============================================================

salida = os.path.join(
    CARPETA,
    "resultados_validacion_origen_movil.xlsx"
)

with pd.ExcelWriter(
    salida,
    engine="openpyxl"
) as writer:

    detalle.to_excel(
        writer,
        sheet_name="Predicciones",
        index=False
    )

    resumen.to_excel(
        writer,
        sheet_name="Metricas_secuencia",
        index=False
    )

    globales.to_excel(
        writer,
        sheet_name="Metricas_globales",
        index=False
    )


# ============================================================
# 11. MOSTRAR RESULTADOS
# ============================================================

print("\n========================================")
print("MÉTRICAS POR SECUENCIA")
print("========================================")

print(resumen.round(5).to_string(index=False))

print("\n========================================")
print("MÉTRICAS GLOBALES")
print("========================================")

print(globales.round(5).to_string(index=False))

print("\n========================================")
print("PROCESO FINALIZADO")
print("========================================")

print(f"Resultados: {salida}")
print(f"Gráficos: {CARPETA}/graficos/")
