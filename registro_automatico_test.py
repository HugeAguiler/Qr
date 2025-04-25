import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- PARÁMETROS DE CONFIGURACIÓN ---
json_path = "registro-eventos-hugo-5fea994304f5.json"
sheet_id = "1yWJoHTzHRwxCPQCnthm2MCgD2DFO--fQEgqMq0_fbCM"
sheet_name = "prueba.py"

# --- CONEXIÓN A GOOGLE SHEETS ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(sheet_id).worksheet(sheet_name)

# --- DATOS DE PRUEBA ---
codigo_qr = "TEST123 Z1 A1 99"
fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
evento = "Entrada"
lugar = "Z1"
posicion = "A1"
cantidad = 99
usuario = "Hugo"

# --- REGISTRO ---
data = [codigo_qr, fecha_hora, evento, lugar, posicion, cantidad, usuario]

try:
    sheet.append_row(data)
    print("✅ Registro exitoso:", data)
except Exception as e:
    print("❌ Error al registrar:", e)