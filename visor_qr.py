import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from gtts import gTTS
import openai
import os

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Sentinela QR", layout="wide")
st.title("🚚 Sentinela QR - Trazabilidad Inteligente 2025")

# --- API Keys (opcional si usas OpenAI) ---
openai.api_key = os.environ.get("OPENAI_API_KEY")

# --- PARÁMETROS ---
sheet_id = "1yWJoHTzHRwxCPQCnthm2MCgD2DFO--fQEgqMq0_fbCM"
sheet_name = "DatosQR"
json_path = "registro-eventos-hugo-a97cbe9d7f0f.json"  # Debe estar en la misma carpeta

# --- CONEXIÓN SOLO USANDO ARCHIVO JSON ---
@st.cache_resource
def conectar_google_sheet(sheet_id, sheet_name):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    try:
        cred_path = os.path.join(os.getcwd(), json_path)
        st.write(f"[DEBUG] Usando JSON local: {cred_path}")
        creds = Credentials.from_service_account_file(cred_path, scopes=scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        return worksheet, f"✅ Conectado a: {spreadsheet.title}"
    except gspread.exceptions.SpreadsheetNotFound:
        return None, f"❌ Hoja con ID {sheet_id} no encontrada. Verifica el ID."
    except Exception as e:
        return None, f"❌ Error al conectar con Hojas de cálculo de Google: {e}"

# --- FUNCIONES AUXILIARES ---
def registrar_evento(sheet, data):
    try:
        data = [str(x) for x in data]
        sheet.append_row(data)
        st.success("✅ Evento registrado correctamente.")
    except Exception as e:
        st.error(f"❌ Error al registrar evento: {e}")

def cargar_eventos(sheet):
    try:
        records = sheet.get_all_records()
        df = pd.DataFrame(records)
        for col in df.columns:
            df[col] = df[col].astype(str)
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar eventos: {e}")
        return pd.DataFrame()

def sugerir_siguiente_paso(codigo_qr, eventos):
    try:
        if not openai.api_key:
            return "🔐 No se puede generar sugerencia: falta la API Key."
        prompt = f"Historial de eventos para el código QR '{codigo_qr}': {eventos}. ¿Cuál es el siguiente paso lógico en logística?"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres experto en procesos logísticos."},
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

# --- CONECTAR ---
sheet, connection_message = conectar_google_sheet(sheet_id, sheet_name)
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
        st.dataframe(df_eventos)

# --- TAB 2: VISOR + IA ---
with tab2:
    st.header("Visor de QR y Sugerencia Inteligente")
    df = cargar_eventos(sheet)

    codigo_url = st.query_params.get("codigo") if hasattr(st, 'query_params') else None
    if codigo_url:
        st.success(f"📦 Código recibido automáticamente: {codigo_url}")
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = [codigo_url, fecha, "Escaneado", "Lugar Desconocido", "Posición Desconocida", 1, "Usuario Desconocido"]
        registrar_evento(sheet, data)

    if not df.empty and "Codigo QR" in df.columns:
        seleccionado = st.selectbox("Selecciona un QR", df["Codigo QR"].unique())
        df_qr = df[df["Codigo QR"] == seleccionado]
        st.subheader("📌 Historial del Código QR")
        st.dataframe(df_qr)

        eventos = df_qr["Evento"].tolist()
        sugerencia = sugerir_siguiente_paso(seleccionado, eventos)

        st.subheader("🔮 Sugerencia del próximo paso")
        st.write(sugerencia)

        if st.button("🔊 Escuchar sugerencia"):
            reproducir_audio(sugerencia)
    else:
        st.warning("⚠️ Datos insuficientes para mostrar historial y sugerencias.")
















