@echo off
setlocal

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

:: Run Server
echo [INFO] Starting Trading Assistant Server...
echo [INFO] Access via http://localhost:8000
python -m uvicorn src.api.server:app --reload --port 8000

endlocal
pause
