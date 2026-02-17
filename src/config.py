import os
from pathlib import Path
from typing import Dict, List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator

# SSL 인증서 경로 설정 (yfinance curl_cffi 오류 해결)
# TODO (에이전트): yfinance의 curl_cffi가 가상환경(.venv)의 잘못된 경로를 참조하는 문제 해결
try:
    import certifi
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['CURL_CA_BUNDLE'] = certifi.where()
except ImportError:
    pass  # certifi가 없으면 시스템 기본값 사용

# 기본 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHART_DIR = BASE_DIR / "charts"

# 디렉토리 자동 생성
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    """
    중앙 설정 관리 클래스 (Pydantic Settings)
    환경 변수 및 기본값 자동 로드 및 유효성 검사
    """
    # API Keys
    HF_TOKEN: str = Field(default="")
    GEMINI_API_KEY: str = Field(default="")
    GROQ_API_KEY: str = Field(default="")
    FRED_API_KEY: str = Field(default="")
    TRADING_ECONOMICS_KEY: str = Field(default="")
    
    # DB & Infrastructure
    DB_PATH: str = Field(default="trading_assistant.db")
    
    # Analysis Configuration
    DEFAULT_INTERVAL: str = "1d"
    SUPPORTED_INTERVALS: List[str] = ["1m", "5m", "15m", "60m", "1d", "1wk"]
    
    ANALYSIS_WEIGHTS: Dict[str, float] = {
        "technical": 0.6,
        "fundamental": 0.4
    }
    
    # RSI & Indicators
    RSI_OVERSOLD: int = 30
    RSI_OVERBOUGHT: int = 70
    SMA_SHORT: int = 20
    SMA_MEDIUM: int = 50
    SMA_LONG: int = 200
    BOLLINGER_WINDOW: int = 20
    BOLLINGER_STD: int = 2

    # Signal Thresholds
    SIGNAL_THRESHOLDS: Dict[str, float] = {
        "strong_buy": 85,
        "buy": 70,
        "hold_upper": 55,
        "hold_lower": 40,
        "sell": 25,
        "strong_sell": 0
    }

    # UI Design Tokens
    UI_COLORS: Dict[str, str] = {
        "bg_primary": "#1a1a2e",
        "bg_secondary": "#16213e",
        "bg_tertiary": "#0f3460",
        "fg_primary": "#eaeaea",
        "fg_secondary": "#aaaaaa",
        "fg_muted": "#888888",
        "accent": "#00d4ff",
        "buy": "#ff4757",      # 상승
        "sell": "#3742fa",     # 하락
        "neutral": "#ffa502",
        "success": "#4CAF50",
        "warning": "#FF9800",
        "error": "#F44336"
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# 싱글톤 인스턴스 생성
settings = Settings()

# 레거시 코드 호환성을 위한 전역 변수 유지
HF_TOKEN = settings.HF_TOKEN
GEMINI_API_KEY = settings.GEMINI_API_KEY
GROQ_API_KEY = settings.GROQ_API_KEY
DB_PATH = settings.DB_PATH
DEFAULT_INTERVAL = settings.DEFAULT_INTERVAL
SUPPORTED_INTERVALS = settings.SUPPORTED_INTERVALS
ANALYSIS_WEIGHTS = settings.ANALYSIS_WEIGHTS
RSI_OVERSOLD = settings.RSI_OVERSOLD
RSI_OVERBOUGHT = settings.RSI_OVERBOUGHT
SMA_SHORT = settings.SMA_SHORT
SMA_MEDIUM = settings.SMA_MEDIUM
SMA_LONG = settings.SMA_LONG
BOLLINGER_WINDOW = settings.BOLLINGER_WINDOW
BOLLINGER_STD = settings.BOLLINGER_STD
SIGNAL_THRESHOLDS = settings.SIGNAL_THRESHOLDS
UI_COLORS = settings.UI_COLORS

def validate_config():
    """설정 유효성 검사 (확장 가능)"""
    warnings = []
    if not settings.HF_TOKEN:
        warnings.append("HF_TOKEN이 설정되지 않았습니다. AI 분석 기능이 제한됩니다.")
    if not settings.GEMINI_API_KEY:
        warnings.append("GEMINI_API_KEY가 설정되지 않았습니다. 메인 AI 기능을 사용할 수 없습니다.")
    return warnings
