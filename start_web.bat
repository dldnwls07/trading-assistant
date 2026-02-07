@echo off
setlocal
cd /d "%~dp0"

echo [1/3] Backend starting...
start cmd /k "uvicorn src.api.server:app --host 0.0.0.0 --port 8000"

echo [2/3] Frontend starting...
cd frontend
start cmd /k "npm run dev"

echo [3/3] DONE! Open http://localhost:5173 to see your Premium Dashboard.
pause
