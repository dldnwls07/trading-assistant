"""
레버리지 ETF 감지기(LeveragedETFDetector) 단위 테스트 스크립트.
구현 후 이 스크립트로 핵심 케이스를 검증합니다.

실행: python check_detector.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.utils.leveraged_etf_detector import LeveragedETFDetector

detector = LeveragedETFDetector()

# 테스트 케이스: (티커, 예상 기초자산, 예상 배수방향)
# 배수방향: "pos" = 양수, "neg" = 음수, None = 일반 종목(None 반환)
TEST_CASES = [
    # ── 지수형 레버리지 ───────────────────────
    ("SOXL",  "SOXX", "pos"),   # 반도체 3x Bull
    ("SOXS",  "SOXX", "neg"),   # 반도체 3x Bear
    ("TQQQ",  "QQQ",  "pos"),   # 나스닥 3x
    ("SQQQ",  "QQQ",  "neg"),   # 나스닥 -3x
    ("SPXL",  "SPY",  "pos"),   # S&P 500 3x
    ("SPXS",  "SPY",  "neg"),   # S&P 500 -3x
    ("TMF",   "TLT",  "pos"),   # 국채 3x
    ("LABU",  "XBI",  "pos"),   # 바이오 3x
    # ── 개별주 레버리지 ───────────────────────
    ("NVDL",  "NVDA", "pos"),   # NVDA 2x
    ("TSLL",  "TSLA", "pos"),   # TSLA 2x
    ("TSLS",  "TSLA", "neg"),   # TSLA -1x
    # ── 일반 종목 (None 반환 기대) ────────────
    ("AAPL",  None,   None),
    ("SPY",   None,   None),
    ("SOXX",  None,   None),
    ("NVDA",  None,   None),
]

print("=" * 60)
print("🔍 LeveragedETFDetector 단위 테스트")
print("=" * 60)

passed = 0
failed = 0

for ticker, expected_base, expected_dir in TEST_CASES:
    result = detector.detect(ticker)

    if expected_base is None:
        # 일반 종목 — None 반환 기대
        ok = (result is None)
        status = "✅ PASS" if ok else f"❌ FAIL (예상: None, 실제: {result})"
    else:
        if result is None:
            ok = False
            status = f"❌ FAIL (예상: ({expected_base}, {expected_dir}), 실제: None)"
        else:
            base, mult = result
            dir_ok = (mult > 0) if expected_dir == "pos" else (mult < 0)
            base_ok = (base == expected_base)
            ok = base_ok and dir_ok
            status = "✅ PASS" if ok else f"❌ FAIL (예상: {expected_base}/{expected_dir}, 실제: {base}/{mult:+.1f}x)"

    print(f"  {ticker:8s} → {status}")
    if ok:
        passed += 1
    else:
        failed += 1

print("=" * 60)
print(f"결과: {passed} PASS / {failed} FAIL / {len(TEST_CASES)} 총")
print("=" * 60)

if failed > 0:
    sys.exit(1)
