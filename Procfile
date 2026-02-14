web: uvicorn src.api.server:app --host 0.0.0.0 --port ${PORT:-8000}
worker: python -m src.agents.auto_trader
alert: python -m src.api.alert_worker
