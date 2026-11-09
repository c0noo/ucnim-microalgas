import pandas as pd
import numpy as np
from scipy.optimize import curve_fit

ARCHIVO = "datos_procesados_corregidos.xlsx"

SECUENCIAS = [
    "Planta__BIM-08_C12",
    "Planta__BIM-02_C01",
    "Planta__BIM-02_C04"
]

def exponencial(t, a, r):
    return a * np.exp(r * t)

def logistica(t, K, r, A):
    return K / (1 + A * np.exp(-r * t))

df = pd.read_excel(ARCHIVO)
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

for c in ["OD", "Días cultivo"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

resultados = []

for sec in SECUENCIAS:
    g = df[
        (df["Ciclo_ID"] == sec) &
        (df["Estado"].astype(str).str.lower() != "descarte")
    ].dropna(subset=["OD", "Días cultivo"]).sort_values(
        ["Días cultivo", "Fecha"]
    )

    t_original = g["Días cultivo"].to_numpy(float)
    t = t_original - t_original.min()
    y = g["OD"].to_numpy(float)

    print("\n" + "=" * 65)
    print(sec)
    print("=" * 65)

    for nombre, funcion, p0, limites, k in [
        (
            "Exponencial",
            exponencial,
            [y[0], 0.04],
            ([0, 0], [np.inf, 2]),
            2
        ),
        (
            "Logístico",
            logistica,
            [max(y)*3, 0.05, 2],
            ([max(y)*1.001, 0.000001, 0.000001],
             [max(y)*1000, 5, 10000]),
            3
        )
    ]:
        try:
            p, cov = curve_fit(
                funcion, t, y,
                p0=p0,
                bounds=limites,
                maxfev=100000
            )

            errores = np.sqrt(np.diag(cov))
            pred = funcion(t, *p)
            rmse = np.sqrt(np.mean((y-pred)**2))

            print("\nModelo:", nombre)
            print("Parámetros:", p)
            print("Errores estándar aproximados:", errores)
            print("RMSE:", rmse)

            if nombre == "Logístico":
                if p[0] >= max(y)*999:
                    print("ADVERTENCIA: K alcanzó el límite superior.")
                if not np.all(np.isfinite(errores)):
                    print("ADVERTENCIA: incertidumbre no estimable.")
                elif errores[0] > p[0]:
                    print("ADVERTENCIA: K presenta alta incertidumbre.")

            # Sensibilidad: retirar una observación cada vez
            valores = []

            for i in range(len(y)):
                mascara = np.arange(len(y)) != i
                if len(np.unique(t[mascara])) < 4:
                    continue

                try:
                    pp, _ = curve_fit(
                        funcion,
                        t[mascara],
                        y[mascara],
                        p0=p,
                        bounds=limites,
                        maxfev=100000
                    )
                    valores.append(pp)
                except Exception:
                    pass

            if valores:
                valores = np.array(valores)
                print("Parámetros al retirar una observación:")
                for j in range(len(p)):
                    print(
                        f"  Parámetro {j+1}: "
                        f"mínimo={valores[:,j].min():.6f}, "
                        f"máximo={valores[:,j].max():.6f}"
                    )

        except Exception as e:
            print("No se pudo validar:", e)

print("\nFIN DE LA VALIDACIÓN")
