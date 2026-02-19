@echo off
REM RIFT 2026 - Money Muling Detection Engine
REM Batch file for Windows

echo.
echo 🚀 Starting RIFT 2026 Money Muling Detection Engine...
echo.

REM Check if we're in the right directory
if not exist "run.bat" (
    echo ❌ Error: Script must be run from the project root directory
    exit /b 1
)

REM Start Backend
echo 📦 Starting Backend (FastAPI)...
cd backend

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
if exist "requirements.txt" (
    pip install -r requirements.txt --quiet
)

REM Start FastAPI server in background
start "FastAPI Server" cmd /k uvicorn app.main:app --host 0.0.0.0 --port 8000
timeout /t 3 /nobreak

echo ✅ Backend started
echo    📍 Available at: http://localhost:8000
echo    📚 API docs at: http://localhost:8000/docs
echo.

REM Start Frontend
echo ⚛️  Starting Frontend (React + Vite)...
cd ..\frontend

REM Check if Node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16+
    exit /b 1
)

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing npm dependencies...
    call npm install --silent
)

REM Start Vite dev server in background
start "React Dev Server" cmd /k npm run dev

echo ✅ Frontend started
echo    📍 Available at: http://localhost:5173
echo.

echo ===========================================
echo ✨ RIFT 2026 is now running!
echo ===========================================
echo.
echo 🌐 Frontend:  http://localhost:5173
echo 🔧 Backend:   http://localhost:8000
echo 📚 API Docs:  http://localhost:8000/docs
echo.
echo Close the terminal windows to stop services
echo.
pause
