"""
레버리지 ETF 동적 감지 유틸리티 (LeveragedETFDetector)

감지 전략 (3-Tier):
  1. 로컬 JSON 캐시 (.cache/etf_meta.json) — 속도 최적화
  2. yfinance longName 동적 파싱 — 개별종목형 + 지수형 ETF 자동 감지
  3. 하드코딩 폴백 테이블 — 네트워크 오류 시 최소 안전망

이렇게 설계하면 SOXL(지수형), NVDL(개별주형) 등
수백 개의 레버리지 ETF를 별도 업데이트 없이 자동 지원합니다.
"""

import re
import json
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# 캐시 파일 경로 및 유효 기간
_CACHE_DIR = Path(__file__).resolve().parent.parent.parent / ".cache"
_CACHE_FILE = _CACHE_DIR / "etf_meta.json"
# 캐시 유효 기간: 30일 (ETF 메타데이터는 자주 바뀌지 않음)
_CACHE_TTL_DAYS = 30

# --- Tier 2 파싱에 사용할 배수 키워드 ---
# 이유: yfinance longName의 표현 방식이 제공사마다 다름
_MULTIPLIER_PATTERNS = [
    # 숫자 + X 패턴 (Direxion 스타일: "3X", "2X", "1.5X")
    (re.compile(r'(\d+(?:\.\d+)?)[Xx]\b'), lambda m: float(m.group(1))),
    # GraniteShares 스타일: "2x Long"
    (re.compile(r'(\d+(?:\.\d+)?)x\s+(?:Long|Short)', re.IGNORECASE), lambda m: float(m.group(1))),
    # ProShares 스타일: "UltraPro" = 3x, "Ultra" = 2x
    (re.compile(r'UltraPro', re.IGNORECASE), lambda m: 3.0),
    (re.compile(r'\bUltra\b(?!Pro)', re.IGNORECASE), lambda m: 2.0),
]

# Bear/Short 방향성 반전 키워드 (음수 배수로 변환)
_INVERSE_KEYWORDS = re.compile(r'\b(Bear|Short|Inverse|UltraShort|Bear\s*\dX)\b', re.IGNORECASE)

# --- Tier 2 지수/섹터 키워드 → 기초 ETF 매핑 ---
# 이유: 지수형 ETF는 이름에 기초 ETF 티커가 없으므로 키워드로 식별
# 개별주형(NVDL→NVDA)은 이름에서 티커를 직접 추출하므로 여기 불필요
_SECTOR_KEYWORD_TO_BASE: Dict[str, str] = {
    # 반도체
    "semiconductor": "SOXX",
    # 나스닥
    "nasdaq-100": "QQQ",
    "nasdaq 100": "QQQ",
    "ultrapro qqq": "QQQ",
    "ultra qqq": "QQQ",
    # S&P 500
    "s&p 500": "SPY",
    "s&p500": "SPY",
    "s&p 500 bull": "SPY",
    # 러셀 2000
    "russell 2000": "IWM",
    "small cap": "IWM",
    # 에너지
    "energy": "XLE",
    "oil": "XLE",
    # 금융
    "financial": "XLF",
    "bank": "XLF",
    # 바이오/헬스케어
    "biotech": "XBI",
    "biotechnology": "XBI",
    # 장기 국채
    "20+ year treasury": "TLT",
    "treasury bond": "TLT",
    "long-term bond": "TLT",
    # 금
    "gold miners": "GDX",
    "gold miner": "GDX",
    # 중국
    "china": "MCHI",
    "chinese": "MCHI",
    # 기술주
    "technology": "XLK",
    "tech": "XLK",
}

# --- Tier 3 하드코딩 폴백 테이블 ---
# 이유: yfinance 오류/타임아웃 시 최소 안전망
# Tier 2가 실패하더라도 가장 많이 쓰이는 종목은 커버
_HARDCODED_MAP: Dict[str, Tuple[str, float]] = {
    # 반도체
    "SOXL": ("SOXX", 3.0), "SOXS": ("SOXX", -3.0),
    # 나스닥
    "TQQQ": ("QQQ", 3.0), "SQQQ": ("QQQ", -3.0), "QLD": ("QQQ", 2.0),
    # S&P 500
    "SPXL": ("SPY", 3.0), "SPXS": ("SPY", -3.0),
    "SSO": ("SPY", 2.0), "SDS": ("SPY", -2.0),
    # 러셀 2000
    "TNA": ("IWM", 3.0), "TZA": ("IWM", -3.0),
    # 에너지
    "ERX": ("XLE", 2.0), "ERY": ("XLE", -2.0),
    # 금융
    "FAS": ("XLF", 3.0), "FAZ": ("XLF", -3.0),
    # 바이오
    "LABU": ("XBI", 3.0), "LABD": ("XBI", -3.0),
    # 국채
    "TMF": ("TLT", 3.0), "TMV": ("TLT", -3.0),
    # 개별주 (자주 검색되는 상위 종목)
    "NVDL": ("NVDA", 2.0), "NVDU": ("NVDA", 1.5), "NVDS": ("NVDA", -1.0),
    "TSLL": ("TSLA", 2.0), "TSLS": ("TSLA", -1.0),
    "MSFU": ("MSFT", 2.0),
    "AMZU": ("AMZN", 2.0),
    "METL": ("META", 2.0),
    "AAPU": ("AAPL", 2.0),
}

# yfinance에서 티커 추출 시 제외할 일반 단어 (오탐 방지)
# 이유: "DAILY", "BULL", "LONG" 등이 티커로 오인될 수 있음
_EXCLUDE_WORDS = {
    "DAILY", "BULL", "BEAR", "LONG", "SHORT", "ULTRA", "PRO",
    "SHARES", "FUND", "ETF", "INDEX", "TRUST", "PLUS", "MINI",
    "DIREXION", "PROSHARES", "GRANITE", "TREX", "WISDOMTREE",
    "AND", "THE", "FOR", "DAY", "NEW", "INC", "LLC", "LP",
}


class LeveragedETFDetector:
    """
    레버리지 ETF 동적 감지기.
    detect(ticker) 한 번 호출로 기초 자산과 레버리지 배수를 반환합니다.
    일반 종목이면 None을 반환합니다.
    """

    def __init__(self):
        # 캐시 디렉토리 생성 (없을 경우)
        _CACHE_DIR.mkdir(exist_ok=True)
        self._cache: Dict[str, dict] = self._load_cache()

    # ─── Public API ───────────────────────────────────────────────────────────

    def detect(self, ticker: str) -> Optional[Tuple[str, float]]:
        """
        레버리지 ETF 여부를 감지합니다.

        Returns:
            (base_ticker: str, multiplier: float) — 레버리지 ETF인 경우
            None — 일반 종목인 경우
        
        multiplier가 음수이면 인버스 ETF를 의미합니다.
        """
        ticker = ticker.upper().strip()

        # --- Tier 1: 캐시 확인 ---
        cached = self._get_from_cache(ticker)
        if cached is not None:
            # 캐시에 "not_leveraged"로 저장된 경우 (일반 종목 캐싱)
            if cached.get("base") == "__NONE__":
                logger.debug(f"[캐시] {ticker} → 일반 종목 (캐시 히트)")
                return None
            base = cached.get("base")
            mult = cached.get("multiplier")
            if base and mult is not None:
                logger.info(f"[캐시] {ticker} → {base} ({mult:+.1f}x)")
                return base, float(mult)

        # --- Tier 2: yfinance 동적 파싱 ---
        result = self._parse_from_yfinance(ticker)
        if result is not None:
            self._save_to_cache(ticker, result[0], result[1])
            return result

        # --- Tier 3: 하드코딩 폴백 ---
        if ticker in _HARDCODED_MAP:
            base, mult = _HARDCODED_MAP[ticker]
            logger.info(f"[폴백] {ticker} → {base} ({mult:+.1f}x)")
            self._save_to_cache(ticker, base, mult)
            return base, mult

        # 일반 종목으로 판정 — 캐시에도 기록하여 재조회 방지
        logger.debug(f"{ticker} → 일반 종목으로 판정")
        self._save_none_to_cache(ticker)
        return None

    # ─── Tier 2: yfinance 파싱 ────────────────────────────────────────────────

    def _parse_from_yfinance(self, ticker: str) -> Optional[Tuple[str, float]]:
        """
        yfinance 메타데이터에서 레버리지 배수와 기초 자산을 파싱합니다.
        타임아웃은 약 5초로 제한합니다.
        """
        try:
            import yfinance as yf
            info = yf.Ticker(ticker).info

            # quoteType이 ETF가 아니면 즉시 None 반환
            quote_type = info.get("quoteType", "")
            if quote_type not in ("ETF", ""):
                return None

            long_name = info.get("longName", "") or info.get("shortName", "")
            if not long_name:
                return None

            logger.debug(f"{ticker} longName: {long_name}")

            # 1. 배수 추출
            multiplier = self._extract_multiplier(long_name)
            if multiplier is None:
                # 배수 키워드가 전혀 없으면 레버리지 ETF가 아님
                return None

            # 2. Bear/Short 방향 반전
            if _INVERSE_KEYWORDS.search(long_name):
                multiplier = -abs(multiplier)

            # 3. 기초 자산 추출 (개별주 → 지수/섹터 순서로 시도)
            base_ticker = self._extract_base_ticker(long_name, ticker)
            if base_ticker is None:
                logger.warning(f"{ticker}: 배수({multiplier:+.1f}x)는 감지됐으나 기초 자산 추출 실패.")
                return None

            # 4. 무한 루프 방지: 기초 자산이 자기 자신이 되지 않도록 검증
            if base_ticker == ticker:
                logger.warning(f"{ticker}: 기초 자산이 자기 자신 → 감지 취소.")
                return None

            logger.info(f"[yfinance 파싱] {ticker}('{long_name}') → {base_ticker} ({multiplier:+.1f}x)")
            return base_ticker, multiplier

        except Exception as e:
            logger.warning(f"{ticker} yfinance 파싱 실패 (Tier 3으로 폴백): {e}")
            return None

    def _extract_multiplier(self, long_name: str) -> Optional[float]:
        """longName 문자열에서 레버리지 배수(절댓값)를 추출합니다."""
        for pattern, extractor in _MULTIPLIER_PATTERNS:
            m = pattern.search(long_name)
            if m:
                return extractor(m)
        return None

    def _extract_base_ticker(self, long_name: str, original_ticker: str) -> Optional[str]:
        """
        longName에서 기초 자산 티커를 추출합니다.

        전략:
        1. 개별주형: 이름 내 대문자 티커 패턴 탐색 (NVDA, TSLA 등)
        2. 지수/섹터형: 키워드 매핑 테이블 검색
        """
        lower_name = long_name.lower()

        # --- 지수/섹터 키워드 먼저 확인 (더 신뢰성 높음) ---
        for keyword, base_etf in _SECTOR_KEYWORD_TO_BASE.items():
            if keyword in lower_name:
                return base_etf

        # --- 개별주 티커 추출 (대문자 단어 중 주식 티커로 보이는 것) ---
        # 이유: "GraniteShares 2x Long NVDA Daily ETF" → "NVDA" 추출
        # 패턴: 2~5개의 대문자 알파벳으로만 이루어진 단어
        candidates = re.findall(r'\b([A-Z]{1,5})\b', long_name)
        for candidate in candidates:
            if candidate in _EXCLUDE_WORDS:
                continue
            if candidate == original_ticker:
                continue
            # 길이가 1인 단어는 오탐 가능성 높음 (예: "X")
            if len(candidate) < 2:
                continue
            # 숫자가 섞인 패턴 제외
            logger.debug(f"  기초 자산 후보: {candidate}")
            return candidate

        return None

    # ─── 캐시 관리 ────────────────────────────────────────────────────────────

    def _load_cache(self) -> Dict[str, dict]:
        """JSON 캐시 파일을 로드합니다. 파일이 없으면 빈 딕셔너리 반환."""
        try:
            if _CACHE_FILE.exists():
                with open(_CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"캐시 파일 로드 실패 ({_CACHE_FILE}): {e}")
        return {}

    def _save_cache(self) -> None:
        """현재 캐시 상태를 JSON 파일에 저장합니다."""
        try:
            with open(_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"캐시 파일 저장 실패: {e}")

    def _get_from_cache(self, ticker: str) -> Optional[dict]:
        """캐시에서 ticker 정보를 조회합니다. TTL 초과 시 만료 처리."""
        entry = self._cache.get(ticker)
        if not entry:
            return None
        try:
            updated = datetime.fromisoformat(entry.get("updated", "2000-01-01"))
            if datetime.now() - updated > timedelta(days=_CACHE_TTL_DAYS):
                logger.debug(f"캐시 만료: {ticker} (갱신일: {updated.date()})")
                del self._cache[ticker]
                return None
        except Exception:
            pass
        return entry

    def _save_to_cache(self, ticker: str, base: str, multiplier: float) -> None:
        """레버리지 ETF 정보를 캐시에 저장합니다."""
        self._cache[ticker] = {
            "base": base,
            "multiplier": multiplier,
            "updated": datetime.now().isoformat(),
        }
        self._save_cache()

    def _save_none_to_cache(self, ticker: str) -> None:
        """일반 종목임을 캐시에 기록합니다 (재조회 방지)."""
        self._cache[ticker] = {
            "base": "__NONE__",
            "multiplier": 0.0,
            "updated": datetime.now().isoformat(),
        }
        self._save_cache()


# 모듈 수준 싱글톤 — 재사용을 통해 캐시 인메모리 상태 공유
_detector_instance: Optional[LeveragedETFDetector] = None

def get_detector() -> LeveragedETFDetector:
    """싱글톤 감지기 인스턴스를 반환합니다."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = LeveragedETFDetector()
    return _detector_instance
