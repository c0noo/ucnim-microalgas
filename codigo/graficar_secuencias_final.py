import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import tarfile

archivo = "evaluacion_secuencias_final.xlsx"
datos = pd.read_excel(archivo, sheet_name="Detalle_OD")
resumen = pd.read_excel(archivo, sheet_name="Resumen_secuencias")

carpeta = "graficos_secuencias_finales"
os.makedirs(carpeta, exist_ok=True)

# Graficar secuencias con al menos 5 mediciones
seleccion = resumen[resumen["N_OD_con_edad"] >= 5]

for _, fila in seleccion.iterrows():
    secuencia = fila["Secuencia"]
    grupo = datos[datos["Secuencia"] == secuencia].copy()
    grupo = grupo.sort_values("Edad")

    if grupo.empty:
        continue

    nombre = re.sub(r"[^A-Za-z0-9_-]+", "_", str(secuencia))

    plt.figure(figsize=(9, 5))
    plt.plot(
        grupo["Edad"],
        grupo["OD"],
        marker="o",
        linewidth=1.8
    )

    for _, punto in grupo.iterrows():
        plt.annotate(
            f'{punto["OD"]:.2f}',
            (punto["Edad"], punto["OD"]),
            textcoords="offset points",
            xytext=(0, 7),
            ha="center",
            fontsize=8
        )

    plt.xlabel("Días de cultivo registrados")
    plt.ylabel("Densidad óptica (OD)")
    plt.title(
        f'{secuencia}\n'
        f'{fila["N_OD_con_edad"]} mediciones | '
        f'{fila["Clasificacion"]}'
    )
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(carpeta, nombre + ".png"),
        dpi=160
    )
    plt.close()

# Crear archivo comprimido
with tarfile.open("graficos_secuencias_finales.tar.gz", "w:gz") as tar:
    tar.add(carpeta, arcname=carpeta)

print("Gráficos generados:", len(seleccion))
print("Carpeta:", carpeta)
print("Archivo: graficos_secuencias_finales.tar.gz")

print("\nSECUENCIAS GRAFICADAS:")
print(seleccion[[
    "Ciclo_ID", "Secuencia", "N_OD_con_edad", "Clasificacion"
]].to_string(index=False))
