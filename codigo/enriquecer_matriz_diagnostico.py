"""
Enriquece la matriz de diagnóstico ya existente (24 filas) con:
  - chequeo de que sus errores sean efectivamente LOO
  - tasas por día (normaliza huecos entre registros)
  - posición borde/interior y leverage (efecto mecánico de extrapolación)
  - diagnóstico de dilución (OD y EC esperadas)
  - cambios operacionales (estado, aire, luces)
  - z robustos intra-secuencia y lista de variables con cambio inusual
No asume causalidad: marca coincidencias.
Ejecutar desde ~/UCNIM/resultados_epica1/
"""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----------------------------- rutas / parámetros -----------------------------
F_MATRIZ = Path("matriz_diagnostico_operacional/matriz_diagnostico_ambiental_operacional.xlsx")
F_LOO = Path("validacion_loo/resultados_validacion_loo.xlsx")
F_DET = Path("analisis_residuos_loo/analisis_residuos_y_predicciones.xlsx")
OUT_DIR = Path("matriz_diagnostico_operacional")
OUT_XLSX = OUT_DIR / "matriz_diagnostico_enriquecida.xlsx"
OUT_PNG = OUT_DIR / "graficos_enriquecida"
OUT_PNG.mkdir(parents=True, exist_ok=True)

KEY = ["Secuencia", "Días cultivo"]
VOL_EVENT_THR = 0.05   # |ΔV|/V_prev > 5 % => evento de volumen
Z_THR = 1.5            # |z robusto| de la tasa > 1.5 => cambio "inusual"
GAP_THR = 1.5          # días entre registros > 1.5 => hueco


# ----------------------------- utilidades -----------------------------
def z_robusto(s):
    """z con mediana/MAD; si MAD=0 usa desvío estándar; si ambos 0 devuelve 0."""
    s = pd.Series(s, dtype=float)
    med = s.median()
    esc = 1.4826 * (s - med).abs().median()
    if not np.isfinite(esc) or esc == 0:
        esc = s.std(ddof=0)
    if not np.isfinite(esc) or esc == 0:
        return pd.Series(np.where(s.notna(), 0.0, np.nan), index=s.index)
    return (s - med) / esc


def a_binario(s):
    """'Sí'->1, 'No'->0, cualquier otra cosa (incl. NaN) -> NaN (NO se asume apagado)."""
    return s.map({"Sí": 1, "No": 0})


# ----------------------------- carga y chequeos -----------------------------
M = pd.read_excel(F_MATRIZ, sheet_name="Matriz_diagnostico")
M["Fecha"] = pd.to_datetime(M["Fecha"])
loo = pd.read_excel(F_LOO, sheet_name="Detalle_LOO")
det = pd.read_excel(F_DET, sheet_name="Detalle_observaciones")

assert not M.duplicated(KEY).any(), "Hay (Secuencia, Días cultivo) duplicados en la matriz"

# 1) ¿Los errores de la matriz son los del LOO?
loo_k = (loo.rename(columns={"Edad_retirada": "Días cultivo"})
            [KEY + ["Error_exponencial", "Error_baranyi"]]
            .rename(columns={"Error_exponencial": "_e_exp_loo",
                             "Error_baranyi": "_e_bar_loo"}))
M = M.merge(loo_k, on=KEY, how="left", validate="1:1")
chequeo = (M.assign(dif_max_exp=(M["Error_exponencial"] - M["_e_exp_loo"]).abs(),
                    dif_max_bar=(M["Error_baranyi"] - M["_e_bar_loo"]).abs())
             .groupby("Secuencia")[["dif_max_exp", "dif_max_bar"]].max())
chequeo["errores_son_LOO"] = (chequeo.max(axis=1) < 1e-6)
M = M.drop(columns=["_e_exp_loo", "_e_bar_loo"])

# 2) Traer μ reportado y marca de inicio tras descarte
extra = (det[KEY + ["μ (d⁻¹)", "Inicio_Tras_Descarte"]]
         .drop_duplicates(KEY).rename(columns={"μ (d⁻¹)": "mu_reportado"}))
M = M.merge(extra, on=KEY, how="left", validate="1:1")


# ----------------------------- enriquecimiento por secuencia -----------------------------
def enriquecer(g):
    g = g.sort_values("Fecha").reset_index(drop=True).copy()
    n = len(g)
    t = (g["Fecha"] - g["Fecha"].iloc[0]).dt.total_seconds().to_numpy() / 86400
    g["idx"] = np.arange(n)
    g["t_dias"] = t
    g["dt_dias"] = pd.Series(t).diff()
    g["hueco"] = g["dt_dias"] > GAP_THR

    # Efecto mecánico de extrapolación: bordes y leverage (aprox. log-lineal)
    g["posicion"] = np.where(g["idx"].isin([0, n - 1]), "borde", "interior")
    sxx = ((t - t.mean()) ** 2).sum()
    g["leverage_aprox"] = 1 / n + (t - t.mean()) ** 2 / sxx if sxx > 0 else np.nan

    # Error del modelo exponencial (Error = OD - pred; negativo = sobreestima)
    g["err_rel_pct"] = 100 * g["Error_exponencial"] / g["OD_predicha_exponencial"]
    g["err_log"] = np.log(g["OD"]) - np.log(g["OD_predicha_exponencial"])
    g["z_err_exp"] = z_robusto(g["Error_exponencial"])

    # Crecimiento observado y tasas por día (los Cambio_* son por registro)
    g["mu_obs"] = np.log(g["OD"] / g["OD"].shift(1)) / g["dt_dias"]
    g["dOD_dia"] = g["OD"].diff() / g["dt_dias"]
    for var, lab in [("pH", "pH"), ("Temperatura (°C)", "T"), ("EC", "EC")]:
        g[f"tasa_{lab}"] = g[f"Cambio_{var}"] / g["dt_dias"]
        g[f"z_tasa_{lab}"] = z_robusto(g[f"tasa_{lab}"])

    # Volumen y diagnóstico de dilución
    V, Vp = g["Volumen (L)"], g["Volumen (L)"].shift(1)
    g["vol_rel"] = V / Vp - 1
    g["z_vol_rel"] = z_robusto(g["vol_rel"])
    g["evento_vol"] = g["vol_rel"].abs() > VOL_EVENT_THR
    g["OD_esperada_dilucion"] = (g["OD"].shift(1) * Vp / V).where(g["evento_vol"])
    g["EC_esperada_si_agua"] = (g["EC"].shift(1) * Vp / V).where(g["evento_vol"])
    g["ratio_OD_vs_dilucion"] = g["OD"] / g["OD_esperada_dilucion"]   # >1: OD mayor que la dilución pura
    g["ratio_EC_vs_agua"] = g["EC"] / g["EC_esperada_si_agua"]        # ~1: el líquido agregado NO era agua

    # Cambios operacionales (NaN en Aire/Luces NO se interpreta como apagado)
    for col, lab in [("Luces encendidas", "luces"), ("Aire encendido", "aire")]:
        b = a_binario(g[col])
        g[f"d_{lab}"] = b.diff()
        g[f"{lab}_NaN"] = g[col].isna()
    g["d_n_luces"] = g["Cantidad luces"].diff()
    g["cambio_estado"] = (g["Estado"] != g["Estado"].shift(1)) & g["Estado"].notna() \
                         & g["Estado"].shift(1).notna()

    # Coincidencias (descriptivas, no causales)
    def flags(r):
        f = []
        if r["evento_vol"]:
            f.append("vol")
        for lab in ["pH", "T", "EC"]:
            z = r[f"z_tasa_{lab}"]
            if pd.notna(z) and abs(z) > Z_THR:
                f.append(lab)
        if r["cambio_estado"]:
            f.append("estado")
        if pd.notna(r["d_aire"]) and r["d_aire"] != 0:
            f.append("aire")
        if pd.notna(r["d_luces"]) and r["d_luces"] != 0:
            f.append("luces")
        if pd.notna(r["d_n_luces"]) and r["d_n_luces"] != 0:
            f.append("n_luces")
        return ",".join(f)
    g["vars_cambio_inusual"] = g.apply(flags, axis=1)
    return g


E = pd.concat([enriquecer(g) for _, g in M.groupby("Secuencia", sort=False)],
              ignore_index=True)


# ----------------------------- tablas de revisión -----------------------------
COLS_TOP = ["Secuencia", "Días cultivo", "Fecha", "posicion", "leverage_aprox", "dt_dias",
            "OD", "OD_predicha_exponencial", "Error_exponencial", "err_rel_pct", "z_err_exp",
            "mu_obs", "tasa_pH", "tasa_T", "tasa_EC", "vol_rel", "Cambio_Volumen (L)",
            "ratio_OD_vs_dilucion", "ratio_EC_vs_agua", "Aire encendido", "Estado", "Ritmo",
            "vars_cambio_inusual"]


def top_desv(df, k=4, solo_interior=False):
    d = df[df["posicion"] == "interior"] if solo_interior else df
    return (d.assign(abs_err=d["Error_exponencial"].abs())
             .sort_values(["Secuencia", "abs_err"], ascending=[True, False])
             .groupby("Secuencia").head(k)[COLS_TOP].round(4))


def asociaciones(df, feats, tgts, nombre):
    """Spearman descriptivo. n≈7-10 por secuencia: usar solo para priorizar, no concluir."""
    filas = []
    for f in feats:
        for tg, lab in tgts:
            x = df[[f, tg]].dropna()
            if len(x) >= 5 and x[f].nunique() > 1 and x[tg].nunique() > 1:
                rho, p = spearmanr(x[f], x[tg])
                filas.append(dict(ambito=nombre, variable=f, objetivo=lab, n=len(x),
                                  rho=round(rho, 3), p=round(p, 3)))
    return pd.DataFrame(filas)


E["abs_err"] = E["Error_exponencial"].abs()
E["abs_z_err"] = E["z_err_exp"].abs()
feats = ["tasa_pH", "tasa_T", "tasa_EC", "vol_rel", "mu_obs"]
tgts = [("Error_exponencial", "error signado"), ("abs_err", "|error|")]
asoc = pd.concat(
    [asociaciones(g, feats, tgts, s) for s, g in E.groupby("Secuencia")] +
    [asociaciones(E, ["z_tasa_pH", "z_tasa_T", "z_tasa_EC", "z_vol_rel"],
                  [("z_err_exp", "z error signado"), ("abs_z_err", "|z error|")],
                  "TODAS (z intra-secuencia)")],
    ignore_index=True)

cat_cols = ["Luces encendidas", "Aire encendido", "Estado", "Ritmo", "Cantidad luces"]
calidad = (E.groupby("Secuencia")[cat_cols]
             .agg(lambda s: f"NaN={s.isna().sum()}; valores={sorted(map(str, s.dropna().unique()))}")
             .reset_index())


# ----------------------------- gráficos -----------------------------
def graficar(d, seq):
    fig, ax = plt.subplots(5, 1, figsize=(9, 12), sharex=True)
    ax[0].plot(d.t_dias, d.OD, "o-", label="OD obs")
    ax[0].plot(d.t_dias, d.OD_predicha_exponencial, "s--", label="Pred. exp. (LOO)")
    ax[0].plot(d.t_dias, d.OD_predicha_baranyi, "^:", label="Pred. Baranyi (LOO)", alpha=.6)
    ax[0].scatter(d.t_dias[d.OD_esperada_dilucion.notna()],
                  d.OD_esperada_dilucion.dropna(), marker="x", c="k", label="Esperada solo dilución")
    ax[0].set_ylabel("OD"); ax[0].legend(fontsize=8); ax[0].set_title(seq)
    ax[1].bar(d.t_dias, d.err_rel_pct,
              color=np.where(d.posicion == "borde", "lightgray", "tab:red"), width=.4)
    ax[1].axhline(0, c="k", lw=.5); ax[1].set_ylabel("Error LOO exp (%)\n(gris = borde)")
    ax[2].plot(d.t_dias, d["Volumen (L)"], "o-"); ax[2].set_ylabel("Volumen (L)")
    ax[3].plot(d.t_dias, d["Temperatura (°C)"], "o-", c="tab:orange"); ax[3].set_ylabel("Temp (°C)")
    ax[4].plot(d.t_dias, d.pH, "o-", c="tab:green"); ax[4].set_ylabel("pH")
    a2 = ax[4].twinx(); a2.plot(d.t_dias, d.EC, "s--", c="tab:purple"); a2.set_ylabel("EC")
    ax[4].set_xlabel("t desde primer registro (días)")
    for a in ax:
        for tv in d.t_dias[d.evento_vol]:
            a.axvline(tv, c="gray", ls=":", lw=.9)
        for tv in d.t_dias[d["cambio_estado"]]:
            a.axvline(tv, c="tab:blue", ls="--", lw=.6)
    plt.tight_layout()
    fig.savefig(OUT_PNG / f"{seq}_diagnostico.png", dpi=150)
    plt.close(fig)


for s, g in E.groupby("Secuencia"):
    graficar(g, s)


# ----------------------------- salida -----------------------------
with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as xw:
    E.drop(columns=["abs_err", "abs_z_err"]).to_excel(xw, sheet_name="Matriz_enriquecida", index=False)
    top_desv(E, 4, False).to_excel(xw, sheet_name="Top_desviaciones", index=False)
    top_desv(E, 4, True).to_excel(xw, sheet_name="Top_desv_solo_interior", index=False)
    asoc.to_excel(xw, sheet_name="Asociaciones_descriptivas", index=False)
    calidad.to_excel(xw, sheet_name="Calidad_categoricas", index=False)
    chequeo.reset_index().to_excel(xw, sheet_name="Chequeo_es_LOO", index=False)

pd.set_option("display.width", 220, "display.max_columns", 40)
print("\n== ¿Los errores de la matriz son LOO? ==\n", chequeo)
print("\n== Calidad variables categóricas ==\n", calidad.to_string())
print("\n== BIM-08_C12: top 4 desviaciones (todas) ==")
print(top_desv(E[E.Secuencia == "Planta__BIM-08_C12"], 4, False).T.to_string())
print("\n== Eventos de volumen (todas las secuencias) ==")
print(E.loc[E.evento_vol, ["Secuencia", "Días cultivo", "Volumen (L)", "vol_rel", "OD",
                           "OD_esperada_dilucion", "ratio_OD_vs_dilucion", "EC",
                           "ratio_EC_vs_agua", "Error_exponencial"]].round(3).to_string())
print(f"\nGuardado: {OUT_XLSX}\nGráficos: {OUT_PNG}/")
