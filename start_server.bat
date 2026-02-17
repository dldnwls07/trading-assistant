@echo off
chcp 65001 >nul
setlocal

:: [중요] 스크립트가 있는 폴더로 이동 (관리자 실행 시 오류 방지)
cd /d "%~dp0"

echo ========================================================
echo  🚀 Trading Assistant Server (Laptop Mode)
echo ========================================================
echo.

:: 가상환경 생성 (.venv)
if not exist ".venv" (
    echo [INFO] Creating Virtual Environment (.venv)...
    python -m venv .venv
)

:: 가상환경 활성화
if exist ".venv\Scripts\activate" (
    call .venv\Scripts\activate
) else (
    echo [ERROR] Virtual environment activation failed!
    pause
    exit /b 1
)

:: 의존성 설치 (requirements.txt)
if exist "requirements.txt" (
    echo [INFO] Installing Python Dependencies (this may take a while)...
    pip install -r requirements.txt
) else (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)

:: 프론트엔드 빌드 (Node.js 있으면)
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
)

:: IP 주소 출력 (참고용)
echo.
echo [NETWORK INFO]
ipconfig | findstr /c:"IPv4"
echo.

:: 서버 실행
echo [INFO] Starting Server on 0.0.0.0:8000...
echo        - Access Locally: http://localhost:8000
echo        - Access Remotely: Use the IPv4 Address shown above
echo.

python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload

endlocal
pause
