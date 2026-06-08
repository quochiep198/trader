@echo off
title TradeMind AI MVP Launcher
color 0A

echo ==========================================================
echo       TradeMind AI MVP - KHOI DONG HE THONG DEV
echo ==========================================================
echo.
echo Dang chuan bi khoi chay Backend va Frontend...
echo Terminal moi se duoc mo cho tung dich vu.
echo.

:: Khoi chay Backend FastAPI
echo [1/2] Dang khoi dong Backend (FastAPI tai port 8000)...
start "TradeMind Backend (FastAPI)" cmd /k "cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

:: Cho 2 giay de Backend on dinh
timeout /t 2 /nobreak >nul

:: Khoi chay Frontend React/Vite
echo [2/2] Dang khoi dong Frontend (React/Vite tai port 5173)...
start "TradeMind Frontend (React/Vite)" cmd /k "cd frontend && npm run dev -- --host 0.0.0.0"

echo.
echo ==========================================================
echo KHOI DONG THANH CONG!
echo - API Backend: http://192.168.3.132:8000 (Swagger: /docs)
echo - Web Frontend (PC): http://localhost:5173
echo - Mobile/Wi-Fi: http://192.168.3.132:5173
echo ==========================================================
echo.
echo Nhan phim bat ky de thoat trinh khoi chay...
pause >nul
