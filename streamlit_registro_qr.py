import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from urllib.parse import unquote
import streamlit.components.v1 as components
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Registro QR Automático", layout="centered")
st.title("📦 Registro Automático desde Código QR")

# --- PARÁMETROS DE CONEXIÓN ---
sheet_id = "1yWJoHTzHRwxCPQCnthm2MCgD2DFO--fQEgqMq0_fbCM"
sheet_name = "DatosQR"

# --- CONECTAR A GOOGLE SHEETS USANDO SECRETS ---
def conectar_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Reemplaza \n por saltos reales
    raw_json = st.secrets["GOOGLE_CREDS"].replace('\\n', '\n')
    creds_dict = json.loads(raw_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id).worksheet(sheet_name)

# --- ABRIR HOJA DE CÁLCULO ---
try:
    sheet = conectar_google_sheet()
except Exception as e:
    st.error("❌ Error al conectar con Google Sheets:")
    st.exception(e)
    st.stop()

# --- CARGAR CÓDIGOS EXISTENTES ---
try:
    existing_records = sheet.get_all_records()
    codigos_existentes = set()
    for row in existing_records:
        valor = str(row.get("Codigo QR", "")).strip()
        if valor:
            codigos_existentes.add(valor)
except Exception as e:
    st.error("❌ No se pudieron cargar los códigos existentes.")
    st.exception(e)
    codigos_existentes = set()

# --- LEER PARÁMETRO DE LA URL ---
param = st.query_params.get("codigo", "")
codigo_param = param[0] if isinstance(param, list) else param
codigo_inicial = unquote(codigo_param).strip()
codigo_inicial = " ".join(codigo_inicial.split())  # Limpia espacios dobles

# --- MOSTRAR SOLO SI HAY CÓDIGO ---
if codigo_inicial:
    st.write("🧪 Código escaneado:", codigo_inicial)

    partes = codigo_inicial.split(" ")
    if len(partes) == 4:
        codigo, lugar, posicion, cantidad = partes
        try:
            cantidad = int(cantidad)
        except:
            cantidad = 1

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        evento = "Entrada"
        usuario = "Hugo"

        data = [codigo_inicial, fecha, evento, lugar, posicion, cantidad, usuario]
        st.write("📤 Datos a registrar:", data)

        if codigo_inicial in codigos_existentes:
            st.info("ℹ️ Este código ya fue registrado anteriormente.")
        else:
            try:
                sheet.append_row(data)
                st.success("✅ Registro automático exitoso.")
                components.html(
                    """<script>
                    setTimeout(function() {
                      window.location.href = window.location.origin;
                    }, 2500);
                    </script>""",
                    height=0,
                )
            except Exception as e:
                st.error(f"❌ Error al registrar:")
                st.exception(e)
    else:
        st.warning("⚠️ Código escaneado inválido. Usa el formato: LOTE123 Z3 B4 20")
else:
    st.info("📷 Escanea un QR válido para registrar automáticamente.")




