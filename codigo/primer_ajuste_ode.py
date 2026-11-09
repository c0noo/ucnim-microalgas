import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from pathlib import Path

ARCHIVO = "datos_procesados_corregidos.xlsx"
CARPETA = Path("primer_ajuste_ode")
CARPETA.mkdir(exist_ok=True)

SECUENCIAS = [
    "Planta__BIM-08_C12",
    "Planta__BIM-02_C01",
    "Planta__BIM-02_C04"
]

def exponencial(t, a, r):
    return a * np.exp(r * t)

def logistica(t, K, r, A):
    return K / (1 + A * np.exp(-r * t))

def metricas(y, pred, k):
    n = len(y)
    residuos = y - pred
    rss = np.sum(residuos ** 2)
    rmse = np.sqrt(np.mean(residuos ** 2))

    if rss <= 0:
        aicc = np.nan
    else:
        aic = n * np.log(rss / n) + 2 * k
        aicc = aic + (2 * k * (k + 1)) / (n - k - 1) if n > k + 1 else np.nan

    return rmse, aicc, rss

df = pd.read_excel(ARCHIVO)
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
df["OD"] = pd.to_numeric(df["OD"], errors="coerce")
df["Días cultivo"] = pd.to_numeric(df["Días cultivo"], errors="coerce")

resultados = []
predicciones = []

for sec in SECUENCIAS:
    g = df[
        (df["Ciclo_ID"] == sec) &
        (df["Estado"].astype(str).str.lower() != "descarte")
    ].copy()

    g = g.dropna(subset=["OD", "Días cultivo"])
    g = g.sort_values(["Días cultivo", "Fecha"])

    # Una observación por registro, sin eliminar edades repetidas automáticamente
    t_original = g["Días cultivo"].to_numpy(dtype=float)
    y = g["OD"].to_numpy(dtype=float)
    t = t_original - t_original.min()

    print("\n" + "=" * 65)
    print(sec, "- observaciones:", len(y))
    print("=" * 65)

    if len(y) < 5 or len(np.unique(t)) < 4:
        print("Datos insuficientes para este ajuste exploratorio.")
        continue

    # Modelo exponencial
    try:
        p_exp, _ = curve_fit(
            exponencial, t, y,
            p0=[max(y[0], 0.001), 0.03],
            bounds=([0, 0], [np.inf, 2]),
            maxfev=30000
        )
        pred_exp = exponencial(t, *p_exp)
        rmse_exp, aicc_exp, rss_exp = metricas(y, pred_exp, 2)

        resultados.append({
            "Secuencia": sec,
            "Modelo": "Exponencial",
            "N": len(y),
            "Parametro_a": p_exp[0],
            "r": p_exp[1],
            "K": np.nan,
            "RMSE": rmse_exp,
            "AICc": aicc_exp,
            "RSS": rss_exp,
            "Aviso": ""
        })

        for ti, yi, pi in zip(t_original, y, pred_exp):
            predicciones.append({
                "Secuencia": sec, "Modelo": "Exponencial",
                "Edad": ti, "OD_observada": yi, "OD_ajustada": pi
            })

    except Exception as e:
        print("No se pudo ajustar exponencial:", e)

    # Modelo logístico
    try:
        K0 = max(y) * 3
        A0 = max(K0 / max(y[0], 0.001) - 1, 0.01)

        p_log, cov_log = curve_fit(
            logistica, t, y,
            p0=[K0, 0.1, A0],
            bounds=(
                [max(y) * 1.001, 0.000001, 0.000001],
                [max(y) * 1000, 5, 10000]
            ),
            maxfev=100000
        )

        pred_log = logistica(t, *p_log)
        rmse_log, aicc_log, rss_log = metricas(y, pred_log, 3)

        # Revisar si K llegó al límite superior
        limite_K = p_log[0] >= max(y) * 999

        resultados.append({
            "Secuencia": sec,
            "Modelo": "Logístico",
            "N": len(y),
            "Parametro_a": np.nan,
            "r": p_log[1],
            "K": p_log[0],
            "RMSE": rmse_log,
            "AICc": aicc_log,
            "RSS": rss_log,
            "Aviso": "K alcanzó el límite superior" if limite_K else ""
        })

        for ti, yi, pi in zip(t_original, y, pred_log):
            predicciones.append({
                "Secuencia": sec, "Modelo": "Logístico",
                "Edad": ti, "OD_observada": yi, "OD_ajustada": pi
            })

    except Exception as e:
        print("No se pudo ajustar logístico:", e)

    # Gráfico de observaciones y ajustes
    plt.figure(figsize=(8, 5))
    plt.scatter(t_original, y, label="OD observada")

    t_plot = np.linspace(t.min(), t.max(), 150)

    try:
        plt.plot(t_plot + t_original.min(),
                 exponencial(t_plot, *p_exp),
                 label="Exponencial")
    except:
        pass

    try:
        plt.plot(t_plot + t_original.min(),
                 logistica(t_plot, *p_log),
                 label="Logístico")
    except:
        pass

    plt.xlabel("Días de cultivo")
    plt.ylabel("Densidad óptica (OD)")
    plt.title(sec)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(CARPETA / (sec.replace("/", "_") + ".png"), dpi=150)
    plt.close()

    print("Edades:", t_original)
    print("OD:", y)

# Exportar resultados
res = pd.DataFrame(resultados)
pred = pd.DataFrame(predicciones)

with pd.ExcelWriter("resultados_primer_ajuste_ode.xlsx") as writer:
    res.to_excel(writer, sheet_name="Comparacion_modelos", index=False)
    pred.to_excel(writer, sheet_name="Predicciones", index=False)

print("\nRESULTADOS DE LOS AJUSTES")
print(res.to_string(index=False))
print("\nArchivo generado: resultados_primer_ajuste_ode.xlsx")
print("Gráficos guardados en:", CARPETA)
