import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from gtts import gTTS
import openai
import os

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Sentinela QR", layout="wide")
st.title("🚚 Sentinela QR - Trazabilidad Inteligente 2025")

# --- API Keys ---
openai.api_key = os.environ.get("OPENAI_API_KEY")

# --- CONEXIÓN A GOOGLE SHEETS LOCAL ---
@st.cache_resource
def conectar_google_sheet(json_path, sheet_id, sheet_name):
    dir_path = os.path.dirname(__file__)
    full_path = os.path.join(dir_path, json_path)
    if not os.path.exists(full_path):
        return None, f"❌ Archivo JSON no encontrado: {full_path}"
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(full_path, scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        return worksheet, f"✅ Conectado a: {spreadsheet.title}"
    except gspread.exceptions.SpreadsheetNotFound:
        return None, f"❌ Hoja con ID {sheet_id} no encontrada. Verifica el ID."
    except Exception as e:
        return None, f"❌ Error al conectar con Google Sheets: {e}"

# --- FUNCIONES AUXILIARES ---
def registrar_evento(sheet, data):
    try:
        sheet.append_row(data)
        st.success("✅ Evento registrado correctamente.")
    except Exception as e:
        st.error(f"❌ Error al registrar evento: {e}")

def cargar_eventos(sheet):
    try:
        records = sheet.get_all_records()
        return pd.DataFrame(records)
    except Exception as e:
        st.error(f"❌ Error al cargar eventos: {e}")
        return pd.DataFrame()

def sugerir_siguiente_paso(codigo_qr, eventos):
    try:
        prompt = f"Tengo un historial de eventos para el código QR '{codigo_qr}': {eventos}. ¿Cuál sería el siguiente paso lógico en un proceso logístico?"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un experto en procesos logísticos y trazabilidad."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al generar sugerencia: {e}"

def reproducir_audio(texto):
    try:
        tts = gTTS(texto, lang="es")
        audio_file = "sugerencia.mp3"
        tts.save(audio_file)
        with open(audio_file, "rb") as f:
            st.audio(f.read(), format="audio/mp3")
        os.remove(audio_file)
    except Exception as e:
        st.error(f"❌ Error al generar audio: {e}")

# --- PARÁMETROS ---
json_path = "registro-eventos-hugo-bf4035e53377.json"
sheet_id = "1yWJoHTzHRwxCPQCnthm2MCgD2DFO--fQEgqMq0_fbCM"
sheet_name = "DatosQR"

# --- CONECTAR ---
sheet, connection_message = conectar_google_sheet(json_path, sheet_id, sheet_name)
if sheet is None:
    st.error(connection_message)
    st.stop()
else:
    st.success(connection_message)

# --- UI CON TABS ---
tab1, tab2 = st.tabs(["📝 Registro", "📦 Visor + IA"])

# --- TAB 1: REGISTRO ---
with tab1:
    st.header("Registrar Nuevo Evento")
    with st.form("registro_evento"):
        codigo = st.text_input("Código QR")
        evento = st.selectbox("Evento", ["Entrada", "Ubicación", "Picking", "Liberado", "Embarcado", "Salida"])
        lugar = st.text_input("Lugar")
        posicion = st.text_input("Posición")
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        usuario = st.text_input("Usuario", value="Hugo")
        enviar = st.form_submit_button("📤 Registrar")

    if enviar:
        if not all([codigo, lugar, posicion, usuario]):
            st.warning("⚠️ Llena todos los campos obligatorios.")
        else:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = [codigo, fecha, evento, lugar, posicion, cantidad, usuario]
            registrar_evento(sheet, data)

    with st.expander("📄 Ver últimos eventos"):
        df_eventos = cargar_eventos(sheet)
        if not df_eventos.empty:
            st.dataframe(df_eventos)
        else:
            st.warning("⚠️ No se encontraron eventos.")

# --- TAB 2: VISOR + IA ---
with tab2:
    st.header("Visor de QR y Sugerencia Inteligente")
    df = cargar_eventos(sheet)

    # Leer código desde la URL
    codigo_url = st.query_params.get("codigo")
    if codigo_url:
        st.success(f"📦 Código recibido automáticamente: {codigo_url}")
        # Registrar automáticamente el QR escaneado
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = [codigo_url, fecha, "Escaneado", "Lugar Desconocido", "Posición Desconocida", 1, "Usuario Desconocido"]
        registrar_evento(sheet, data)

    if not df.empty:
        st.subheader("📊 Vista previa de datos")
        st.dataframe(df)

        if "Codigo QR" in df.columns:
            codigos = df["Codigo QR"].dropna().unique()

            # Si tenemos el código en la URL, seleccionarlo automáticamente en el selectbox
            seleccionado = st.selectbox(
                "Selecciona un QR",
                codigos,
                index=0 if not codigo_url or codigo_url not in codigos else list(codigos).index(codigo_url)
            )

            # Filtrar el DataFrame según el código seleccionado
            df_qr = df[df["Codigo QR"] == seleccionado].sort_values(by="Fecha Hora")
            st.subheader("📌 Historial del Código QR")
            cols = ["Fecha Hora", "Evento", "Ubicacion", "Usuario"]
            disponibles = [col for col in cols if col in df_qr.columns]
            st.dataframe(df_qr[disponibles])

            eventos = df_qr["Evento"].tolist()
            sugerencia = sugerir_siguiente_paso(seleccionado, eventos)

            st.subheader("🔮 Sugerencia del próximo paso")
            st.write(sugerencia)

            if st.button("🔊 Escuchar sugerencia"):
                reproducir_audio(sugerencia)
        else:
            st.warning("⚠️ No se encontró la columna 'Codigo QR'. Verifica tu hoja.")
    else:
        st.error("❌ No se pudieron cargar los datos.")







