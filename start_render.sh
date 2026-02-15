#!/bin/bash

# 1. AI 트레이딩 엔진을 백그라운드에서 실행
echo "Starting AI Trading Engine..."
python -m src.agents.auto_trader &

# 2. 알림 워커를 백그라운드에서 실행
echo "Starting Alert Worker..."
python -m src.api.alert_worker &

# 3. FastAPI 서버를 메인 프로세스로 실행 (Render가 포트를 감시함)
echo "Starting FastAPI Server..."
uvicorn src.api.server:app --host 0.0.0.0 --port $PORT
