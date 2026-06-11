@echo off
REM ============================================
REM ATS Resume Analyzer v2.0.0
REM One-Click Startup Script for Windows
REM ============================================

cls
echo.
echo ============================================
echo  ATS Resume Analyzer v2.0.0
echo  Starting System...
echo ============================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Kill any existing Python processes on ports 8000/8501
echo Cleaning up old processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501"') do taskkill /PID %%a /F 2>nul
timeout /t 2 /nobreak

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

REM Start Backend
echo.
echo Starting Backend on port 8000...
start "ATS Backend" cmd /k "cd /d %cd% && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
timeout /t 5 /nobreak

REM Start Frontend
echo Starting Frontend on port 8501...
start "ATS Frontend" cmd /k "cd /d %cd% && python -m streamlit run frontend/streamlit_app.py"
timeout /t 3 /nobreak

REM Open Browser
echo.
echo Opening browser...
start "" "http://localhost:8501"

echo.
echo ============================================
echo  SYSTEM STARTED!
echo ============================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8501
echo.
echo 1. Upload your resume
echo 2. Wait 50-70 seconds
echo 3. Get your ATS score!
echo.
echo To stop: Close both console windows
echo.
pause
