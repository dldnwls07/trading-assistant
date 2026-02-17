@echo off
setlocal

:: Get Local IP Address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
)
set IP=%IP:~1%

echo ========================================================
echo  🚀 Trading Assistant Server (Laptop Mode)
echo ========================================================
echo  Your Local IP Address: %IP%
echo  Access via Phone/PC: http://%IP%:8000
echo ========================================================

:: Check if .venv exists
if not exist ".venv" (
    echo [INFO] Creating Virtual Environment (.venv)...
    python -m venv .venv
)

:: Activate Virtual Environment
call .venv\Scripts\activate

:: Check if requirements.txt exists and install dependencies
if exist "requirements.txt" (
    echo [INFO] Installing Python Dependencies...
    pip install -r requirements.txt
) else (
    echo [ERROR] requirements.txt not found! Exiting...
    pause
    exit /b 1
)

:: Build Frontend (if node exists)
where npm >nul 2>nul
if %errorlevel% equ 0 (
    if exist "frontend" (
        echo [INFO] Building Frontend...
        cd frontend
        call npm install
        call npm run build
        cd ..
    )
) else (
    echo [WARNING] Node.js not found. Skipping Frontend Build.
    echo Server will run in API-only mode if static files are missing.
)

:: Run Server (Host 0.0.0.0 allows external access)
echo [INFO] Starting Server on 0.0.0.0:8000...
python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000

endlocal
pause
