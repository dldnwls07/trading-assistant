@echo off
chcp 65001

echo Starting backend server...
start "Trading Assistant Backend" cmd /c "python -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload"

echo Starting frontend development server...
start "Trading Assistant Frontend" cmd /c "cd frontend && npm run dev"

echo Both servers are starting in separate windows.

echo Opening application in your browser in 5 seconds...
timeout /t 5 /nobreak > nul
start http://localhost:5173

echo You can close this window now.