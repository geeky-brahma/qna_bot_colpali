@echo off
REM Quick start script for Windows

echo ======================================
echo RAG Production System - Local Setup
echo ======================================

cd /d "%~dp0"

echo Checking prerequisites...

where python >nul 2>nul
if errorlevel 1 (
    echo ❌ Python 3.10+ not found
    exit /b 1
)

where node >nul 2>nul
if errorlevel 1 (
    echo ❌ Node.js 18+ not found
    exit /b 1
)

echo ✓ Python and Node.js found

REM Frontend
echo Setting up Frontend...
cd frontend
call npm install
copy .env.local.example .env.local
echo ✓ Frontend setup complete
echo   Edit frontend\.env.local with Google OAuth credentials

REM API Backend
echo Setting up API Backend...
cd ..\api-backend
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
echo ✓ API Backend setup complete
echo   Edit api-backend\.env with Pinecone credentials

REM Inference Backend
echo Setting up Inference Backend...
cd ..\inference-backend
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
echo ✓ Inference Backend setup complete
echo   Edit inference-backend\.env with GCP credentials

echo.
echo ======================================
echo Setup Complete!
echo ======================================
echo.
echo Next steps:
echo 1. Edit environment files with your credentials
echo 2. Run in separate terminals:
echo.
echo    REM Terminal 1: Inference
echo    cd inference-backend
echo    venv\Scripts\activate.bat
echo    functions-framework --target colpali_query --debug
echo.
echo    REM Terminal 2: API
echo    cd api-backend
echo    venv\Scripts\activate.bat
echo    python main.py
echo.
echo    REM Terminal 3: Frontend
echo    cd frontend
echo    npm run dev
echo.
echo 3. Open http://localhost:3000
