@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

:: -------------------------------------------------------------
:: Trading Assistant Launcher (Split Mode)
:: -------------------------------------------------------------

:: 1. Initial Checks (Silent Mode)
python --version >nul 2>&1
if %errorlevel% neq 0 ( exit /b 1 )

if not exist ".venv" ( python -m venv .venv )
call .venv\Scripts\activate

if exist "requirements.txt" ( pip install -r requirements.txt >nul )

where npm >nul 2>nul
if %errorlevel% equ 0 (
    if exist "frontend" (
        cd frontend
        call npm install >nul 2>&1
        call npm run build >nul 2>&1
        cd ..
    )
)

:: 2. Get IP (Robust)
set IP=127.0.0.1
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do ( set IP=%%a )
set IP=%IP:~1%

:: 3. Clear Screen & Show Dashboard (Fixed View)
cls
color 0A

echo.
echo  ========================================================
echo   🚀 AI Trading Assistant v2.0 (Active Server)
echo  ========================================================
echo.
echo   [ACCESS LINKS]  (Keep this window open!)
echo.
echo   👉 Local Access:     http://localhost:8000
echo   👉 Network Access:   http://%IP%:8000
echo.
echo  ========================================================
echo   [STATUS]
echo   - Server PID: Running in separate window...
echo   - Frontend:   Ready
echo   - AI Agent:   Active
echo.
echo   * Press any key to stop server...
echo  ========================================================

:: 4. Launch Server in NEW Window (Logs go there)
start "Trading Assistant Server Logs (DO NOT CLOSE)" cmd /k "call .venv\Scripts\activate && python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload"

pause >nul
