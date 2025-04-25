@echo off
cd /d C:\ikwbolero\Proyecto\QR
echo Iniciando servidor en http://192.168.1.75:8000
start http://192.168.1.75:8000
python -m http.server 8000
pause
