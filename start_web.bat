@echo off
chcp 65001 >nul
setlocal

echo ========================================
echo  AI 트레이딩 어시스턴트 v2.0 통합 시작
echo ========================================

:: 경로 설정 및 이동
cd /d "%~dp0"
set PYTHONPATH=%cd%

:: [해결책 1] 이미 사용 중인 8000번 포트 강제 종료
echo.
echo [1/4] 포트 충돌 확인 및 해결 중...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo 기존 서버(PID: %%a^)를 종료합니다.
    taskkill /f /pid %%a >nul 2>&1
)

:: [해결책 2] src 모듈 인식 문제 방지를 위해 __init__.py 확인
if not exist "src\api\__init__.py" type nul > "src\api\__init__.py"

timeout /t 1 /nobreak >nul

echo.
echo [2/4] FastAPI 백엔드 서버 시작...
start "BACKEND" cmd /k "set PYTHONPATH=%cd% && uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo.
echo [3/4] 알림 워커(Alert Worker) 시작...
:: -m 모듈 방식을 사용하여 경로 문제 해결
start "WORKER" cmd /k "set PYTHONPATH=%cd% && python -m src.api.alert_worker"

timeout /t 2 /nobreak >nul

echo.
echo [4/4] React 프론트엔드 서버 시작...
cd frontend
start "FRONTEND" cmd /k "npm run dev"

echo.
echo ========================================
echo  모든 서비스가 재시작되었습니다!
echo ========================================
echo  - 백엔드: http://localhost:8000
echo  - 프론트엔드: http://localhost:5173
echo ========================================
pause
