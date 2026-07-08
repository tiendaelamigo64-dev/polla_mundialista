import pandas as pd
import json
import os
import sys


def cargar_resultados_api():
    if getattr(sys, 'frozen', False):
        ruta_base = os.path.dirname(sys.executable)
    else:
        ruta_base = os.path.dirname(os.path.abspath(__file__))

    ruta_json = os.path.join(ruta_base, "resultados_temp.json")

    if os.path.exists(ruta_json):
        with open(ruta_json, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    return {}


def calcular_puntos_fase(df_predicciones, resultados_reales, mapeo_columnas=None, puntos_acierto=3):
    if df_predicciones.empty:
        return pd.DataFrame(columns=['Nombre', 'Puntos', 'Aciertos'])

    df = df_predicciones.copy()
    df['Nombre'] = df['Nombre'].astype(str).str.strip().str.upper()

    lista_resultados = []

    for index, fila in df.iterrows():
        puntos_usuario = 0
        aciertos_usuario = 0

        for partido_id, info in resultados_reales.items():
            if info['estado'] != 'FINISHED':
                continue
            col_partido = ""
            if mapeo_columnas and partido_id in mapeo_columnas:
                col_partido = mapeo_columnas[partido_id]
            else:
                col_partido = f"{info['local']} - {info['visitante']}"

            if col_partido in df.columns:
                prediccion = str(fila[col_partido]).strip().upper()
                real = str(info['resultado']).strip().upper()

                if prediccion == real:
                    puntos_usuario += puntos_acierto
                    aciertos_usuario += 1

        lista_resultados.append({
            'Nombre': fila['Nombre'],
            'Puntos': puntos_usuario,
            'Aciertos': aciertos_usuario
        })

    return pd.DataFrame(lista_resultados)


def obtener_tabla_final(df_grupos, df_16avos):
    resultados_reales = cargar_resultados_api()

    puntos_g = calcular_puntos_fase(df_grupos, resultados_reales)
    puntos_16 = calcular_puntos_fase(df_16avos, resultados_reales)

    df_final = pd.merge(puntos_g, puntos_16, on=['Nombre'], how='outer', suffixes=('_Grupos', '_16avos'))

    df_final['Puntos_Grupos'] = df_final['Puntos_Grupos'].fillna(0)
    df_final['Puntos_16avos'] = df_final['Puntos_16avos'].fillna(0)

    if 'Aciertos_Grupos' in df_final.columns:
        df_final['Aciertos_Grupos'] = df_final['Aciertos_Grupos'].fillna(0)
    if 'Aciertos_16avos' in df_final.columns:
        df_final['Aciertos_16avos'] = df_final['Aciertos_16avos'].fillna(0)

    df_final['Total'] = df_final['Puntos_Grupos'] + df_final['Puntos_16avos']
    df_final['Puntos_Grupos'] = df_final['Puntos_Grupos'].astype(int)
    df_final['Puntos_16avos'] = df_final['Puntos_16avos'].astype(int)
    df_final['Total'] = df_final['Total'].astype(int)

    df_final = df_final.sort_values(by='Total', ascending=False).reset_index(drop=True)
    df_final.index = df_final.index + 1
    df_final.index.name = 'Posición'

    return df_final