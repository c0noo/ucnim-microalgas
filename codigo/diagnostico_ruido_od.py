"""
Ruido de medición de OD (escala log) y efecto de la hora de lectura.
Fuente: evaluacion_secuencias_final.xlsx (Detalle_OD, Resumen_secuencias)
Ejecutar desde ~/UCNIM/resultados_epica1/
"""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr

F = Path("evaluacion_secuencias_final.xlsx")
F_LOO = Path("validacion_loo/resultados_validacion_loo.xlsx")
OUT = Path("diagnostico_ruido_od"); OUT.mkdir(exist_ok=True)

MAX_SPAN = 4.0        # días máx. entre la 1ª y 3ª lectura del trío (limita la curvatura real)
MIN_DT = 0.2          # días mín. entre lecturas consecutivas
EXCLUIR_OD_ALTA = True  # excluye lecturas marcadas OD_Alta_Revisar
N_BOOT = 5000
N_SIM = 5000
PRIORITARIAS = ["Planta__BIM-08_C12", "Planta__BIM-02_C04", "Planta__BIM-02_C01"]
rng = np.random.default_rng(42)

# ------------------------------- carga -------------------------------
det = pd.read_excel(F, sheet_name="Detalle_OD")
res = (pd.read_excel(F, sheet_name="Resumen_secuencias")[["Secuencia", "Clasificacion"]]
         .drop_duplicates("Secuencia"))
det["Fecha"] = pd.to_datetime(det["Fecha"])
det = det.merge(res, on="Secuencia", how="left")
n0 = len(det)
det = det[det["OD"] > 0]
if EXCLUIR_OD_ALTA:
    det = det[~det["OD_Alta_Revisar"].astype(bool)]
print(f"Lecturas: {n0} -> {len(det)} tras filtros (OD>0"
      f"{', sin OD_Alta_Revisar' if EXCLUIR_OD_ALTA else ''}); "
      f"{det['Secuencia'].nunique()} secuencias")
det = det.sort_values(["Secuencia", "Fecha"]).reset_index(drop=True)
det["Localidad"] = det["Secuencia"].str.split("__").str[0]
det["hora"] = det["Fecha"].dt.hour + det["Fecha"].dt.minute / 60


# ------------------------------- tríos -------------------------------
def triadas(g):
    t = (g["Fecha"] - g["Fecha"].iloc[0]).dt.total_seconds().to_numpy() / 86400
    y, h, od = np.log(g["OD"].to_numpy()), g["hora"].to_numpy(), g["OD"].to_numpy()
    filas = []
    for i in range(1, len(g) - 1):
        t0, t1, t2 = t[i - 1], t[i], t[i + 1]
        if (t1 - t0) < MIN_DT or (t2 - t1) < MIN_DT or (t2 - t0) > MAX_SPAN:
            continue
        w = (t1 - t0) / (t2 - t0)
        e = y[i] - ((1 - w) * y[i - 1] + w * y[i + 1])      # residuo vs interpolación log-lineal
        k = np.sqrt(1 + w ** 2 + (1 - w) ** 2)               # Var(e) = sigma^2 * k^2
        dh = h[i] - ((1 - w) * h[i - 1] + w * h[i + 1])      # hora vs hora interpolada de vecinas
        filas.append(dict(Secuencia=g["Secuencia"].iloc[0], Localidad=g["Localidad"].iloc[0],
                          Fecha=g["Fecha"].iloc[i], OD=od[i], hora=h[i], w=w,
                          e_log=e, e_norm=e / k, dh_horas=dh))
    return pd.DataFrame(filas)


T = pd.concat([triadas(g) for _, g in det.groupby("Secuencia")], ignore_index=True)
print(f"Tríos utilizables: {len(T)} en {T['Secuencia'].nunique()} secuencias")


# ------------------------------- ruido -------------------------------
def sig(x):
    x = np.asarray(x, float)
    return pd.Series(dict(n=len(x),
                          sigma_rms=np.sqrt(np.mean(x ** 2)),
                          sigma_mad=1.4826 * np.median(np.abs(x))))


R_glob = sig(T["e_norm"]).to_frame("TODAS").T
R_loc = T.groupby("Localidad")["e_norm"].apply(sig).unstack()
T["tramo_OD"] = pd.qcut(T["OD"], 3, labels=["OD baja", "OD media", "OD alta"])
R_od = T.groupby("tramo_OD", observed=True)["e_norm"].apply(sig).unstack()
R_seq = T.groupby("Secuencia")["e_norm"].apply(sig).unstack()
R_all = pd.concat([R_glob, R_loc, R_od]).round(4)


# ------------------------------- efecto hora -------------------------------
print("\nDistribución de hora de lectura (h):")
print(det["hora"].describe(percentiles=[.05, .25, .5, .75, .95]).round(2).to_string())
print(f"SD de dh (hora - hora interpolada vecinas): {T['dh_horas'].std():.2f} h; "
      f"tríos con |dh| > 1 h: {(T['dh_horas'].abs() > 1).sum()} de {len(T)}")

S = (T.assign(sxy=T["dh_horas"] * T["e_log"], sxx=T["dh_horas"] ** 2)
       .groupby("Secuencia")[["sxy", "sxx"]].sum())
beta = S["sxy"].sum() / S["sxx"].sum()                       # ln(OD) por hora, regresión por el origen
seqs = S.index.to_numpy()
bs = np.empty(N_BOOT)
for b in range(N_BOOT):
    idx = rng.integers(0, len(seqs), len(seqs))              # remuestreo por secuencia
    bs[b] = S["sxy"].to_numpy()[idx].sum() / S["sxx"].to_numpy()[idx].sum()
rho, p_rho = spearmanr(T["dh_horas"], T["e_log"])
H = pd.DataFrame([dict(beta_lnOD_por_hora=beta, beta_pct_por_hora=100 * (np.exp(beta) - 1),
                       IC95_inf=np.nanpercentile(bs, 2.5), IC95_sup=np.nanpercentile(bs, 97.5),
                       spearman_rho=rho, spearman_p=p_rho, n_trios=len(T), n_secuencias=len(seqs))]).round(4)

# Sensibilidad: sin los 3 tríos de mayor |dh|
T_s = T.reindex(T["dh_horas"].abs().sort_values(ascending=False).index[3:])
beta_s = (T_s["dh_horas"] * T_s["e_log"]).sum() / (T_s["dh_horas"] ** 2).sum()
H["beta_sin_top3_dh"] = round(beta_s, 4)


# ------------------------------- simulación LOO por ruido -------------------------------
def loo_rmse_loglineal(Y, t):
    """RMSE LOO (escala OD) del exponencial ajustado por regresión log-lineal.
    Y: (m, n) ln(OD). Usa la fórmula cerrada e_i/(1-h_ii)."""
    X = np.column_stack([np.ones_like(t), t])
    Hm = X @ np.linalg.inv(X.T @ X) @ X.T
    e = Y - Y @ Hm.T
    e_loo = e / (1 - np.diag(Hm))
    pred = Y - e_loo
    return np.sqrt(np.mean((np.exp(Y) - np.exp(pred)) ** 2, axis=1)), Hm


obs_ref = (pd.read_excel(F_LOO, sheet_name="Resumen")
             .set_index("Secuencia")["RMSE_LOO_exponencial"])
sim_rows = []
sig_planta = R_loc.loc["Planta"] if "Planta" in R_loc.index else R_glob.iloc[0]
for s in PRIORITARIAS:
    g = det[det["Secuencia"] == s]
    if len(g) < 5:
        continue
    t = (g["Fecha"] - g["Fecha"].iloc[0]).dt.total_seconds().to_numpy() / 86400
    y = np.log(g["OD"].to_numpy())
    obs, Hm = loo_rmse_loglineal(y[None, :], t)
    linea = (Hm @ y)                                          # "verdad" = recta log-lineal ajustada
    for nombre, sg in [("sigma_mad", sig_planta["sigma_mad"]), ("sigma_rms", sig_planta["sigma_rms"])]:
        Ysim = linea[None, :] + rng.normal(0, sg, (N_SIM, len(t)))
        sim, _ = loo_rmse_loglineal(Ysim, t)
        sim_rows.append(dict(Secuencia=s, n=len(t), sigma_usada=nombre, sigma=round(sg, 4),
                             RMSE_LOO_obs_loglineal=round(float(obs[0]), 4),
                             RMSE_LOO_obs_exp_reportado=round(float(obs_ref.get(s, np.nan)), 4),
                             sim_p05=round(np.percentile(sim, 5), 4),
                             sim_mediana=round(np.percentile(sim, 50), 4),
                             sim_p95=round(np.percentile(sim, 95), 4),
                             frac_sim_ge_obs=round(float((sim >= obs[0]).mean()), 3)))
SIM = pd.DataFrame(sim_rows)


# ------------------------------- salida -------------------------------
with pd.ExcelWriter(OUT / "diagnostico_ruido_od.xlsx", engine="openpyxl") as xw:
    T.to_excel(xw, sheet_name="Trios", index=False)
    R_all.reset_index().to_excel(xw, sheet_name="Ruido_resumen", index=False)
    R_seq.round(4).reset_index().to_excel(xw, sheet_name="Ruido_por_secuencia", index=False)
    H.to_excel(xw, sheet_name="Efecto_hora", index=False)
    SIM.to_excel(xw, sheet_name="Simulacion_RMSE_LOO", index=False)

pd.set_option("display.width", 230, "display.max_columns", 40)
print("\n== Ruido sigma (escala log) – cota superior; rms vs MAD robusto ==\n", R_all.to_string())
print("\n== Efecto de la hora de lectura ==\n", H.T.to_string(header=False))
print("\n== Mayores |dh| (identificación del efecto hora) ==")
print(T.reindex(T["dh_horas"].abs().sort_values(ascending=False).index)
        .head(8)[["Secuencia", "Fecha", "hora", "dh_horas", "e_log", "OD"]].round(3).to_string(index=False))
print("\n== BIM-08_C12: tríos ==")
print(T[T["Secuencia"] == "Planta__BIM-08_C12"][["Fecha", "OD", "hora", "dh_horas", "e_log", "e_norm"]]
        .round(3).to_string(index=False))
print("\n== RMSE LOO observado vs esperable solo por ruido ==\n", SIM.to_string(index=False))
print(f"\nGuardado en {OUT}/diagnostico_ruido_od.xlsx")
