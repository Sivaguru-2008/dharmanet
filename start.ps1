# DharmaNet Startup Script for PowerShell
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "Starting DharmaNet on Dedicated Ports:" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8005" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3005" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan

$root = $PSScriptRoot

Write-Host "`n[1/3] Starting FastAPI Backend on http://localhost:8005..." -ForegroundColor Yellow
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "Set-Location '$root/backend'; .venv/Scripts/python -m uvicorn app.main:create_app --factory --port 8005"

Start-Sleep -Seconds 3

Write-Host "[2/3] Starting Next.js Frontend on http://localhost:3005..." -ForegroundColor Yellow
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "Set-Location '$root/frontend'; npm run dev"

Start-Sleep -Seconds 3

Write-Host "[3/3] Opening Browser at http://localhost:3005..." -ForegroundColor Green
Start-Process "http://localhost:3005"

Write-Host "`n===================================================" -ForegroundColor Cyan
Write-Host "DharmaNet is running!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3005"
Write-Host "Backend API docs: http://localhost:8005/docs"
Write-Host "===================================================" -ForegroundColor Cyan
