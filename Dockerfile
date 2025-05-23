FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY visor_qr.py .
COPY registro-eventos-hugo-a97cbe9d7f0f.json .

EXPOSE 8501

CMD ["streamlit", "run", "visor_qr.py", "--server.port=8501", "--server.address=0.0.0.0"]

