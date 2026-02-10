@echo off
echo ========================================
echo  AI 트레이딩 어시스턴트 v2.0
echo ========================================
echo.
echo 웹 서버를 시작합니다...
echo.

cd /d "%~dp0"

streamlit run app.py

pause
