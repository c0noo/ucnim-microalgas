"""
Heterogeneidad de tasa de crecimiento y covariables con rezago.
Lee la matriz enriquecida (24 filas) y los parámetros del exponencial.
Ejecutar desde ~/UCNIM/resultados_epica1/
"""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = Path("matriz_diagnostico_operacional")
F_ENR = D / "matriz_diagnostico_enriquecida.xlsx"
F_PAR = Path("validacion_loo/resultados_validacion_loo.xlsx")
F_RUIDO = Path("comparacion_mediciones_od.xlsx")
OUT_XLSX = D / "diagnostico_regimen_crecimiento.xlsx"
OUT_PNG = D / "graficos_enriquecida"
N_PERM = 5000
rng = np.random.default_rng(42)

# ------------------------- carga -------------------------
E = pd.read_excel(F_ENR, sheet_name="Matriz_enriquecida")
E["Fecha"] = pd.to_datetime(E["Fecha"])
E = E.sort_values(["Secuencia", "Fecha"]).reset_index(drop=True)

# r del exponencial ajustado con todos los datos (tasa "promedio" del modelo)
par = pd.read_excel(F_PAR, sheet_name="Parametros_completos")
r_exp = par.loc[par["Modelo"] == "Exponencial"].set_index("Secuencia")["r"]
E["r_exp"] = E["Secuencia"].map(r_exp)
E["mu_dev"] = E["mu_obs"] - E["r_exp"]      # >0: el cultivo crece más rápido que el modelo

# ------------------------- rezagos (intervalo previo) -------------------------
g = E.groupby("Secuencia")
for c in ["tasa_pH", "tasa_T", "tasa_EC", "vol_rel"]:
    E[f"{c}_lag1"] = g[c].shift(1)

# ------------------------- tablas -------------------------
COLS_INT = ["Secuencia", "Días cultivo", "dt_dias", "OD", "mu_obs", "r_exp", "mu_dev",
            "tasa_pH", "tasa_T", "tasa_EC", "vol_rel",
            "tasa_pH_lag1", "tasa_T_lag1", "tasa_EC_lag1",
            "Error_exponencial", "z_err_exp", "vars_cambio_inusual"]
INT = E[COLS_INT].round(3)

dist = (E.groupby("Secuencia")["mu_obs"]
          .describe(percentiles=[.25, .5, .75])
          .join(r_exp.rename("r_exp")).round(3))

# ------------------------- asociaciones (permutación intra-secuencia) -------------------------
def zs(s):
    """Estandariza dentro de la secuencia (evita mezclar escalas entre recipientes)."""
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd > 0 else s * 0

def perm_spearman(x, y, grp):
    """Spearman pooled; p por permutación de y DENTRO de cada secuencia."""
    d = pd.DataFrame({"x": x, "y": y, "g": grp}).dropna()
    if len(d) < 6 or d["x"].nunique() < 2 or d["y"].nunique() < 2:
        return np.nan, np.nan, len(d)
    xv, yv = d["x"].to_numpy(), d["y"].to_numpy()
    grupos = [np.where(d["g"].to_numpy() == k)[0] for k in d["g"].unique()]
    rho = spearmanr(xv, yv)[0]
    cnt = 0
    for _ in range(N_PERM):
        yp = yv.copy()
        for ix in grupos:
            yp[ix] = rng.permutation(yv[ix])
        if abs(spearmanr(xv, yp)[0]) >= abs(rho) - 1e-12:
            cnt += 1
    return rho, (cnt + 1) / (N_PERM + 1), len(d)

covs = ["tasa_pH", "tasa_T", "tasa_EC", "vol_rel",
        "tasa_pH_lag1", "tasa_T_lag1", "tasa_EC_lag1", "vol_rel_lag1"]
filas = []
for c in covs:
    x = E.groupby("Secuencia")[c].transform(zs)
    for tgt, lab in [("mu_dev", "mu_obs - r_exp"), ("Error_exponencial", "error LOO exp")]:
        rho, p, n = perm_spearman(x, E[tgt], E["Secuencia"])
        filas.append(dict(covariable=c, objetivo=lab, n=n, rho=round(rho, 3), p_perm=round(p, 4)))
ASOC = pd.DataFrame(filas)

# ------------------------- gráficos -------------------------
OUT_PNG.mkdir(parents=True, exist_ok=True)
for s, d in E.groupby("Secuencia"):
    fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    ax[0].bar(d["t_dias"], d["mu_obs"], width=0.4,
              color=np.where(d["hueco"].astype(bool), "lightgray", "tab:blue"))
    ax[0].axhline(d["r_exp"].iloc[0], c="r", ls="--", label="r del exponencial ajustado")
    ax[0].axhline(0, c="k", lw=.5)
    ax[0].set_ylabel("mu_obs (1/d)\n(gris = intervalo > 1.5 d)")
    ax[0].legend(fontsize=8); ax[0].set_title(s)
    ax[1].plot(d["t_dias"], d["pH"], "o-", c="tab:green"); ax[1].set_ylabel("pH")
    a2 = ax[1].twinx(); a2.plot(d["t_dias"], d["EC"], "s--", c="tab:purple"); a2.set_ylabel("EC")
    ax[1].set_xlabel("t desde primer registro (días)")
    plt.tight_layout(); fig.savefig(OUT_PNG / f"{s}_regimen_mu.png", dpi=150); plt.close(fig)

# ------------------------- salida -------------------------
with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as xw:
    INT.to_excel(xw, sheet_name="Intervalos", index=False)
    dist.reset_index().to_excel(xw, sheet_name="Distribucion_mu", index=False)
    ASOC.to_excel(xw, sheet_name="Asociaciones_rezago", index=False)

pd.set_option("display.width", 250, "display.max_columns", 40)
print("== BIM-08_C12: intervalos ==")
print(INT[INT["Secuencia"] == "Planta__BIM-08_C12"].to_string(index=False))
print("\n== Distribución de mu_obs vs r del exponencial ==\n", dist.to_string())
print("\n== Asociaciones (permutación intra-secuencia; 8 covariables x 2 objetivos, "
      "sin corrección por múltiples contrastes: p < 0.003 para Bonferroni) ==\n", ASOC.to_string(index=False))

print("\n== Esquema comparacion_mediciones_od.xlsx (para fijar piso de ruido de la OD) ==")
if F_RUIDO.exists():
    for h, df in pd.read_excel(F_RUIDO, sheet_name=None).items():
        print(f"--- hoja '{h}': {df.shape}\ncolumnas: {list(df.columns)}\n{df.head(3).to_string()}")
else:
    print("no existe")
print(f"\nGuardado: {OUT_XLSX}")
