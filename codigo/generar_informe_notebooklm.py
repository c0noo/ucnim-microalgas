
from pathlib import Path
from datetime import datetime

# ============================================================
# CONFIGURACION
# ============================================================

CARPETA_SALIDA = Path.home() / "UCNIM" / "resultados_epica1"

ARCHIVO_SALIDA = CARPETA_SALIDA / "informe_primer_ajuste_ODE_NotebookLM.md"

# ============================================================
# CONTENIDO DEL INFORME
# ============================================================

contenido = r"""
# Informe de resultados: primer ajuste de modelos ODE para curvas de crecimiento de microalgas

## 1. Contexto del análisis

Este documento presenta los resultados del primer ajuste de modelos
matemáticos a las secuencias de crecimiento de microalgas seleccionadas
en el proyecto.

El objetivo es caracterizar el comportamiento de la densidad óptica (OD)
a lo largo del tiempo de cultivo y evaluar la posibilidad de utilizar
modelos diferenciales para describir su evolución.

Se trabajó inicialmente con tres secuencias:

- Planta__BIM-08_C12
- Planta__BIM-02_C01
- Planta__BIM-02_C04

Estas secuencias fueron seleccionadas a partir de un proceso previo de
revisión de continuidad, disponibilidad de mediciones y consistencia
temporal.

Es importante señalar que la variable modelada es la densidad óptica
(OD), no la biomasa directamente. Para interpretar OD como biomasa
sería necesaria una calibración experimental.

## 2. Modelos evaluados

Se ajustaron dos modelos:

### 2.1. Modelo exponencial

Y(t) = a * exp(r * t)

Donde:

- Y(t): densidad óptica estimada.
- a: valor inicial estimado.
- r: parámetro de crecimiento.
- t: tiempo transcurrido desde la edad inicial de la secuencia.

Este modelo representa un crecimiento exponencial sin una limitación
explícita de capacidad de carga.

### 2.2. Modelo logístico

Y(t) = K / (1 + A * exp(-r * t))

Donde:

- Y(t): densidad óptica estimada.
- K: asíntota o capacidad de carga estimada.
- A: parámetro relacionado con la condición inicial.
- r: parámetro de crecimiento.
- t: tiempo transcurrido desde la edad inicial.

El modelo logístico permite representar un crecimiento que tiende a
estabilizarse en torno a una asíntota.

Sin embargo, la estimación de K requiere suficientes observaciones que
permitan identificar una tendencia de saturación. Un buen ajuste
numérico por sí solo no demuestra que la capacidad de carga haya sido
identificada.

## 3. Resultados del primer ajuste

### 3.1. Planta__BIM-08_C12

#### Modelo exponencial

- Parámetro a: 0.36241191
- Parámetro r: 0.04537107 d⁻¹
- Error estándar de a: 0.01477502
- Error estándar de r: 0.00532016
- RMSE: 0.02604773
- AICc: -67.24221

#### Modelo logístico

- K: 613.998953
- r: 0.04540550 d⁻¹
- A: 1693.21987
- Error estándar de K: 1,608,577.14
- Error estándar de r: 0.0923725
- Error estándar de A: 4,438,512.54
- RMSE: 0.02604954
- AICc: -62.95511

El parámetro K alcanzó el límite superior impuesto durante el ajuste.
Además, presenta una incertidumbre extremadamente elevada.

#### Sensibilidad al retirar una observación

Modelo exponencial:

- a: mínimo 0.354736; máximo 0.366830.
- r: mínimo 0.041653; máximo 0.047751.

Modelo logístico:

- K: mínimo 613.998953; máximo 614.000000.
- r: mínimo 0.041684; máximo 0.047787.
- A: mínimo 1672.820500; máximo 1729.891348.

#### Interpretación

El modelo exponencial presenta parámetros relativamente estables
cuando se retira una observación.

En el modelo logístico, K permanece prácticamente en el límite
superior impuesto. Por tanto, no existe evidencia suficiente para
interpretar ese valor como una capacidad de carga real del cultivo.

El modelo exponencial es la alternativa más razonable para esta
secuencia en esta etapa del análisis.

### 3.2. Planta__BIM-02_C01

#### Modelo exponencial

- Parámetro a: 0.67671453
- Parámetro r: 0.03956342 d⁻¹
- Error estándar de a: 0.02405027
- Error estándar de r: 0.00662282
- RMSE: 0.03414042
- AICc: -40.28182

#### Modelo logístico

- K: 985.999601
- r: 0.03959508 d⁻¹
- A: 1456.04426
- Error estándar de K: 6,240,413.86
- Error estándar de r: 0.2040053
- Error estándar de A: 9,221,614.08
- RMSE: 0.03414188
- AICc: -33.28123

El parámetro K alcanzó el límite superior impuesto durante el ajuste
y presentó una incertidumbre muy elevada.

#### Sensibilidad al retirar una observación

Modelo exponencial:

- a: mínimo 0.667412; máximo 0.690440.
- r: mínimo 0.030011; máximo 0.042037.

Modelo logístico:

- K: mínimo 0.986993; máximo 986.000000.
- r: mínimo 0.039248; máximo 0.141286.
- A: mínimo 0.447197; máximo 1476.352237.

La variación de los parámetros logísticos al retirar una observación
muestra una elevada inestabilidad.

#### Interpretación

El modelo exponencial presenta un comportamiento relativamente
estable y un ajuste similar al logístico.

El modelo logístico no permite estimar de forma confiable K.
Por ello, se prefiere el modelo exponencial como primera aproximación.

### 3.3. Planta__BIM-02_C04

#### Modelo exponencial

- Parámetro a: 0.45424336
- Parámetro r: 0.06439845 d⁻¹
- Error estándar de a: 0.00803065
- Error estándar de r: 0.00268793
- RMSE: 0.01219857
- AICc: -54.69011

#### Modelo logístico

- K: 1.25068056
- r: 0.13065635 d⁻¹
- A: 1.82312693
- Error estándar de K: 0.34961484
- Error estándar de r: 0.03835685
- Error estándar de A: 0.75109676
- RMSE: 0.00916233
- AICc: -51.69717

#### Sensibilidad al retirar una observación

Modelo exponencial:

- a: mínimo 0.449155; máximo 0.460168.
- r: mínimo 0.062684; máximo 0.067394.

Modelo logístico:

- K: mínimo 1.110463; máximo 2.074569.
- r: mínimo 0.095700; máximo 0.150843.
- A: mínimo 1.509756; máximo 3.642229.

#### Interpretación

El modelo logístico presenta un RMSE menor que el exponencial.
Sin embargo, su parámetro K varía considerablemente al retirar
observaciones.

Además, la secuencia contiene solamente siete mediciones y presenta
un intervalo de cuatro días entre las edades de cultivo 5 y 9.

Aunque el modelo logístico consigue un ajuste numéricamente mejor
según RMSE, no existe evidencia suficiente para afirmar que se haya
identificado una capacidad de carga.

## 4. Comparación entre modelos

| Secuencia | RMSE exponencial | RMSE logístico | AICc exponencial | AICc logístico |
|---|---:|---:|---:|---:|
| BIM-08_C12 | 0.026048 | 0.026050 | -67.242 | -62.955 |
| BIM-02_C01 | 0.034140 | 0.034142 | -40.282 | -33.281 |
| BIM-02_C04 | 0.012199 | 0.009162 | -54.690 | -51.697 |

En las tres secuencias, el AICc favorece al modelo exponencial.
En BIM-02_C04, el modelo logístico presenta menor RMSE, pero su
complejidad adicional no se justifica según AICc.

Los valores de AICc deben interpretarse como una comparación relativa
entre estos modelos, ajustados sobre los mismos datos de cada
secuencia. No constituyen una validación predictiva independiente.

## 5. Resultados de sensibilidad

La validación consistió en retirar una observación por vez y volver
a ajustar los modelos.

Los resultados muestran:

- BIM-08_C12: el parámetro r exponencial se mantiene entre 0.041653
  y 0.047751 d⁻¹.
- BIM-02_C01: el parámetro r exponencial se mantiene entre 0.030011
  y 0.042037 d⁻¹.
- BIM-02_C04: el parámetro r exponencial se mantiene entre 0.062684
  y 0.067394 d⁻¹.

En contraste, los modelos logísticos presentan parámetros K
inestables o fijados en el límite superior, especialmente en las
dos primeras secuencias.

Esta evaluación indica que los parámetros del modelo exponencial
son más robustos frente a la eliminación individual de observaciones.
No obstante, esta prueba no reemplaza una validación con datos
independientes.

## 6. Consideraciones metodológicas

1. La variable dependiente es OD, no biomasa directamente.
2. Los parámetros r estimados describen la tasa de cambio relativa
   de OD bajo el modelo ajustado. No deben confundirse con la variable
   experimental μ (d⁻¹).
3. Las secuencias contienen pocas observaciones: siete en BIM-02_C01,
   siete en BIM-02_C04 y diez en BIM-08_C12.
4. Los tamaños muestrales reducidos limitan la identificación de
   modelos con varios parámetros.
5. Los datos presentan intervalos temporales desiguales.
6. La ausencia de una asíntota observada dificulta identificar K
   en el modelo logístico.
7. La estabilidad al retirar una observación es una evaluación de
   sensibilidad, no una demostración de capacidad predictiva.
8. No se debe interpretar automáticamente una disminución de OD
   como muerte celular ni un aumento como crecimiento biológico
   confirmado.
9. Las fases de crecimiento deben contrastarse con información
   experimental y operacional adicional.

## 7. Conclusiones preliminares

- El modelo exponencial constituye la alternativa de referencia
  para las tres secuencias evaluadas.
- BIM-08_C12 y BIM-02_C01 muestran parámetros exponenciales
  relativamente estables.
- BIM-02_C04 presenta un mejor RMSE logístico, pero el AICc favorece
  al exponencial y la estimación de K sigue siendo incierta.
- No se ha demostrado que las secuencias hayan alcanzado una fase
  estacionaria ni que se haya identificado una capacidad de carga.
- Los resultados deben considerarse exploratorios debido al bajo
  número de observaciones y a la ausencia de validación independiente.

## 8. Próximos pasos propuestos

1. Realizar una validación temporal progresiva, ajustando con las
   primeras observaciones y prediciendo la siguiente.
2. Comparar las predicciones mediante MAE y RMSE.
3. Evaluar la sensibilidad de los resultados a los intervalos
   temporales y a las observaciones atípicas.
4. Revisar si existen secuencias adicionales con suficiente
   continuidad y disponibilidad de variables.
5. Evaluar la incorporación de variables ambientales, como pH,
   temperatura, aireación e iluminación, solo cuando exista
   suficiente información y fundamento experimental.
6. Contrastar las tendencias matemáticas con el conocimiento
   operacional y biológico del equipo de TACHI.

## 9. Preguntas abiertas para revisión del proyecto

- ¿Qué relación experimental existe entre OD y biomasa para las
  microalgas estudiadas?
- ¿Qué condiciones operacionales determinan el término de un cultivo?
- ¿Existe un umbral de OD utilizado para tomar decisiones de cosecha
  o descarte?
- ¿Las mediciones disponibles cubren realmente el ciclo completo
  de crecimiento?
- ¿Qué variables ambientales tienen suficiente cobertura y
  variabilidad para incorporarse a un modelo?
- ¿Es posible obtener más mediciones por cultivo para mejorar
  la identificación de los parámetros?

---

Documento generado para complementar los antecedentes del proyecto.
Los resultados deben contrastarse con los archivos fuente y las
decisiones metodológicas documentadas previamente.
"""

# ============================================================
# GENERAR ARCHIVO
# ============================================================

CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)

with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as archivo:
    archivo.write(contenido)

print("Informe generado correctamente.")
print(f"Archivo: {ARCHIVO_SALIDA}")
print(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
