Write-Host "==========================================================" -ForegroundColor Yellow
Write-Host "  Decentralized Solar Microgrid & P2P Energy Sharing      " -ForegroundColor Green
Write-Host "  Full Software Stack + Hardware Simulation Environment   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Yellow

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start Backend in Background Process
Write-Host "`n[1/2] Launching FastAPI Backend on http://localhost:8000..." -ForegroundColor Cyan
$backendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir'; python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload" -PassThru

# 2. Start Frontend in Background Process
Write-Host "[2/2] Launching React Vite Dashboard on http://localhost:5173..." -ForegroundColor Cyan
$frontendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir\frontend'; npm run dev" -PassThru

Write-Host "`nMicrogrid platform is now running!" -ForegroundColor Green
Write-Host "  - UI Dashboard:      http://localhost:5173" -ForegroundColor Yellow
Write-Host "  - Backend API & Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "  - Wokwi Node Sketch:  $rootDir\simulation\wokwi\sketch.ino" -ForegroundColor Yellow
