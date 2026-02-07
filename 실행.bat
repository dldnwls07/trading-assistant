@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ===========================================
echo   📊 Trading Assistant 실행 중...
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

:: 의존성 체크 (필요시 설치)
echo [정보] 라이브러리 체크 중... (%PYTHON_CMD% 사용)
%PYTHON_CMD% -c "import yfinance, pyperclip, PIL" 2>nul
if %errorlevel% neq 0 (
    echo [경고] 필수 라이브러리가 없습니다. 자동 설치를 시도합니다...
    %PYTHON_CMD% -m pip install -r requirements.txt
)

echo [정보] 프로그램을 시작합니다. 잠시만 기다려주세요...
echo.

%PYTHON_CMD% src/ui/overlay.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 프로그램이 예기치 않게 종료되었습니다.
    echo 위의 오류 메시지를 확인해주세요.
    pause
)

exit
