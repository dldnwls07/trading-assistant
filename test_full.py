"""
전체 기능 통합 테스트
- AI 분석 (Hugging Face)
- 이벤트 정보 수집
- 차트 생성
"""
import sys
import os
import io

# UTF-8 출력
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.append(os.path.join(os.getcwd(), 'src'))

from dotenv import load_dotenv
load_dotenv()

from data.collector import MarketDataCollector
from data.storage import DataStorage
from data.parser import FinancialParser
from agents.analyst import StockAnalyst
from agents.ai_analyzer import AIAnalyzer, get_stock_events
from ui.chart_generator import ChartGenerator

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_full_analysis(ticker: str):
    print(f"\n{'='*60}")
    print(f"[FULL TEST] {ticker}")
    print('='*60)
    
    # 1. 데이터 수집
    print("\n[1] 데이터 수집 중...")
    collector = MarketDataCollector(use_db=True)
    storage = DataStorage("trading_assistant.db")
    parser = FinancialParser(use_db=True)
    
    price_df = collector.get_ohlcv(ticker, period="1y", interval="1d")
    if price_df is None:
        print(f"ERROR: {ticker} 시세 데이터 수집 실패")
        return
    print(f"  - 시세 데이터: {len(price_df)} 건")
    
    financials = storage.get_financials(ticker)
    if not financials:
        parser.fetch_and_save_financials(ticker)
        financials = storage.get_financials(ticker)
    print(f"  - 재무 데이터: {len(financials) if financials else 0} 건")
    
    # 2. 이벤트 정보 수집
    print("\n[2] 이벤트 정보 수집 중...")
    events = get_stock_events(ticker)
    print(f"  - 실적발표일: {events.get('earnings_date', '미정')}")
    print(f"  - 배당락일: {events.get('ex_dividend_date', '미정')}")
    print(f"  - 섹터: {events.get('sector', 'N/A')}")
    
    # 3. 기술/기본 분석
    print("\n[3] 분석 수행 중...")
    analyst = StockAnalyst()
    result = analyst.analyze_ticker(ticker, price_df, financials)
    result['events'] = events
    
    print(f"  - 신호: {result['signal']}")
    print(f"  - 점수: {result['final_score']}/100")
    
    entry = result.get('entry_points', {})
    if entry:
        print(f"  - 현재가: {entry.get('current_price', 0):,.0f}")
        print(f"  - 1차 매수: {entry.get('buy_target_1', 0):,.0f}")
        print(f"  - 손절가: {entry.get('stop_loss', 0):,.0f}")
        print(f"  - 목표가: {entry.get('sell_target_1', 0):,.0f}")
    
    # 4. AI 리포트 생성
    print("\n[4] AI 리포트 생성 중...")
    ai = AIAnalyzer()
    report = ai.generate_report(result)
    print("\n" + "-"*50)
    print(report)
    print("-"*50)
    
    # 5. 차트 생성
    print("\n[5] 차트 생성 중...")
    chart_gen = ChartGenerator(output_dir="charts")
    chart_path = chart_gen.generate_analysis_chart(ticker, price_df, result)
    if chart_path:
        print(f"  - 차트 저장: {chart_path}")
    else:
        print("  - 차트 생성 실패")
    
    print("\n" + "="*60)
    print("[COMPLETE] 전체 분석 완료!")
    print("="*60)

if __name__ == "__main__":
    # 미국 주식 테스트
    test_full_analysis("AAPL")
    
    # 한국 주식 테스트
    # test_full_analysis("005930.KS")
