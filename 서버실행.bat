@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ===========================================
echo   🚀 Trading Assistant API 서버 시작...
echo   (크롬 확장 프로그램 연동용)
echo ===========================================

cd /d "%~dp0"

:: 가상환경 체크 및 활성화
if exist ".venv\Scripts\activate.bat" (
    echo [정보] 가상환경(.venv)을 활성화합니다.
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo [정보] 가상환경(venv)을 활성화합니다.
    call venv\Scripts\activate.bat
)

:: Python 명령어 결정
set PYTHON_CMD=python
py --version >nul 2>&1
if %errorlevel% equ 0 set PYTHON_CMD=py

:: 서버 실행
echo [정보] 로컬 서버를 시작합니다 (http://127.0.0.1:8000)
echo [팁] 이 창을 닫지 마세요! (최소화 해두세요)
echo.

%PYTHON_CMD% -m uvicorn src.api.server:app --host 127.0.0.1 --port 8000 --reload

if %errorlevel% neq 0 (
    echo.
    echo ❌ 서버 실행 중 오류가 발생했습니다.
    pause
)
