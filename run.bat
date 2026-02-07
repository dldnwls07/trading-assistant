@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ===========================================
echo   🚀 트레이딩 어시스턴트 실행 중...
echo ===========================================

rem 현재 폴더로 이동 (드라이브 변경 포함)
cd /d "%~dp0"

rem 가상환경 파이썬 직접 지정 (절대 경로)
set PYTHON_EXE="%~dp0.venv\Scripts\python.exe"
set PIP_EXE="%~dp0.venv\Scripts\pip.exe"

rem 필독: 라이브러리 자동 설치 (화면에 진행 상황이 표시됩니다)
echo [준비] 필수 라이브러리 설치 중... (약 1~3분 소요)
%PIP_EXE% install -r requirements.txt

rem 실행 (오류 로그 기록)
echo [정보] %PYTHON_EXE% 사용 중...
%PYTHON_EXE% src/ui/overlay.py 2> error.log

if %errorlevel% neq 0 (
    echo.
    echo ❌ 프로그램 실행 중 오류가 발생했습니다!
    echo 📂 error.log 확인 결과:
    echo ---------------------------------------------------
    type error.log
    echo ---------------------------------------------------
    pause
)

exit
