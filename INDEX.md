# Índice de archivos — ucnim-microalgas

Proyecto UCNIM / TACHI Microalgas: modelamiento de OD en *Chlorella vulgaris*.
Cada archivo enlaza a su versión *raw* (texto plano).

## Informes

- [informes/informe_primer_ajuste_ODE_NotebookLM.md](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/informes/informe_primer_ajuste_ODE_NotebookLM.md)

## Código

| Archivo | Descripción (1ª línea del docstring) | URL raw |
|---|---|---|
| `ajustar_modelos_iniciales.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/ajustar_modelos_iniciales.py) |
| `analizar_errores_validacion.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/analizar_errores_validacion.py) |
| `analizar_incrementos_od.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/analizar_incrementos_od.py) |
| `analizar_residuos_loo.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/analizar_residuos_loo.py) |
| `analizar_sensibilidad_baranyi.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/analizar_sensibilidad_baranyi.py) |
| `auditar_tendencias.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/auditar_tendencias.py) |
| `auditoria_cobertura.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/auditoria_cobertura.py) |
| `caracterizar_variables.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/caracterizar_variables.py) |
| `construir_matriz_diagnostico.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/construir_matriz_diagnostico.py) |
| `diagnostico_regimen_crecimiento.py` | Heterogeneidad de tasa de crecimiento y covariables con rezago. | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/diagnostico_regimen_crecimiento.py) |
| `diagnostico_ruido_od.py` | Ruido de medición de OD (escala log) y efecto de la hora de lectura. | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/diagnostico_ruido_od.py) |
| `enriquecer_matriz_diagnostico.py` | Enriquece la matriz de diagnóstico ya existente (24 filas) con: | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/enriquecer_matriz_diagnostico.py) |
| `evaluar_secuencias.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/evaluar_secuencias.py) |
| `generar_atlas_y_validacion.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/generar_atlas_y_validacion.py) |
| `generar_informe_notebooklm.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/generar_informe_notebooklm.py) |
| `graficar_secuencias_final.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/graficar_secuencias_final.py) |
| `inspeccionar_esquema.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/inspeccionar_esquema.py) |
| `inspeccionar_esquema2.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/inspeccionar_esquema2.py) |
| `primer_ajuste_ode.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/primer_ajuste_ode.py) |
| `resumen_forma_curvas.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/resumen_forma_curvas.py) |
| `revisar_datos_ode.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/revisar_datos_ode.py) |
| `validacion_origen_movil.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/validacion_origen_movil.py) |
| `validar_ajustes_ode.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/validar_ajustes_ode.py) |
| `validar_estabilidad_loo.py` |  | [raw](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/codigo/validar_estabilidad_loo.py) |

## Datos (CSV exportados de los .xlsx)

### [datos_procesados_corregidos__Sheet1.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/datos_procesados_corregidos__Sheet1.csv)
origen: datos_procesados_corregidos.xlsx / hoja 'Sheet1' — 746 filas x 34 columnas

Columnas: Fecha, Localidad, BIM, pH, Temperatura (°C), EC, Volumen (L), Luces encendidas, Cantidad luces, Aire encendido, Días cultivo, OD, μ (d⁻¹), Micro (1-5), Macro (1-5), Estado, Ritmo, Fila_Excel_Original, Fecha_Invalida, Identificador_Faltante, OD_Faltante, OD_Negativa, OD_Alta_Revisar, Dias_Cultivo_Negativos, Duplicado_Exacto, Grupo_Recipiente, Dias_Entre_Registros, Cambio_Dias_Cultivo, Reinicio_Dias_Sospechoso, Numero_Ciclo, Ciclo_ID, Cierre_Ciclo_Descarte, Inicio_Tras_Descarte, Motivo_Revision_Ciclo

### [evaluacion_secuencias_final__Resumen_secuencias.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/evaluacion_secuencias_final__Resumen_secuencias.csv)
origen: evaluacion_secuencias_final.xlsx / hoja 'Resumen_secuencias' — 36 filas x 22 columnas

Columnas: Ciclo_ID, Secuencia, Estado_revision_ciclo, N_OD_con_edad, N_edades_distintas, Edad_min, Edad_max, Rango_edad, Fecha_inicio, Fecha_fin, OD_min, OD_max, OD_inicial, OD_final, Tendencia_neta, Aumentos, Descensos, Estables, Intervalos_mayores_7_dias, Edades_repetidas, Tiene_OD_alta_marcada, Clasificacion

### [evaluacion_secuencias_final__Detalle_OD.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/evaluacion_secuencias_final__Detalle_OD.csv)
origen: evaluacion_secuencias_final.xlsx / hoja 'Detalle_OD' — 185 filas x 7 columnas

Columnas: Ciclo_ID, Secuencia, Fecha, Edad, OD, Estado, OD_Alta_Revisar

### [evaluacion_secuencias_final__Criterios.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/evaluacion_secuencias_final__Criterios.csv)
origen: evaluacion_secuencias_final.xlsx / hoja 'Criterios' — 4 filas x 2 columnas

Columnas: Clasificacion, Criterio

### [matriz_diagnostico_ambiental_operacional__Matriz_diagnostico.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/matriz_diagnostico_ambiental_operacional__Matriz_diagnostico.csv)
origen: matriz_diagnostico_operacional/matriz_diagnostico_ambiental_operacional.xlsx / hoja 'Matriz_diagnostico' — 24 filas x 27 columnas

Columnas: Secuencia, Fecha, Días cultivo, OD, OD_predicha_exponencial, OD_predicha_baranyi, Error_exponencial, Error_baranyi, Error_abs_exp, Error_abs_baranyi, Direccion_error_exp, Direccion_error_baranyi, Ranking_error_exp, Ranking_error_baranyi, pH, Cambio_pH, Temperatura (°C), Cambio_Temperatura (°C), EC, Cambio_EC, Volumen (L), Cambio_Volumen (L), Luces encendidas, Cantidad luces, Aire encendido, Estado, Ritmo

### [matriz_diagnostico_ambiental_operacional__Resumen_variables.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/matriz_diagnostico_ambiental_operacional__Resumen_variables.csv)
origen: matriz_diagnostico_operacional/matriz_diagnostico_ambiental_operacional.xlsx / hoja 'Resumen_variables' — 18 filas x 9 columnas

Columnas: Secuencia, Variable, N_registros, N_disponibles, N_faltantes, Media, Desviacion_estandar, Minimo, Maximo

### [matriz_diagnostico_ambiental_operacional__Mayores_errores.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/matriz_diagnostico_ambiental_operacional__Mayores_errores.csv)
origen: matriz_diagnostico_operacional/matriz_diagnostico_ambiental_operacional.xlsx / hoja 'Mayores_errores' — 18 filas x 28 columnas

Columnas: Secuencia, Fecha, Días cultivo, OD, OD_predicha_exponencial, OD_predicha_baranyi, Error_exponencial, Error_baranyi, Error_abs_exp, Error_abs_baranyi, Direccion_error_exp, Direccion_error_baranyi, Ranking_error_exp, Ranking_error_baranyi, pH, Cambio_pH, Temperatura (°C), Cambio_Temperatura (°C), EC, Cambio_EC, Volumen (L), Cambio_Volumen (L), Luces encendidas, Cantidad luces, Aire encendido, Estado, Ritmo, Modelo

### [matriz_diagnostico_enriquecida__Matriz_enriquecida.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/matriz_diagnostico_enriquecida__Matriz_enriquecida.csv)
origen: matriz_diagnostico_operacional/matriz_diagnostico_enriquecida.xlsx / hoja 'Matriz_enriquecida' — 24 filas x 60 columnas

Columnas: Secuencia, Fecha, Días cultivo, OD, OD_predicha_exponencial, OD_predicha_baranyi, Error_exponencial, Error_baranyi, Error_abs_exp, Error_abs_baranyi, Direccion_error_exp, Direccion_error_baranyi, Ranking_error_exp, Ranking_error_baranyi, pH, Cambio_pH, Temperatura (°C), Cambio_Temperatura (°C), EC, Cambio_EC, Volumen (L), Cambio_Volumen (L), Luces encendidas, Cantidad luces, Aire encendido, Estado, Ritmo, mu_reportado, Inicio_Tras_Descarte, idx, t_dias, dt_dias, hueco, posicion, leverage_aprox, err_rel_pct, err_log, z_err_exp, mu_obs, dOD_dia …

### [matriz_diagnostico_enriquecida__Top_desviaciones.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/matriz_diagnostico_enriquecida__Top_desviaciones.csv)
origen: matriz_diagnostico_operacional/matriz_diagnostico_enriquecida.xlsx / hoja 'Top_desviaciones' — 12 filas x 23 columnas

Columnas: Secuencia, Días cultivo, Fecha, posicion, leverage_aprox, dt_dias, OD, OD_predicha_exponencial, Error_exponencial, err_rel_pct, z_err_exp, mu_obs, tasa_pH, tasa_T, tasa_EC, vol_rel, Cambio_Volumen (L), ratio_OD_vs_dilucion, ratio_EC_vs_agua, Aire encendido, Estado, Ritmo, vars_cambio_inusual

### [matriz_diagnostico_enriquecida__Top_desv_solo_interior.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/matriz_diagnostico_enriquecida__Top_desv_solo_interior.csv)
origen: matriz_diagnostico_operacional/matriz_diagnostico_enriquecida.xlsx / hoja 'Top_desv_solo_interior' — 12 filas x 23 columnas

Columnas: Secuencia, Días cultivo, Fecha, posicion, leverage_aprox, dt_dias, OD, OD_predicha_exponencial, Error_exponencial, err_rel_pct, z_err_exp, mu_obs, tasa_pH, tasa_T, tasa_EC, vol_rel, Cambio_Volumen (L), ratio_OD_vs_dilucion, ratio_EC_vs_agua, Aire encendido, Estado, Ritmo, vars_cambio_inusual

### [matriz_diagnostico_enriquecida__Asociaciones_descriptivas.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/matriz_diagnostico_enriquecida__Asociaciones_descriptivas.csv)
origen: matriz_diagnostico_operacional/matriz_diagnostico_enriquecida.xlsx / hoja 'Asociaciones_descriptivas' — 28 filas x 6 columnas

Columnas: ambito, variable, objetivo, n, rho, p

### [matriz_diagnostico_enriquecida__Calidad_categoricas.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/matriz_diagnostico_enriquecida__Calidad_categoricas.csv)
origen: matriz_diagnostico_operacional/matriz_diagnostico_enriquecida.xlsx / hoja 'Calidad_categoricas' — 3 filas x 6 columnas

Columnas: Secuencia, Luces encendidas, Aire encendido, Estado, Ritmo, Cantidad luces

### [matriz_diagnostico_enriquecida__Chequeo_es_LOO.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/matriz_diagnostico_enriquecida__Chequeo_es_LOO.csv)
origen: matriz_diagnostico_operacional/matriz_diagnostico_enriquecida.xlsx / hoja 'Chequeo_es_LOO' — 3 filas x 4 columnas

Columnas: Secuencia, dif_max_exp, dif_max_bar, errores_son_LOO

### [diagnostico_regimen_crecimiento__Intervalos.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/diagnostico_regimen_crecimiento__Intervalos.csv)
origen: matriz_diagnostico_operacional/diagnostico_regimen_crecimiento.xlsx / hoja 'Intervalos' — 24 filas x 17 columnas

Columnas: Secuencia, Días cultivo, dt_dias, OD, mu_obs, r_exp, mu_dev, tasa_pH, tasa_T, tasa_EC, vol_rel, tasa_pH_lag1, tasa_T_lag1, tasa_EC_lag1, Error_exponencial, z_err_exp, vars_cambio_inusual

### [diagnostico_regimen_crecimiento__Distribucion_mu.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/diagnostico_regimen_crecimiento__Distribucion_mu.csv)
origen: matriz_diagnostico_operacional/diagnostico_regimen_crecimiento.xlsx / hoja 'Distribucion_mu' — 3 filas x 10 columnas

Columnas: Secuencia, count, mean, std, min, 25%, 50%, 75%, max, r_exp

### [diagnostico_regimen_crecimiento__Asociaciones_rezago.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/diagnostico_regimen_crecimiento__Asociaciones_rezago.csv)
origen: matriz_diagnostico_operacional/diagnostico_regimen_crecimiento.xlsx / hoja 'Asociaciones_rezago' — 16 filas x 5 columnas

Columnas: covariable, objetivo, n, rho, p_perm

### [resultados_validacion_loo__Resumen.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/resultados_validacion_loo__Resumen.csv)
origen: validacion_loo/resultados_validacion_loo.xlsx / hoja 'Resumen' — 3 filas x 13 columnas

Columnas: Secuencia, N, RMSE_LOO_exponencial, RMSE_LOO_baranyi, MAE_LOO_exponencial, MAE_LOO_baranyi, q0_minimo_LOO, q0_maximo_LOO, mu_minimo_LOO, mu_maximo_LOO, lag_minimo_LOO, lag_maximo_LOO, ajustes_q0_cerca_limite

### [resultados_validacion_loo__Detalle_LOO.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/resultados_validacion_loo__Detalle_LOO.csv)
origen: validacion_loo/resultados_validacion_loo.xlsx / hoja 'Detalle_LOO' — 24 filas x 14 columnas

Columnas: Secuencia, Registro_retirado, Edad_retirada, OD_observada, OD_predicha_exponencial, OD_predicha_baranyi, Error_exponencial, Error_baranyi, X0_baranyi, mu_max_baranyi, q0_baranyi, alpha_inicial, lag_dias, q0_cerca_limite

### [resultados_validacion_loo__Parametros_completos.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/resultados_validacion_loo__Parametros_completos.csv)
origen: validacion_loo/resultados_validacion_loo.xlsx / hoja 'Parametros_completos' — 6 filas x 8 columnas

Columnas: Secuencia, Modelo, X0, r, mu_max, q0, alpha_inicial, lag_dias

### [analisis_residuos_y_predicciones__Metricas.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/analisis_residuos_y_predicciones__Metricas.csv)
origen: analisis_residuos_loo/analisis_residuos_y_predicciones.xlsx / hoja 'Metricas' — 6 filas x 9 columnas

Columnas: Secuencia, Modelo, RMSE_ajuste, Sesgo_ajuste, RMSE_LOO, MAE_LOO, Error_LOO_maximo, Observaciones_LOO_subestimadas, Observaciones_LOO_sobreestimadas

### [analisis_residuos_y_predicciones__Detalle_observaciones.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/analisis_residuos_y_predicciones__Detalle_observaciones.csv)
origen: analisis_residuos_loo/analisis_residuos_y_predicciones.xlsx / hoja 'Detalle_observaciones' — 24 filas x 53 columnas

Columnas: Fecha, Localidad, BIM, pH, Temperatura (°C), EC, Volumen (L), Luces encendidas, Cantidad luces, Aire encendido, Días cultivo, OD, μ (d⁻¹), Micro (1-5), Macro (1-5), Estado, Ritmo, Fila_Excel_Original, Fecha_Invalida, Identificador_Faltante, OD_Faltante, OD_Negativa, OD_Alta_Revisar, Dias_Cultivo_Negativos, Duplicado_Exacto, Grupo_Recipiente, Dias_Entre_Registros, Cambio_Dias_Cultivo, Reinicio_Dias_Sospechoso, Numero_Ciclo, Ciclo_ID, Cierre_Ciclo_Descarte, Inicio_Tras_Descarte, Motivo_Revision_Ciclo, Registro_retirado, Secuencia, Edad_retirada, OD_observada, OD_predicha_exponencial, OD_predicha_baranyi …

### [analisis_residuos_y_predicciones__Mayores_errores.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/analisis_residuos_y_predicciones__Mayores_errores.csv)
origen: analisis_residuos_loo/analisis_residuos_y_predicciones.xlsx / hoja 'Mayores_errores' — 18 filas x 8 columnas

Columnas: Secuencia, Modelo, Fecha, Edad, OD_observada, OD_predicha, Error_LOO, Estado

### [analisis_incrementos_od__Detalle_incrementos.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/analisis_incrementos_od__Detalle_incrementos.csv)
origen: analisis_incrementos_od/analisis_incrementos_od.xlsx / hoja 'Detalle_incrementos' — 9 filas x 21 columnas

Columnas: Secuencia, Fecha_anterior, Fecha_real, Edad_anterior, Edad_real, OD_anterior, OD_real, Cambio_edad, Dias_entre_mediciones, Incremento_OD_real, OD_predicha_Exponencial, Incremento_predicho_Exponencial, Error_OD_Exponencial, Error_incremento_Exponencial, Error_abs_incremento_Exponencial, OD_predicha_Logistico, Incremento_predicho_Logistico, Error_OD_Logistico, Error_incremento_Logistico, Error_abs_incremento_Logistico, Comportamiento_real

### [analisis_incrementos_od__Resumen_modelos.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/analisis_incrementos_od__Resumen_modelos.csv)
origen: analisis_incrementos_od/analisis_incrementos_od.xlsx / hoja 'Resumen_modelos' — 6 filas x 6 columnas

Columnas: Secuencia, Modelo, N, MAE_incremento, RMSE_incremento, Sesgo_incremento

### [analisis_incrementos_od__Por_comportamiento.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/analisis_incrementos_od__Por_comportamiento.csv)
origen: analisis_incrementos_od/analisis_incrementos_od.xlsx / hoja 'Por_comportamiento' — 6 filas x 5 columnas

Columnas: Comportamiento, Modelo, N, MAE_incremento, RMSE_incremento

### [analisis_errores_validacion__Detalle_errores.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/analisis_errores_validacion__Detalle_errores.csv)
origen: analisis_errores_validacion/analisis_errores_validacion.xlsx / hoja 'Detalle_errores' — 9 filas x 23 columnas

Columnas: Secuencia, N_entrenamiento, Edad_real, Fecha_real, OD_real, OD_referencia, OD_exponencial, OD_logistico, Error_referencia, Error_exponencial, Error_logistico, OD_anterior, Cambio_OD_real, Comportamiento, Error_Referencia, ErrorAbs_Referencia, ErrorPorcentual_Referencia, Error_Exponencial, ErrorAbs_Exponencial, ErrorPorcentual_Exponencial, Error_Logistico, ErrorAbs_Logistico, ErrorPorcentual_Logistico

### [analisis_errores_validacion__Resumen_modelos.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/analisis_errores_validacion__Resumen_modelos.csv)
origen: analisis_errores_validacion/analisis_errores_validacion.xlsx / hoja 'Resumen_modelos' — 9 filas x 7 columnas

Columnas: Secuencia, Modelo, N_predicciones, Error_medio, Error_absoluto_medio, Error_maximo_absoluto, Error_porcentual_medio

### [analisis_errores_validacion__Error_comportamiento.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/analisis_errores_validacion__Error_comportamiento.csv)
origen: analisis_errores_validacion/analisis_errores_validacion.xlsx / hoja 'Error_comportamiento' — 9 filas x 6 columnas

Columnas: Comportamiento, Modelo, N_predicciones, MAE, RMSE, Sesgo

### [resultados_validacion_origen_movil__Predicciones.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/resultados_validacion_origen_movil__Predicciones.csv)
origen: validacion_origen_movil/resultados_validacion_origen_movil.xlsx / hoja 'Predicciones' — 9 filas x 11 columnas

Columnas: Secuencia, N_entrenamiento, Edad_real, Fecha_real, OD_real, OD_referencia, OD_exponencial, OD_logistico, Error_referencia, Error_exponencial, Error_logistico

### [resultados_validacion_origen_movil__Metricas_secuencia.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/resultados_validacion_origen_movil__Metricas_secuencia.csv)
origen: validacion_origen_movil/resultados_validacion_origen_movil.xlsx / hoja 'Metricas_secuencia' — 3 filas x 10 columnas

Columnas: Secuencia, MAE_Referencia, RMSE_Referencia, N_Referencia, MAE_Exponencial, RMSE_Exponencial, N_Exponencial, MAE_Logistico, RMSE_Logistico, N_Logistico

### [resultados_validacion_origen_movil__Metricas_globales.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/resultados_validacion_origen_movil__Metricas_globales.csv)
origen: validacion_origen_movil/resultados_validacion_origen_movil.xlsx / hoja 'Metricas_globales' — 3 filas x 4 columnas

Columnas: Modelo, N_predicciones, MAE, RMSE

### [comparacion_modelos_ode__Metricas.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/comparacion_modelos_ode__Metricas.csv)
origen: ajustes_modelos_iniciales/comparacion_modelos_ode.xlsx / hoja 'Metricas' — 6 filas x 13 columnas

Columnas: Secuencia, N, Edad_inicial, Edad_final, Modelo, X0, r, RSS, RMSE, R2, AICc, mu_max, q0

### [comparacion_modelos_ode__Predicciones.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/comparacion_modelos_ode__Predicciones.csv)
origen: ajustes_modelos_iniciales/comparacion_modelos_ode.xlsx / hoja 'Predicciones' — 24 filas x 5 columnas

Columnas: Secuencia, Edad, OD_observada, OD_exponencial, OD_baranyi

### [comparacion_modelos_ode__Descarte.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/comparacion_modelos_ode__Descarte.csv)
origen: ajustes_modelos_iniciales/comparacion_modelos_ode.xlsx / hoja 'Descarte' — 2 filas x 6 columnas

Columnas: Secuencia, Edad_descarte, OD_observada, OD_exponencial, OD_baranyi, Dentro_intervalo_ajuste

### [sensibilidad_parametro_q0__Sheet1.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/sensibilidad_parametro_q0__Sheet1.csv)
origen: sensibilidad_baranyi/sensibilidad_parametro_q0.xlsx / hoja 'Sheet1' — 240 filas x 8 columnas

Columnas: Secuencia, q0, X0, mu_max, alpha_inicial, lag_estimado_dias, RSS, RMSE

### [resultados_primer_ajuste_ode__Comparacion_modelos.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/resultados_primer_ajuste_ode__Comparacion_modelos.csv)
origen: resultados_primer_ajuste_ode.xlsx / hoja 'Comparacion_modelos' — 6 filas x 10 columnas

Columnas: Secuencia, Modelo, N, Parametro_a, r, K, RMSE, AICc, RSS, Aviso

### [resultados_primer_ajuste_ode__Predicciones.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/resultados_primer_ajuste_ode__Predicciones.csv)
origen: resultados_primer_ajuste_ode.xlsx / hoja 'Predicciones' — 48 filas x 5 columnas

Columnas: Secuencia, Modelo, Edad, OD_observada, OD_ajustada

### [diagnostico_ruido_od__Trios.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/diagnostico_ruido_od__Trios.csv)
origen: diagnostico_ruido_od/diagnostico_ruido_od.xlsx / hoja 'Trios' — 68 filas x 10 columnas

Columnas: Secuencia, Localidad, Fecha, OD, hora, w, e_log, e_norm, dh_horas, tramo_OD

### [diagnostico_ruido_od__Ruido_resumen.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/diagnostico_ruido_od__Ruido_resumen.csv)
origen: diagnostico_ruido_od/diagnostico_ruido_od.xlsx / hoja 'Ruido_resumen' — 6 filas x 4 columnas

Columnas: index, n, sigma_rms, sigma_mad

### [diagnostico_ruido_od__Ruido_por_secuencia.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/diagnostico_ruido_od__Ruido_por_secuencia.csv)
origen: diagnostico_ruido_od/diagnostico_ruido_od.xlsx / hoja 'Ruido_por_secuencia' — 31 filas x 4 columnas

Columnas: Secuencia, n, sigma_rms, sigma_mad

### [diagnostico_ruido_od__Efecto_hora.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/diagnostico_ruido_od__Efecto_hora.csv)
origen: diagnostico_ruido_od/diagnostico_ruido_od.xlsx / hoja 'Efecto_hora' — 1 filas x 9 columnas

Columnas: beta_lnOD_por_hora, beta_pct_por_hora, IC95_inf, IC95_sup, spearman_rho, spearman_p, n_trios, n_secuencias, beta_sin_top3_dh

### [diagnostico_ruido_od__Simulacion_RMSE_LOO.csv](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/datos_csv/diagnostico_ruido_od__Simulacion_RMSE_LOO.csv)
origen: diagnostico_ruido_od/diagnostico_ruido_od.xlsx / hoja 'Simulacion_RMSE_LOO' — 6 filas x 10 columnas

Columnas: Secuencia, n, sigma_usada, sigma, RMSE_LOO_obs_loglineal, RMSE_LOO_obs_exp_reportado, sim_p05, sim_mediana, sim_p95, frac_sim_ge_obs

## Salidas de texto de ejecuciones

- [esquema2.txt](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/salidas_texto/esquema2.txt)
- [esquema_salida.txt](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/salidas_texto/esquema_salida.txt)
- [salida_enriquecimiento.txt](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/salidas_texto/salida_enriquecimiento.txt)
- [salida_regimen.txt](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/salidas_texto/salida_regimen.txt)
- [salida_ruido.txt](https://raw.githubusercontent.com/c0noo/ucnim-microalgas/main/salidas_texto/salida_ruido.txt)
