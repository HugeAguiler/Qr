import gspread
from google.oauth2.service_account import Credentials
import os

SHEET_ID = "1yWJoHTzHRwxCPQCnthm2MCgD2DFO--fQEgqMq0_fbCM"
SHEET_NAME = "DatosQR"
JSON_FILENAME = "registro-eventos-hugo-a97cbe9d7f0f.json"

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

cred_path = os.path.join(os.getcwd(), JSON_FILENAME)
print("\n[DEBUG] Probando clave en:", cred_path)
print("[DEBUG] ¿Existe el archivo?:", os.path.exists(cred_path))

if not os.path.exists(cred_path):
    raise FileNotFoundError(f"No existe el archivo {cred_path}")

with open(cred_path, "r", encoding="utf-8") as f:
    contenido = f.read(300)
    print("[DEBUG] Primeros 300 caracteres del JSON:\n", contenido)

try:
    creds = Credentials.from_service_account_file(cred_path, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID)
    worksheet = sheet.worksheet(SHEET_NAME)
    print("[DEBUG] ¡CONEXIÓN EXITOSA!")
    print("Primeras filas de la hoja:")
    data = worksheet.get_all_values()
    for row in data[:5]:
        print(row)
except Exception as e:
    print("[ERROR] No se pudo conectar con Google Sheets:")
    print(e)

