import requests
import pandas as pd
import json
import os
import sys

def leer_predicciones_publicas(sheet_id="TU_ID_DE_SHEET_LARGO", gid="0"):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        print(f"✅ Datos cargados correctamente desde el GID: {gid}")
        return df
    except Exception as e:
        print(f"❌ Error al leer la hoja: {e}")
        return None


class FootballDataFetcher:
    def __init__(self, api_key="bb3538f885124f8bb51927c8c2c37c98"):
        self.api_key = api_key
        self.base_url = "https://api.football-data.org/v4/"
        self.headers = {
            'X-Auth-Token': self.api_key
        }

    def obtener_resultados_mundial(self, league_code='WC', season=2026):
        endpoint = f"{self.base_url}competitions/{league_code}/matches"
        params = {'season': season}

        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params,
                timeout=10,
                verify=False
            )
            response.raise_for_status()
            data = response.json()

            traduccion_paises = {
                "SOUTH AFRICA": "SUDAFRICA", "SOUTH KOREA": "COREA", "CZECHIA": "REPUBLICA CHECA",
                "CANADA": "CANADÁ", "BOSNIA-HERZEGOVINA": "BOSNIA", "UNITED STATES": "EEUU",
                "QATAR": "CATAR", "SWITZERLAND": "SUIZA", "BRAZIL": "BRASIL", "MOROCCO": "MARRUECOS",
                "HAITI": "HAITI", "SCOTLAND": "ESCOCIA", "TURKEY": "TURQUIA", "GERMANY": "ALEMANIA",
                "CURAÇAO": "CURAZAO", "NETHERLANDS": "PAISES BAJOS", "JAPAN": "JAPON",
                "IVORY COAST": "COSTA DE MARFIL", "ECUADOR": "ECUADOR", "SWEDEN": "SUECIA",
                "TUNISIA": "TUNEZ", "SPAIN": "ESPANA", "CAPE VERDE ISLANDS": "CABO VERDE",
                "BELGIUM": "BÉLGICA", "EGYPT": "EGIPTO", "SAUDI ARABIA": "ARABIA SAUDI",
                "URUGUAY": "URUGUAY", "IRAN": "IRAN", "NEW ZEALAND": "NUEVA ZELANDA",
                "FRANCE": "FRANCIA", "SENEGAL": "SENEGAL", "IRAQ": "IRAK", "NORWAY": "NORUEGA",
                "ARGENTINA": "ARGENTINA", "ALGERIA": "ARGELIA", "AUSTRIA": "AUSTRIA",
                "JORDAN": "JORDANIA", "PORTUGAL": "PORTUGAL", "CONGO DR": "RD CONGO",
                "ENGLAND": "INGLATERRA", "CROATIA": "CROACIA", "GHANA": "GHANA",
                "PANAMA": "PANAMA", "UZBEKISTAN": "UZBEKISTAN", "COLOMBIA": "COLOMBIA"
            }

            resultados = {}

            for match in data['matches']:
                name_local_raw = match['homeTeam']['name']
                name_visitante_raw = match['awayTeam']['name']

                if (name_local_raw is None or name_visitante_raw is None or
                        name_local_raw == "NONE" or name_visitante_raw == "NONE"):
                    continue

                local_es = traduccion_paises.get(name_local_raw.upper(), name_local_raw.upper())
                visitante_es = traduccion_paises.get(name_visitante_raw.upper(), name_visitante_raw.upper())

                score = match['score']['fullTime']
                status = match['status']
                partido_id = match['id']

                if status == 'FINISHED':
                    if score['home'] > score['away']:
                        resultado_final = local_es
                    elif score['home'] < score['away']:
                        resultado_final = visitante_es
                    else:
                        resultado_final = "EMPATE"
                else:
                    resultado_final = "PENDIENTE"

                resultados[partido_id] = {
                    'local': local_es,
                    'visitante': visitante_es,
                    'goles_local': score['home'],
                    'goles_visitante': score['away'],
                    'resultado': resultado_final,
                    'estado': status
                }

            if getattr(sys, 'frozen', False):
                ruta_real = os.path.dirname(sys.executable)
            else:
                ruta_real = os.path.dirname(os.path.abspath(__file__))

            ruta_json = os.path.join(ruta_real, "resultados_temp.json")

            with open(ruta_json, "w", encoding="utf-8") as archivo:
                json.dump(resultados, archivo, indent=4, ensure_ascii=False)

            print(f"✅ Resultados guardados exitosamente en: {ruta_json}")
            return resultados

        except requests.exceptions.RequestException as e:
            print(f"❌ Error al conectar con el endpoint de partidos: {e}")

            if getattr(sys, 'frozen', False):
                ruta_real = os.path.dirname(sys.executable)
            else:
                ruta_real = os.path.dirname(os.path.abspath(__file__))

            ruta_json = os.path.join(ruta_real, "resultados_temp.json")

            if os.path.exists(ruta_json):
                print("🔄 Cargando última copia local guardada de respaldo...")
                with open(ruta_json, "r", encoding="utf-8") as archivo:
                    return json.load(archivo)

            return {}