import pandas as pd
import numpy as np

datos = pd.read_excel(
    "evaluacion_secuencias_final.xlsx",
    sheet_name="Detalle_OD"
)

resumen = pd.read_excel(
    "evaluacion_secuencias_final.xlsx",
    sheet_name="Resumen_secuencias"
)

resultados = []

for secuencia, g in datos.groupby("Secuencia"):
    g = g.sort_values("Edad").copy()

    edad = g["Edad"].to_numpy(dtype=float)
    od = g["OD"].to_numpy(dtype=float)

    if len(g) < 2:
        continue

    diferencias = np.diff(od)
    diferencias_edad = np.diff(edad)

    pendientes = np.divide(
        diferencias,
        diferencias_edad,
        out=np.full(len(diferencias), np.nan),
        where=diferencias_edad != 0
    )

    mitad = max(1, len(pendientes) // 2)

    pendiente_inicial = np.nanmean(pendientes[:mitad])
    pendiente_final = np.nanmean(pendientes[mitad:])

    posicion_maximo = int(np.argmax(od))
    edad_maximo = edad[posicion_maximo]
    od_maximo = od[posicion_maximo]

    resultados.append({
        "Secuencia": secuencia,
        "N_OD": len(od),
        "Edad_inicial": edad[0],
        "Edad_final": edad[-1],
        "OD_inicial": od[0],
        "OD_maxima": od_maximo,
        "Edad_OD_maxima": edad_maximo,
        "OD_final": od[-1],
        "Pendiente_inicial": pendiente_inicial,
        "Pendiente_final": pendiente_final,
        "Aumentos": int((diferencias > 0).sum()),
        "Descensos": int((diferencias < 0).sum()),
        "Estables": int((diferencias == 0).sum()),
        "OD_maximo_al_final": posicion_maximo == len(od) - 1
    })

forma = pd.DataFrame(resultados)

forma = forma.merge(
    resumen[["Secuencia", "Clasificacion"]],
    on="Secuencia",
    how="left"
)

forma = forma.sort_values(
    ["N_OD", "Pendiente_inicial"],
    ascending=[False, False]
)

forma.to_excel("resumen_forma_curvas.xlsx", index=False)

print("RESUMEN DE FORMA GENERADO")
print("Secuencias:", len(forma))
print("\n")
print(forma.round(4).to_string(index=False))
