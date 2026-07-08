import os
import sys
from streamlit.web import cli as stcli
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import streamlit as st
from calculo import calcular_puntos_fase
from api import FootballDataFetcher, leer_predicciones_publicas

if __name__ == '__main__':
    if getattr(sys, 'frozen', False) and not os.environ.get("STREAMLIT_YA_INICIADO"):
        os.environ["STREAMLIT_YA_INICIADO"] = "true"
        script_path = os.path.join(sys._MEIPASS, "interfaz.py")

        sys.argv = [
            "streamlit",
            "run",
            script_path,
            "--global.developmentMode", "false",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false",
            "--theme.primaryColor", "#003893",
            "--theme.backgroundColor", "#FFFCE6",
            "--theme.secondaryBackgroundColor", "#003893",
            "--theme.textColor", "#292FA8"
        ]
        sys.exit(stcli.main())

st.set_page_config(
    page_title="Polla Mundialista 2026 - TIENDA EL AMIGO",
    page_icon="⚽",
    layout="centered"
)

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #FFFCE6; /* Un amarillo pastel muy suave, limpio y elegante */
    }

    /* Hace que la barra superior sea transparente para que no desentone con el fondo */
    [data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 0);
    }

    div.stButton > button:first-child {
        background-color: #CE1126; /* El rojo oficial de la Selección Colombia */
        color: white;   
        border-radius: 8px;
        border: none;
        font-weight: bold;
        box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.1); /* Le da un pequeño efecto flotante */
        transition: background-color 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #9A0D1C; /* Un rojo más oscuro y elegante al pasar el mouse */
        color: white;
    }

    h1, h3 {
        color: #003893 !important; 
    }

    .green-text {
        color: #003893; 
        font-weight: bold;
    }

    .centered-text {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

nombre_logo = "logo.png"

if os.path.exists(nombre_logo):
    col_izq, col_centro, col_der = st.columns([1.2, 1.6, 1.2])
    with col_centro:
        st.image(nombre_logo, width=240)
else:
    st.markdown("<h1 style='text-align: center; font-size: 80px; margin-bottom: 0px;'>⚽</h1>", unsafe_allow_html=True)

st.markdown("""
    <div class="centered-text">
        <h1 style='margin-top: 15px; margin-bottom: 0px;'>Polla Mundialista 2026</h1>
        <h3 style='color: #2e7d32; margin-top: 0px; margin-bottom: 10px;'>TIENDA EL AMIGO</h3>
        <p style='font-style: italic; color: #555;'>Sigue los puntajes en tiempo real y compite por los premios espectaculares.</p>
    </div>
""", unsafe_allow_html=True)

st.write("---")

st.markdown("### 🏆 <span class='green-text'>Tabla de Posiciones</span>", unsafe_allow_html=True)

if st.button("🔄 Actualizar Tabla"):
    st.toast("Actualizando tabla de posiciones...", icon="⏳")

fetcher = FootballDataFetcher()
dict_resultados = fetcher.obtener_resultados_mundial()

if dict_resultados:
    conn = st.connection("gsheets", type=GSheetsConnection)

    try:
        id_archivo = "1ejw-IN76iDhvVKsN8V8fCU4Lz0dxkUMOnW8vJKrx5SM"
        df_16avos = leer_predicciones_publicas(sheet_id=id_archivo, gid="136102707")
        df_fase_final = leer_predicciones_publicas(sheet_id=id_archivo, gid="1884530799")
        df_puntos_16avos = calcular_puntos_fase(df_16avos, dict_resultados)

        mapeo_fase_final = {
            "537383": "CUARTOS[Llave 1]",
            "537384": "CUARTOS[Llave 2]",
            "537385": "CUARTOS[Llave 3]",
            "537386": "CUARTOS[Llave 4]",
            "ID_API_SEMI_1": "SEMIFINAL [Semifinal 1]",
            "ID_API_SEMI_2": "SEMIFINAL [Semifinal 2]",
            "ID_API_FINAL": "FINAL"
        }
        df_puntos_final = calcular_puntos_fase(df_fase_final, dict_resultados, mapeo_columnas=mapeo_fase_final)
        df_combinado = pd.merge(df_puntos_16avos, df_puntos_final, on='Nombre', how='outer', suffixes=('_16', '_Fin'))
        df_combinado = df_combinado.fillna(0)

        df_combinado['Puntos'] = df_combinado['Puntos_16'] + df_combinado['Puntos_Fin']
        if 'Aciertos_16' in df_combinado.columns and 'Aciertos_Fin' in df_combinado.columns:
            df_combinado['Aciertos'] = df_combinado['Aciertos_16'] + df_combinado['Aciertos_Fin']
        else:
            df_combinado['Aciertos'] = 0

        df_principal = df_combinado[['Nombre', 'Puntos', 'Aciertos']].copy()

        df_principal = df_principal.sort_values(by=['Puntos', 'Aciertos'], ascending=[False, False]).reset_index(
            drop=True)

        df_principal['Puntos'] = df_principal['Puntos'].astype(int)
        df_principal['Aciertos'] = df_principal['Aciertos'].astype(int)

        df_principal.index = df_principal.index + 1
        df_principal.index.name = 'Posición'

        df_estilizado = df_principal.style.set_properties(**{
            'background-color': '#EAEBFA', 'color': '#3038C7', 'border-color': '#FFFCE6'
        }).set_table_styles([
            {'selector': 'th',
             'props': [('background-color', '#003893'), ('color', '#FFFFFF'), ('font-weight', 'bold')]}
        ])

        st.table(df_estilizado)
        st.caption("Puntaje acumulado: Fase Final.")

    except Exception as e:
        st.error(f"No se pudo leer la hoja de cálculo. Revisa que los enlaces o nombres sean correctos. Error: {e}")