import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googlesearch import search
import datetime
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Rastreador de Menciones - Moisés Medrano", page_icon="🔍")
st.title("🔍 Rastreador de Menciones y Eventos")
st.write("Esta herramienta busca nuevas apariciones del profe Moisés Medrano en la web y las guarda en el Google Sheet oficial.")

URL_SHEET = "https://docs.google.com/spreadsheets/d/12eB9rkmsG20FhIKXlthoIp5hQlKgetCQaU_xLS-WCxo/edit?gid=0#gid=0"
ZONA_COLOMBIA = datetime.timezone(datetime.timedelta(hours=-5))

# 1. Conexión con Google Sheets (usando st.secrets para mayor seguridad en la nube)
@st.cache_resource
def conectar_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
    client = gspread.authorize(creds)
    return client.open_by_url(URL_SHEET).sheet1

sheet = conectar_sheets()

# 2. Interfaz y Botón de Ejecución
if st.button("Buscar nuevas apariciones en la web"):
    with st.spinner("Rastreando la web... esto puede tomar un minuto."):

        nombre_objetivo = "Moisés Medrano"
        query = f'"{nombre_objetivo}" (taller OR evento OR texto OR congreso OR cultura OR ministerio OR conversatorio)'

        try:
            resultados = list(search(query, num_results=15, lang="es", sleep_interval=2))
        except Exception:
            resultados = None
            st.error("⚠️ Google bloqueó temporalmente la búsqueda. Intenta de nuevo en unos minutos.")

        if resultados is not None:
            registros_actuales = set(sheet.col_values(3))  # URLs en la columna C
            nuevos_registros = 0

            for url in resultados:
                if url not in registros_actuales:
                    fecha = datetime.datetime.now(ZONA_COLOMBIA).strftime("%Y-%m-%d")
                    tipo = "PDF/Documento" if ".pdf" in url.lower() else "Noticia/Evento"
                    sheet.append_row([fecha, nombre_objetivo, url, tipo])
                    registros_actuales.add(url)
                    nuevos_registros += 1

            if nuevos_registros > 0:
                st.success(f"✅ Búsqueda completada. Se encontraron y guardaron {nuevos_registros} nuevos enlaces.")
            else:
                st.info("No se encontraron menciones nuevas en esta ejecución.")

# 3. Mostrar los datos actuales del Sheet en la web
st.subheader("Últimos registros guardados")
datos = sheet.get_all_records()
if datos:
    df = pd.DataFrame(datos)
    st.dataframe(df, use_container_width=True)
    st.markdown(f"[Abrir el Google Sheet completo aquí]({URL_SHEET})")
else:
    st.write("El documento está vacío.")