@echo off
setlocal
cd /d "%~dp0"

echo ===================================================
echo Starting DharmaNet on Dedicated Ports:
echo Backend:  http://localhost:8005
echo Frontend: http://localhost:3005
echo ===================================================

echo [1/3] Starting FastAPI Backend on port 8005 ...
start "DharmaNet Backend" powershell -NoExit -Command "Set-Location '%~dp0backend'; .\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --port 8005"

timeout /t 3 /nobreak >nul

echo [2/3] Starting Next.js Frontend on port 3005 ...
start "DharmaNet Frontend" powershell -NoExit -Command "Set-Location '%~dp0frontend'; npm run dev"

timeout /t 4 /nobreak >nul

echo [3/3] Opening Browser at http://localhost:3005 ...
start http://localhost:3005

echo.
echo ===================================================
echo DharmaNet is running!
echo Frontend: http://localhost:3005
echo Backend:  http://localhost:8005/docs
echo Close the two command windows when finished.
echo ===================================================
