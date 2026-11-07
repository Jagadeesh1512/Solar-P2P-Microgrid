@echo off
title Decentralized Solar Microgrid Runner
echo ============================================================
echo   Decentralized Solar Microgrid & P2P Energy Sharing
echo   Full Software Stack + Hardware Simulation Environment
echo ============================================================

cd /d "%~dp0"

echo [1/2] Starting Backend Server on http://localhost:8000...
start "Microgrid Backend (FastAPI)" cmd /k "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Starting Frontend UI on http://localhost:5173...
cd frontend
start "Microgrid Frontend (Vite)" cmd /k "npm run dev"

echo.
echo Application launched!
echo Open your browser at: http://localhost:5173
echo.
pause
