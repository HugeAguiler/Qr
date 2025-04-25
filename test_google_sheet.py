import gspread
from oauth2client.service_account import ServiceAccountCredentials

json_path = "registro-eventos-hugo-5fea994304f5.json"
sheet_id = "1yWJoHTzHRwxCPQCnthm2MCgD2DFO--fQEgqMq0_fbCM"
sheet_name = "prueba.py"

try:
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    print(f"✅ Conexión exitosa con la hoja: {sheet.title}")
    print("Primeras 5 filas:")
    rows = sheet.get_all_values()
    for row in rows[:5]:
        print(row)
except Exception as e:
    import traceback
    print("❌ Error al conectar con Google Sheets:")
    traceback.print_exc()


