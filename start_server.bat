@echo off
echo Iniciando el servidor de SERVICED...
cd serviced-backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
