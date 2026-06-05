@echo off
title TradeMind AI MVP Launcher
color 0A

echo ==========================================================
echo       TradeMind AI MVP - KHOI DONG HE THONG DEV
echo ==========================================================
echo.
echo Dang chuan bi khoi chay Backend va Frontend...
echo Cửa sổ terminal mới sẽ được mở cho từng dịch vụ.
echo.

:: Khoi chay Backend FastAPI
echo [1/2] Dang khoi dong Backend (FastAPI tại port 8000)...
start "TradeMind Backend (FastAPI)" cmd /k "cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000"

:: Cho 2 giay de Backend on dinh
timeout /t 2 /nobreak >nul

:: Khoi chay Frontend React/Vite
echo [2/2] Dang khoi dong Frontend (React/Vite tại port 5173)...
start "TradeMind Frontend (React/Vite)" cmd /k "cd frontend && npm run dev"

echo.
echo ==========================================================
echo KHOI DONG THANH CONG!
echo - API Backend: http://localhost:8000 (Swagger: /docs)
echo - Web Frontend: http://localhost:5173
echo ==========================================================
echo.
echo Nhan phim bat ky de thoat trinh khoi chay...
pause >nul
