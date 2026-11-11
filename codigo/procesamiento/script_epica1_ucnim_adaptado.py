"""
UCNIM - Épica 1: preparación, segmentación y caracterización inicial
Proyecto TACHI - historial de monitoreos de microalgas.

Entrada esperada:
  historial-monitoreos-2026-09-09.xlsx
  Hoja: Monitoreos (o primera hoja si no existe ese nombre)

Reglas metodológicas:
- Estado = 'Descarte' cierra el ciclo actual. El registro de descarte
  permanece asignado al ciclo que termina; el siguiente registro inicia otro.
- Los ciclos se identifican por Localidad + BIM + número de ciclo.
- Reinicios de Días cultivo sin descarte se MARCAN para revisión, pero no
  generan automáticamente un ciclo nuevo.
- No se eliminan filas por tener OD faltante ni valores extremos.
- Los duplicados se identifican, pero se conservan.
- No se estima fecha de cosecha ni se ajusta un modelo ODE en esta etapa:
  el Excel no contiene una etiqueta explícita de cosecha ni su criterio.

Instalación (si hace falta):
  pip install pandas numpy matplotlib openpyxl

Ejecución:
  python3 script_epica1_ucnim_adaptado.py
"""

from pathlib import Path
import re
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# 0. CONFIGURACIÓN
# -----------------------------------------------------------------------------

ARCHIVO_ENTRADA = Path("historial-monitoreos-2026-09-09.xlsx")
HOJA_PREFERIDA = "Monitoreos"
CARPETA_SALIDA = Path("resultados_epica1")

COL_FECHA = "Fecha"
COL_LOCALIDAD = "Localidad"
COL_RECIPIENTE = "BIM"
COL_ESTADO = "Estado"
COL_DIAS = "Días cultivo"
COL_OD = "OD"
COL_VOLUMEN = "Volumen (L)"
COL_RITMO = "Ritmo"

# Se marca para revisión cualquier OD por encima de este valor.
# No es un límite biológico ni provoca eliminación de datos.
OD_ALTO_REVISION = 5.0

# Se considera reinicio fuerte sospechoso si el contador baja al menos
# 5 días y vuelve a 0 o 1, sin un descarte registrado entre ambos datos.
CAIDA_DIAS_REINICIO = 5
DIAS_INICIO_REINICIO = 1

CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------
# 1. FUNCIONES AUXILIARES
# -----------------------------------------------------------------------------

def normalizar_texto(serie):
    return serie.astype("string").str.strip()


def nombre_archivo(texto):
    texto = str(texto)
    texto = re.sub(r"[^A-Za-z0-9_-]+", "_", texto)
    return texto.strip("_")[:100]


def leer_excel():
    if not ARCHIVO_ENTRADA.exists():
        raise FileNotFoundError(
            f"No se encontró {ARCHIVO_ENTRADA}. Deja el Excel en la misma "
            "carpeta que este script o cambia ARCHIVO_ENTRADA al inicio."
        )

    xls = pd.ExcelFile(ARCHIVO_ENTRADA)
    if HOJA_PREFERIDA in xls.sheet_names:
        hoja = HOJA_PREFERIDA
    else:
        hoja = 0
        warnings.warn(
            f"No existe la hoja '{HOJA_PREFERIDA}'. Se utilizará la primera: "
            f"{xls.sheet_names[0]}"
        )

    df = pd.read_excel(ARCHIVO_ENTRADA, sheet_name=hoja)
    return df, hoja


# -----------------------------------------------------------------------------
# 2. CARGA Y CONTROL DE CALIDAD
# -----------------------------------------------------------------------------

def cargar_y_revisar():
    df, hoja = leer_excel()
    n_original = len(df)
    df["Fila_Excel_Original"] = np.arange(2, n_original + 2)

    requeridas = [COL_FECHA, COL_LOCALIDAD, COL_RECIPIENTE, COL_ESTADO, COL_OD]
    faltantes = [c for c in requeridas if c not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas en el Excel: {faltantes}")

    # Convertir tipos sin descartar filas.
    df[COL_FECHA] = pd.to_datetime(df[COL_FECHA], errors="coerce")
    columnas_numericas = [COL_OD, COL_DIAS, COL_VOLUMEN, "pH",
                          "Temperatura (°C)", "EC", "μ (d⁻¹)"]
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in [COL_LOCALIDAD, COL_RECIPIENTE, COL_ESTADO, COL_RITMO]:
        if col in df.columns:
            df[col] = normalizar_texto(df[col])

    # Indicadores de calidad. Se conserva todo.
    df["Fecha_Invalida"] = df[COL_FECHA].isna()
    df["Identificador_Faltante"] = (
        df[COL_LOCALIDAD].isna() | df[COL_RECIPIENTE].isna()
    )
    df["OD_Faltante"] = df[COL_OD].isna()
    df["OD_Negativa"] = df[COL_OD].notna() & (df[COL_OD] < 0)
    df["OD_Alta_Revisar"] = df[COL_OD].notna() & (df[COL_OD] > OD_ALTO_REVISION)
    df["Dias_Cultivo_Negativos"] = (
        df[COL_DIAS].notna() & (df[COL_DIAS] < 0)
        if COL_DIAS in df.columns else False
    )

    # Duplicados exactos: marcar todas las filas repetidas, sin borrarlas.
    columnas_originales = [c for c in df.columns if c not in [
        "Fila_Excel_Original", "Duplicado_Exacto"
    ]]
    df["Duplicado_Exacto"] = df.duplicated(
        subset=columnas_originales, keep=False
    )

    # El identificador de agrupación se construye con localidad + recipiente.
    df["Grupo_Recipiente"] = (
        df[COL_LOCALIDAD].fillna("SIN_LOCALIDAD").astype(str).str.strip()
        + "__"
        + df[COL_RECIPIENTE].fillna("SIN_ID").astype(str).str.strip()
    )

    # No se puede ordenar/segmentar cronológicamente una fecha inválida.
    df = df.sort_values(
        ["Grupo_Recipiente", COL_FECHA, "Fila_Excel_Original"],
        na_position="last"
    ).reset_index(drop=True)

    calidad = [
        ("Hoja utilizada", hoja),
        ("Registros originales", n_original),
        ("Fechas inválidas", int(df["Fecha_Invalida"].sum())),
        ("Identificadores faltantes", int(df["Identificador_Faltante"].sum())),
        ("OD faltante", int(df["OD_Faltante"].sum())),
        ("OD negativa", int(df["OD_Negativa"].sum())),
        (f"OD superior a {OD_ALTO_REVISION} (revisar)", int(df["OD_Alta_Revisar"].sum())),
        ("Duplicados exactos (filas marcadas)", int(df["Duplicado_Exacto"].sum())),
        ("Grupos localidad-recipiente", int(df["Grupo_Recipiente"].nunique())),
        ("Filas conservadas", len(df)),
    ]

    return df, pd.DataFrame(calidad, columns=["Indicador", "Valor"])


# -----------------------------------------------------------------------------
# 3. SEGMENTACIÓN DE CICLOS CON ESTADO = DESCARTE
# -----------------------------------------------------------------------------

def segmentar_ciclos(df):
    partes = []

    # Filas sin fecha o identificador se conservan, pero no se asignan a ciclo.
    asignables = df[
        df[COL_FECHA].notna()
        & df[COL_LOCALIDAD].notna()
        & df[COL_RECIPIENTE].notna()
    ].copy()
    no_asignables = df.drop(index=asignables.index).copy()
    no_asignables["Numero_Ciclo"] = pd.NA
    no_asignables["Ciclo_ID"] = "SIN_CICLO_REVISION"
    no_asignables["Motivo_Revision_Ciclo"] = "Fecha o identificador faltante"
    no_asignables["Cierre_Ciclo_Descarte"] = False
    no_asignables["Inicio_Tras_Descarte"] = False

    for grupo_id, g in asignables.groupby("Grupo_Recipiente", sort=False):
        g = g.sort_values([COL_FECHA, "Fila_Excel_Original"]).copy()
        g["Dias_Entre_Registros"] = g[COL_FECHA].diff().dt.total_seconds() / 86400

        if COL_DIAS in g.columns:
            g["Cambio_Dias_Cultivo"] = g[COL_DIAS].diff()
            g["Reinicio_Dias_Sospechoso"] = (
                (g["Cambio_Dias_Cultivo"] <= -CAIDA_DIAS_REINICIO)
                & (g[COL_DIAS] <= DIAS_INICIO_REINICIO)
            )
        else:
            g["Cambio_Dias_Cultivo"] = np.nan
            g["Reinicio_Dias_Sospechoso"] = False

        # El descarte cierra el ciclo que está activo en esa fila.
        estado = g[COL_ESTADO].fillna("").astype(str).str.casefold().str.strip()
        es_descarte = estado.eq("descarte")

        numero_ciclo = []
        ciclo_actual = 1
        inicio_tras_descarte = []
        hubo_descarte_previo = False
        for es_cierre in es_descarte.tolist():
            numero_ciclo.append(ciclo_actual)
            inicio_tras_descarte.append(hubo_descarte_previo)
            if es_cierre:
                ciclo_actual += 1
                hubo_descarte_previo = True
            else:
                hubo_descarte_previo = False

        g["Numero_Ciclo"] = numero_ciclo
        g["Ciclo_ID"] = (
            g["Grupo_Recipiente"].astype(str)
            + "_C"
            + g["Numero_Ciclo"].astype(str).str.zfill(2)
        )
        g["Cierre_Ciclo_Descarte"] = es_descarte.to_numpy()
        g["Inicio_Tras_Descarte"] = inicio_tras_descarte
        g["Motivo_Revision_Ciclo"] = ""
        g.loc[g["Reinicio_Dias_Sospechoso"].fillna(False),
              "Motivo_Revision_Ciclo"] = (
            "Reinicio de Días cultivo sin descarte previo: verificar"
        )

        partes.append(g)

    resultado = pd.concat(partes + [no_asignables], ignore_index=True, sort=False)
    resultado = resultado.sort_values(
        ["Grupo_Recipiente", COL_FECHA, "Fila_Excel_Original"],
        na_position="last"
    ).reset_index(drop=True)
    return resultado


# -----------------------------------------------------------------------------
# 4. RESUMEN DE CICLOS Y PLANTILLA DE VALIDACIÓN
# -----------------------------------------------------------------------------

def resumir_ciclos(df):
    registros = []
    df_ciclos = df[df["Ciclo_ID"] != "SIN_CICLO_REVISION"].copy()

    for ciclo_id, g in df_ciclos.groupby("Ciclo_ID", sort=False):
        g = g.sort_values([COL_FECHA, "Fila_Excel_Original"])
        od = g[COL_OD].dropna() if COL_OD in g.columns else pd.Series(dtype=float)
        dias_fecha = (g[COL_FECHA].max() - g[COL_FECHA].min()).total_seconds() / 86400
        registros.append({
            "Ciclo_ID": ciclo_id,
            "Localidad": g[COL_LOCALIDAD].iloc[0],
            "Recipiente": g[COL_RECIPIENTE].iloc[0],
            "Fecha_Inicio": g[COL_FECHA].min(),
            "Fecha_Fin": g[COL_FECHA].max(),
            "N_Registros": len(g),
            "N_OD_Disponibles": int(g[COL_OD].notna().sum()),
            "Duracion_Fecha_Dias": round(dias_fecha, 2),
            "Dias_Cultivo_Min": g[COL_DIAS].min() if COL_DIAS in g.columns else np.nan,
            "Dias_Cultivo_Max": g[COL_DIAS].max() if COL_DIAS in g.columns else np.nan,
            "OD_Inicial": od.iloc[0] if len(od) else np.nan,
            "OD_Maxima": od.max() if len(od) else np.nan,
            "OD_Final": od.iloc[-1] if len(od) else np.nan,
            "Volumen_Min_L": g[COL_VOLUMEN].min() if COL_VOLUMEN in g.columns else np.nan,
            "Volumen_Max_L": g[COL_VOLUMEN].max() if COL_VOLUMEN in g.columns else np.nan,
            "Termina_En_Descarte": bool(g["Cierre_Ciclo_Descarte"].any()),
            "Tiene_OD_Alta": bool(g["OD_Alta_Revisar"].any()),
            "Tiene_Reinicio_Sospechoso": bool(g["Reinicio_Dias_Sospechoso"].fillna(False).any()),
            "Candidato_Revision": bool(g[COL_OD].notna().sum() >= 3),
        })

    return pd.DataFrame(registros)


def crear_plantilla_revision(resumen):
    columnas = [
        "Ciclo_ID", "Localidad", "Recipiente", "N_Registros",
        "N_OD_Disponibles", "Duracion_Fecha_Dias", "OD_Inicial",
        "OD_Maxima", "OD_Final", "Termina_En_Descarte",
        "Tiene_OD_Alta", "Tiene_Reinicio_Sospechoso", "Candidato_Revision"
    ]
    plantilla = resumen[columnas].copy()
    plantilla["Fase_Lag_Visible"] = ""
    plantilla["Fase_Exponencial_Visible"] = ""
    plantilla["Fase_Estacionaria_Visible"] = ""
    plantilla["Fase_Declive_Visible"] = ""
    plantilla["Curva_Util_Para_Analisis"] = ""
    plantilla["Observaciones_Revision"] = ""
    ruta = CARPETA_SALIDA / "plantilla_revision_manual.xlsx"
    plantilla.to_excel(ruta, index=False)
    return ruta


# -----------------------------------------------------------------------------
# 5. GRÁFICOS DE CURVAS
# -----------------------------------------------------------------------------

def graficar_ciclos(df):
    carpeta = CARPETA_SALIDA / "curvas_por_ciclo"
    carpeta.mkdir(parents=True, exist_ok=True)
    df_ciclos = df[df["Ciclo_ID"] != "SIN_CICLO_REVISION"].copy()

    for ciclo_id, g in df_ciclos.groupby("Ciclo_ID", sort=False):
        g = g.sort_values([COL_FECHA, "Fila_Excel_Original"]).copy()
        g_od = g[g[COL_OD].notna()].copy()
        if g_od.empty:
            continue

        # Eje X preferente: días de cultivo registrados; si no existen, días
        # transcurridos desde el primer monitoreo del ciclo.
        if COL_DIAS in g_od.columns and g_od[COL_DIAS].notna().sum() >= 2:
            x = g_od[COL_DIAS]
            etiqueta_x = "Días de cultivo registrados"
        else:
            x = (g_od[COL_FECHA] - g[COL_FECHA].min()).dt.total_seconds() / 86400
            etiqueta_x = "Días desde el primer monitoreo del ciclo"

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(x, g_od[COL_OD], marker="o", linewidth=1.5, label="OD")
        ax.set_xlabel(etiqueta_x)
        ax.set_ylabel("Densidad óptica (OD)")
        ax.set_title(f"Curva de OD - {ciclo_id}")
        ax.grid(True, alpha=0.3)

        # Marcar valores altos para inspección, sin quitarlos.
        altos = g_od[g_od["OD_Alta_Revisar"]]
        if not altos.empty:
            if COL_DIAS in altos.columns and etiqueta_x == "Días de cultivo registrados":
                x_altos = altos[COL_DIAS]
            else:
                x_altos = (altos[COL_FECHA] - g[COL_FECHA].min()).dt.total_seconds() / 86400
            ax.scatter(x_altos, altos[COL_OD], marker="x", s=80,
                       label="OD alta: revisar")
        ax.legend()
        fig.tight_layout()
        fig.savefig(carpeta / f"{nombre_archivo(ciclo_id)}.png", dpi=150)
        plt.close(fig)


def graficar_comparacion_por_recipiente(df):
    carpeta = CARPETA_SALIDA / "curvas_por_recipiente"
    carpeta.mkdir(parents=True, exist_ok=True)
    df_ciclos = df[df["Ciclo_ID"] != "SIN_CICLO_REVISION"].copy()

    for grupo_id, g in df_ciclos.groupby("Grupo_Recipiente", sort=False):
        fig, ax = plt.subplots(figsize=(10, 5))
        tiene_curva = False
        for ciclo_id, gc in g.groupby("Ciclo_ID", sort=False):
            gc = gc.sort_values(COL_FECHA)
            gc = gc[gc[COL_OD].notna()]
            if gc.empty:
                continue
            if COL_DIAS in gc.columns and gc[COL_DIAS].notna().sum() >= 2:
                x = gc[COL_DIAS]
            else:
                x = (gc[COL_FECHA] - gc[COL_FECHA].min()).dt.total_seconds() / 86400
            ax.plot(x, gc[COL_OD], marker="o", label=ciclo_id)
            tiene_curva = True
        if tiene_curva:
            ax.set_xlabel("Días de cultivo (o días desde inicio del ciclo)")
            ax.set_ylabel("Densidad óptica (OD)")
            ax.set_title(f"Comparación de ciclos - {grupo_id}")
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=7)
            fig.tight_layout()
            fig.savefig(carpeta / f"{nombre_archivo(grupo_id)}.png", dpi=150)
        plt.close(fig)


# -----------------------------------------------------------------------------
# 6. EJECUCIÓN
# -----------------------------------------------------------------------------

def main():
    print("[1/6] Cargando Excel y revisando calidad...")
    df, calidad = cargar_y_revisar()

    print("[2/6] Segmentando ciclos con Estado = Descarte...")
    df = segmentar_ciclos(df)

    print("[3/6] Generando resumen de ciclos...")
    resumen = resumir_ciclos(df)

    print("[4/6] Generando gráficos por ciclo y recipiente...")
    graficar_ciclos(df)
    graficar_comparacion_por_recipiente(df)

    print("[5/6] Exportando archivos...")
    df.to_excel(CARPETA_SALIDA / "datos_procesados_todos.xlsx", index=False)
    resumen.to_excel(CARPETA_SALIDA / "resumen_ciclos.xlsx", index=False)
    calidad.to_excel(CARPETA_SALIDA / "informe_calidad_inicial.xlsx", index=False)
    plantilla = crear_plantilla_revision(resumen)

    no_asignables = df[df["Ciclo_ID"] == "SIN_CICLO_REVISION"]
    if not no_asignables.empty:
        no_asignables.to_excel(
            CARPETA_SALIDA / "registros_sin_ciclo_para_revision.xlsx", index=False
        )

    print("[6/6] Resumen de ejecución")
    print(f"Registros procesados: {len(df)}")
    print(f"Ciclos identificados: {resumen['Ciclo_ID'].nunique() if not resumen.empty else 0}")
    print(f"Ciclos que terminan en descarte: {int(resumen['Termina_En_Descarte'].sum()) if not resumen.empty else 0}")
    print(f"Ciclos con reinicio sospechoso: {int(resumen['Tiene_Reinicio_Sospechoso'].sum()) if not resumen.empty else 0}")
    print(f"Registros sin ciclo asignable: {len(no_asignables)}")
    print("\nProceso terminado.")
    print(f"Resultados: {CARPETA_SALIDA.resolve()}")
    print(f"Plantilla de revisión: {plantilla.resolve()}")
    print("Revisa primero resumen_ciclos.xlsx y las curvas antes de modelar.")


if __name__ == "__main__":
    main()
