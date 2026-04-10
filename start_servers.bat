@echo off
REM Start Backend and Frontend Servers

cd /d "C:\Users\zzeel\OneDrive\Desktop\AutoDevOS"

REM Activate virtual environment
call .venv\Scripts\activate.bat

echo.
echo ========================================
echo Starting AutoDevOS Servers
echo ========================================
echo.

REM Start FastAPI Backend (Port 8000)
echo [1/2] Starting FastAPI Backend on http://localhost:8000
start "AutoDevOS Backend" cmd /k python -m uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload

REM Wait a moment for backend to start
timeout /t 2 /nobreak

REM Start Next.js Frontend (Port 3000)
echo [2/2] Starting Next.js Frontend on http://localhost:3000
cd frontend
start "AutoDevOS Frontend" cmd /k npm run dev

echo.
echo ========================================
echo Both servers starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo ========================================
