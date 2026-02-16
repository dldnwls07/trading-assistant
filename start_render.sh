#!/bin/bash

# 1. DB 마이그레이션 실행 (필요 시)
echo "Running Database Migration..."
python migrate_v2.py

# 2. FastAPI 서버를 메인 프로세스로 실행 (Render가 포트를 감시함)
# server.py의 lifespan에서 AutoTrader와 AlertWorker가 자동으로 백그라운드 태스크로 시작됩니다.
echo "Starting FastAPI Server with Internal Workers..."
uvicorn src.api.server:app --host 0.0.0.0 --port $PORT
