@echo off
chcp 65001 >nul
echo ========================================
echo  AI 트레이딩 어시스턴트 v2.0
echo  FastAPI + React 통합 서버
echo ========================================
echo.
echo [1/2] FastAPI 백엔드 서버 시작...
start cmd /k "cd /d %~dp0 && uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] React 프론트엔드 서버 시작...
cd frontend
start cmd /k "npm run dev"

echo.
echo ========================================
echo  서버가 시작되었습니다!
echo ========================================
echo.
echo  - 백엔드 API: http://localhost:8000
echo  - API 문서: http://localhost:8000/docs
echo  - 프론트엔드: http://localhost:5173
echo.
echo  브라우저에서 http://localhost:5173 을 열어주세요!
echo ========================================
pause
