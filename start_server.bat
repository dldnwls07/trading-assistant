@echo off
setlocal enabledelayedexpansion

echo [INFO] Script Directory: %~dp0
cd /d "%~dp0"

echo ========================================================
echo  🚀 Trading Assistant Server (Debug Mode)
echo ========================================================

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: 2. Setup/Activate Venv
if not exist ".venv" (
    echo [INFO] Creating Virtual Environment...
    python -m venv .venv || pause && exit /b 1
)

echo [INFO] Activating Virtual Environment...
call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate .venv
    pause
    exit /b 1
)

:: 3. Install Dependencies
echo [INFO] Checking dependencies...
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt missing!
    pause
    exit /b 1
)
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: 4. Build Frontend (Try-Catch style)
echo [INFO] Checking Frontend...
where npm >nul 2>nul
if %errorlevel% equ 0 (
    if exist "frontend" (
        cd frontend
        echo [INFO] Installing Frontend Deps...
        call npm install
        echo [INFO] Building Frontend...
        call npm run build
        cd ..
    )
) else (
    echo [WARNING] npm not found. Skipping frontend build.
)

:: 5. Start Server
echo.
echo [INFO] Starting Uvicorn Server...
echo [INFO] Open http://localhost:8000 in your browser.
echo.

python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload

if %errorlevel% neq 0 (
    echo [ERROR] Server crashed with error code !errorlevel!
    pause
)

pause
