# 🏗️ 레버리지 ETF 동적 감지 시스템 구현 계획 (Leverage ETF Auto-Detection)

## 1. 개요
현재 `MLPricePredictor`에 하드코딩된 레버리지 ETF 매핑 방식을 제거하고, **동적 파싱 + 캐싱** 기반의 유틸리티 모듈로 분리합니다. 이를 통해 수백 개의 개별 종목 레버리지(NVDL, TSLL 등)와 지수형 레버리지(SOXL, TQQQ 등)를 자동 지원하며, 논리적 정합성(기초자산 기반 예측)을 확보합니다.

## 2. 핵심 아키텍처 (3-Tier Logic)

시스템은 다음 순서로 기초 자산과 레버리지 배수를 탐색합니다.

### 🟢 Tier 1: 로컬 캐시 (File-based Cache)
- **경로**: `.cache/etf_meta.json`
- **동작**: `ticker`가 캐시에 존재하면 즉시 반환 (속도 최적화, 네트워크 요청 방지).
- **구조**: `{ "SOXL": { "base": "SOXX", "multiplier": 3.0, "updated": "2026-02-19" }, ... }`

### 🟡 Tier 2: yfinance 메타데이터 파싱 (Dynamic Parsing)
- **동작**: `yfinance`로 `longName`, `description` 조회 후 정규식(Regex) 분석.
- **분석 로직**:
  1. **배수 추출**: `3X`, `2X`, `1.5X`, `Ultra`, `UltraPro(3x)`, `Bear(-1x)` 등 키워드 감지.
  2. **기초 자산(Base Asset) 추출**:
     - **개별 종목형**: 이름 내 티커 패턴(`NVDA`, `TSLA`, `COIN` 등) 추출. (예: "GraniteShares 2x Long **NVDA** Daily ETF")
     - **지수/섹터형**: 섹터 키워드 매핑 테이블 활용.
       - `Semiconductor` → **SOXX**
       - `Nasdaq-100`, `QQQ` → **QQQ**
       - `S&P 500` → **SPY**
       - `Biotech` → **XBI**
       - `Energy` → **XLE**
       - `20+ Transaction` (국채) → **TLT**

### 🔴 Tier 3: 하드코딩 폴백 (Legacy Fallback)
- **동작**: 파싱 실패 시, 기존에 정의된 약 20~30개의 주요 ETF 매핑 테이블(Hardcoded Map) 사용.
- **목적**: 네트워크 오류나 yfinance 데이터 형식 변경 시 최소한의 안전장치.

---

## 3. 구현 상세

### 3.1 신규 모듈: `src/utils/leveraged_etf_detector.py`

```python
class LeveragedETFDetector:
    def detect(self, ticker: str) -> Optional[Tuple[str, float]]:
        """
        Input: "SOXL"
        Output: ("SOXX", 3.0) 또는 None (일반 종목인 경우)
        """
        # 1. 캐시 확인
        # 2. yfinance 파싱
        # 3. 하드코딩 폴백
```

### 3.2 수정: `src/agents/ml_predictor.py`

- 기존 `LEVERAGED_ETF_MAP` 제거.
- `predict_next` 메서드 도입부에 `LeveragedETFDetector.detect(ticker)` 호출.
- 감지된 경우: 기초 자산 데이터 다운로드 → 예측 → `배수 * 0.88(Decay)` 보정 로직 수행.

---

## 4. 안전장치 및 예외 처리

1. **무한 루프 방지**:
   - 기초 자산(`base_ticker`)이 다시 레버리지 ETF로 감지되지 않도록 탐색 깊이(Depth) 제한 (최대 1회).
   - 예: `SOXL` → `SOXX` (OK) / `SOXX` → 일반 종목 판정.

2. **yfinance 타임아웃 처리**:
   - 메타데이터 조회 시 3초 타임아웃 설정. 실패 시 Tier 3(하드코딩)로 즉시 전환.

3. **잘못된 매핑 방지**:
   - 추출된 기초 자산 티커가 유효한지 검증(간단한 문자열 형식 검사).

## 5. 작업 순서

1. `src/utils/leveraged_etf_detector.py` 생성 및 로직 구현.
2. 단위 테스트 스크립트(`check_detector.py`)로 주요 종목(SOXL, NVDL, TSLL, SPY) 감지 테스트.
3. `src/agents/ml_predictor.py` 리팩토링 및 연동.
4. 통합 테스트: `integration_service`를 통해 실제 예측 값 논리 확인.
