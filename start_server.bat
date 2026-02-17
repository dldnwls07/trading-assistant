@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ========================================================
echo  🚀 Trading Assistant Server (Split Window Mode)
echo ========================================================

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed.
    pause
    exit /b 1
)

:: 2. Venv Setup
if not exist ".venv" (
    echo [INFO] Creating Virtual Environment...
    python -m venv .venv
)
call .venv\Scripts\activate

:: 3. Dependencies
if exist "requirements.txt" (
    echo [INFO] Checking dependencies...
    pip install -r requirements.txt >nul
)

:: 4. Build Frontend (Silent)
where npm >nul 2>nul
if %errorlevel% equ 0 (
    if exist "frontend" (
        cd frontend
        echo [INFO] Building Frontend...
        call npm install >nul 2>&1
        call npm run build
        cd ..
    )
)

:: 5. Get IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
)
set IP=%IP:~1%

echo.
echo ========================================================
echo  ✅ Setup Complete!
echo  
echo  Opening new window for the Server...
echo  Please Keep THIS window open to check the address.
echo.
echo  👉 Local Access:     http://localhost:8000
echo  👉 Network Access:   http://%IP%:8000
echo ========================================================

:: 6. Launch Server in NEW Window
start "Trading Assistant Server - DO NOT CLOSE" cmd /k "call .venv\Scripts\activate && python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload"

pause
