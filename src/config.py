"""
중앙 설정 관리 모듈
모든 하드코딩된 값을 환경변수 또는 기본값으로 관리
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ===========================================
# 경로 설정
# ===========================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHART_DIR = BASE_DIR / "charts"

# 디렉토리 자동 생성
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

# ===========================================
# 데이터베이스 설정
# ===========================================
DB_PATH = os.getenv("DB_PATH", "trading_assistant.db")

# ===========================================
# API 키 (환경변수에서 로드)
# ===========================================
HF_TOKEN = os.getenv("HF_TOKEN", "")
TRADING_ECONOMICS_KEY = os.getenv("TRADING_ECONOMICS_KEY", "")

# ===========================================
# 분석 설정 (타임프레임 추가)
# ===========================================
DEFAULT_INTERVAL = "1d"  # 기본 일봉
SUPPORTED_INTERVALS = ["1m", "5m", "15m", "60m", "1d", "1wk"]

ANALYSIS_WEIGHTS = {
    "technical": 0.6,  # 기술적 분석 가중치
    "fundamental": 0.4  # 기본적 분석 가중치
}

# RSI 임계값
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# 이동평균 기간
SMA_SHORT = 20
SMA_MEDIUM = 50
SMA_LONG = 200

# 볼린저 밴드 설정
BOLLINGER_WINDOW = 20
BOLLINGER_STD = 2

# ===========================================
# UI 스타일 설정
# ===========================================
UI_COLORS = {
    "bg_primary": "#1a1a2e",
    "bg_secondary": "#16213e",
    "bg_tertiary": "#0f3460",
    "fg_primary": "#eaeaea",
    "fg_secondary": "#aaaaaa",
    "fg_muted": "#888888",
    "accent": "#00d4ff",
    "buy": "#ff4757",      # 한국식: 빨간색 = 상승
    "sell": "#3742fa",     # 한국식: 파란색 = 하락
    "neutral": "#ffa502",
    "success": "#4CAF50",
    "warning": "#FF9800",
    "error": "#F44336"
}

UI_FONTS = {
    "primary": "맑은 고딕",
    "fallback": "Arial"
}

# ===========================================
# 신호 임계값
# ===========================================
SIGNAL_THRESHOLDS = {
    "strong_buy": 85,
    "buy": 70,
    "hold_upper": 55,
    "hold_lower": 40,
    "sell": 25,
    "strong_sell": 0
}

# ===========================================
# 유효성 검사
# ===========================================
def validate_config():
    """설정 유효성 검사"""
    warnings = []
    
    if not HF_TOKEN or HF_TOKEN == "your_huggingface_token_here":
        warnings.append("HF_TOKEN이 설정되지 않았습니다. AI 분석 기능이 제한됩니다.")
    
    if ALPACA_API_KEY and ALPACA_API_KEY.startswith("PK"):
        warnings.append("Alpaca API Key가 노출된 것 같습니다. 재발급을 권장합니다.")
    
    return warnings

# 모듈 로드 시 검증
_warnings = validate_config()
if _warnings:
    import logging
    logger = logging.getLogger(__name__)
    for w in _warnings:
        logger.warning(w)
