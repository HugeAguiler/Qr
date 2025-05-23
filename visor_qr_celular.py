import streamlit as st
import streamlit.components.v1 as components
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(page_title="Sentinela QR Celular", layout="centered")
st.title("📱 Escaneo QR desde Celular - Sentinela")

# --- HTML del lector QR (adaptado del index que funciona bien) ---
html_code = """
<!DOCTYPE html>
<html lang=\"es\">
<head>
  <meta charset=\"UTF-8\">
  <title>Escáner QR Hugo 2025</title>
  <script src=\"https://unpkg.com/html5-qrcode\"></script>
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      background-color: #f9f9f9;
      padding: 20px;
    }
    #reader {
      width: 400px;
      margin: auto;
    }
    #result {
      margin-top: 20px;
      background: #e0ffe3;
      padding: 10px;
      border-radius: 10px;
      font-size: 1.2em;
      color: #0a6d5a;
    }
    #retry-btn, #camera-select {
      display: none;
      margin-top: 20px;
      padding: 10px 20px;
      font-size: 1em;
      border: none;
      border-radius: 5px;
    }
    #retry-btn {
      background-color: #0a6d5a;
      color: white;
      cursor: pointer;
    }
    #camera-select {
      background-color: #f0f0f0;
    }
  </style>
</head>
<body>
  <h2>📷 Escáner de Código QR</h2>
  <p>Apunta la cámara al QR para escanear y registrar automáticamente.</p>
  <select id=\"camera-select\"></select>
  <div id=\"reader\"></div>
  <div id=\"result\">Esperando escaneo...</div>
  <button id=\"retry-btn\" onclick=\"location.reload()\">🔄 Reintentar escaneo</button>

  <script>
    const html5QrCode = new Html5Qrcode(\"reader\");
    let alreadyScanned = false;
    const cameraSelect = document.getElementById(\"camera-select\");

    function startScanner(cameraId) {
      html5QrCode.start(
        cameraId,
        { fps: 10, qrbox: 250 },
        qrCodeMessage => {
          if (alreadyScanned) return;
          alreadyScanned = true;

          document.getElementById("result").innerText = `✅ Detectado: ${qrCodeMessage}`;
          console.log("Código escaneado:", qrCodeMessage);

          window.parent.postMessage({ type: 'qr_code_scanned', data: qrCodeMessage }, '*');
        },
        errorMessage => {
          console.warn("Error escaneando:", errorMessage);
        }
      ).catch(err => {
        alert("❌ No se pudo iniciar el escáner de cámara. Verifica los permisos o intenta con otro navegador.");
        console.error("Error al iniciar escáner:", err);
        document.getElementById("retry-btn").style.display = "inline-block";
      });
    }

    navigator.mediaDevices.getUserMedia({ video: true })
      .then(function(stream) {
        Html5Qrcode.getCameras().then(cameras => {
          if (cameras.length === 0) {
            alert("⚠️ No se detectaron cámaras.");
            document.getElementById("retry-btn").style.display = "inline-block";
            return;
          }

          cameraSelect.style.display = "inline-block";
          cameraSelect.innerHTML = cameras.map(
            cam => `<option value=\"${cam.id}\">${cam.label}</option>`
          ).join("");

          cameraSelect.onchange = () => {
            html5QrCode.stop().then(() => {
              startScanner(cameraSelect.value);
            }).catch(err => {
              console.error("Error al cambiar de cámara:", err);
            });
          };

          startScanner(cameras[0].id);

        }).catch(err => {
          alert("❌ No se pudieron obtener las cámaras. Revisa si otra aplicación está usándola o verifica los permisos del navegador.");
          console.error("Error detectando cámaras:", err);
          document.getElementById("retry-btn").style.display = "inline-block";
        });
      })
      .catch(function(err) {
        alert("❌ Acceso a cámara denegado. Por favor verifica los permisos del navegador o sistema.\n\nDetalles: " + err);
        console.error("Error de permisos:", err);
        document.getElementById("retry-btn").style.display = "inline-block";
      });
  </script>
</body>
</html>
"""

components.html(html_code, height=700)

# --- Google Sheets ---
@st.cache_resource
def conectar_hoja():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["GOOGLE_SHEETS_CREDENTIALS"], scope)
        client = gspread.authorize(creds)
        hoja = client.open_by_key("1yWJoHTzHRwxCPQCnthm2MCgD2DFO--fQEgqMq0_fbCM").worksheet("DatosQR")
        return hoja
    except Exception as e:
        st.error(f"Error conectando hoja: {e}")
        return None

sheet = conectar_hoja()

# --- Captura del código QR desde mensaje recibido del iframe ---
qr_code_placeholder = st.empty()

components.html("""
<script>
  window.addEventListener("message", (event) => {
    if (event.data.type === "qr_code_scanned") {
      const params = new URLSearchParams(window.location.search);
      params.set("scanned", event.data.data);
      window.location.search = params.toString();
    }
  });
</script>
""", height=0)

query_params = st.experimental_get_query_params()
if "scanned" in query_params:
    qr_code = query_params["scanned"][0]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if sheet:
        try:
            sheet.append_row([qr_code, timestamp])
            st.success(f"✅ Escaneado: {qr_code}")
        except Exception as e:
            st.error(f"❌ Error al registrar: {e}")






