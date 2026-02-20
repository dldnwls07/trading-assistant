#!/bin/bash

# 1. DB 마이그레이션 실행 방어 로직 (파일이 있을 때만 실행)
if [ -f "migrate_v2.py" ]; then
    echo "Running Database Migration..."
    python migrate_v2.py
else
    echo "migrate_v2.py not found. Skipping migration."
fi

# 2. FastAPI 서버를 메인 프로세스로 실행 (Render가 포트를 감시함)
echo "Starting FastAPI Server with Internal Workers..."
# Render 환경에서는 $PORT가 주어지지만 없을 경우 8000번 포트로 fallback
uvicorn src.api.server:app --host 0.0.0.0 --port ${PORT:-8000}
