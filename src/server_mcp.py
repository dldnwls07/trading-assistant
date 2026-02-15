import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# mcp 라이브러리 (설치 필요: pip install mcp)
from mcp.server.fastmcp import FastMCP

# 기존 프로젝트 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agents.analyst import StockAnalyst
from src.data.collector import MarketDataCollector
from src.agents.ai_analyzer import AIAnalyzer
from src.agents.portfolio_analyzer import PortfolioAnalyzer
from src.agents.screener import StockScreener
from src.agents.event_calendar import EventCalendar
from src.data.storage import get_storage

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trading-mcp")

# MCP 서버 초기화 (이름: trading-assistant)
mcp = FastMCP("trading-assistant")

# 인스턴스 (싱글톤)
collector = MarketDataCollector()
analyst = StockAnalyst()
ai_analyzer = AIAnalyzer()
portfolio = PortfolioAnalyzer()
screener = StockScreener()
calendar = EventCalendar()
storage = get_storage()

# ---------------------------------------------------------
# 🛠️ Tools (AI가 호출할 수 있는 함수들)
# ---------------------------------------------------------

@mcp.tool()
def get_stock_analysis(ticker: str) -> str:
    """
    주식 종목에 대한 종합적인 분석 데이터(기술적 지표, AI 의견)를 제공합니다.
    Args:
        ticker: 종목 코드 (예: AAPL, TSLA, 005930.KS)
    """
    try:
        # 데이터 수집
        df = collector.get_ohlcv(ticker, period="1y", interval="1d")
        if df is None or df.empty:
            return f"Error: Data not found for {ticker}"
            
        financials = collector.get_financials(ticker)
        
        # 분석 실행
        result = analyst.analyze_ticker(ticker, df, financials)
        
        # 결과 요약
        summary = {
            "ticker": result['ticker'],
            "price": result['current_price'],
            "signal": result['signal'],  # STRONG_BUY, BUY, HOLD, SELL
            "score": result['final_score'],
            "rsi": result['technical_analysis']['rsi'],
            "trend": result['technical_analysis']['trend'],
            "support": result['technical_analysis']['support'],
            "resistance": result['technical_analysis']['resistance']
        }
        return json.dumps(summary, indent=2)
    except Exception as e:
        return f"Analysis failed: {str(e)}"

@mcp.tool()
def get_financial_summary(ticker: str) -> str:
    """
    기업의 재무제표 요약 정보를 조회합니다. (PER, PBR, ROE 등)
    Args:
        ticker: 종목 코드
    """
    try:
        financials = collector.get_financials(ticker)
        if not financials:
            return "No financial data available."
            
        # 필요한 정보만 추출
        summary = {
            "market_cap": financials.get('marketCap'),
            "pe_ratio": financials.get('trailingPE'),
            "forward_pe": financials.get('forwardPE'),
            "peg_ratio": financials.get('pegRatio'),
            "roe": financials.get('returnOnEquity'),
            "revenue_growth": financials.get('revenueGrowth')
        }
        return json.dumps(summary, indent=2)
    except Exception as e:
        return f"Financial lookup failed: {str(e)}"

@mcp.tool()
def check_portfolio_risk(holdings: str) -> str:
    """
    포트폴리오의 리스크와 기대 수익률을 분석합니다.
    Args:
        holdings: JSON 문자열 (예: '[{"ticker":"AAPL", "shares":10, "avg_price":150}]')
    """
    try:
        data = json.loads(holdings)
        result = portfolio.analyze_portfolio(data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Portfolio analysis failed: {str(e)}"

@mcp.tool()
def recommend_stocks(style: str = "balanced") -> str:
    """
    투자 성향에 맞는 유망 종목을 추천합니다.
    Args:
        style: 투자 스타일 ('aggressive', 'balanced', 'conservative')
    """
    try:
        recs = screener.get_recommendations(style=style, limit=5)
        return json.dumps(recs, indent=2)
    except Exception as e:
        return f"Recommendation failed: {str(e)}"

@mcp.tool()
async def set_price_alert(ticker: str, target_price: float, condition: str = "above", note: str = "") -> str:
    """ 주식 가격 알림을 설정합니다. """
    try:
        await storage.initialize() # 초기화 확인
        alert_id = await storage.save_alert(
            ticker=ticker.upper(), alert_type=f"price_{condition}",
            target_value=target_price, note=note
        )
        return f"Alert set successfully (ID: {alert_id})"
    except Exception as e:
        return f"Failed to set alert: {str(e)}"

@mcp.tool()
async def check_triggered_alerts() -> str:
    """ 내 가격 도달 알림 확인 """
    try:
        await storage.initialize()
        active_alerts = await storage.get_active_alerts()
        if not active_alerts: return "No active alerts."
            
        triggered = []
        for alert in active_alerts:
            if alert.alert_type.startswith("price_"):
                df = collector.get_ohlcv(alert.ticker, period="1d", interval="1m")
                if df is not None and not df.empty:
                    current_price = df['Close'].iloc[-1]
                    is_above = "above" in alert.alert_type
                    if (is_above and current_price >= alert.target_value) or \
                       (not is_above and current_price <= alert.target_value):
                        triggered.append({
                            "ticker": alert.ticker, "target": alert.target_value,
                            "current": current_price, "note": alert.note
                        })
                        await storage.trigger_alert(alert.id)
        return json.dumps(triggered, indent=2) if triggered else "No alerts triggered."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_today_high_impact_events() -> str:
    """
    오늘 예정된 중요 경제 지표 및 이벤트를 조회합니다.
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        cal_data = calendar.get_calendar(start_date=today, end_date=today)
        high_impact = [e for e in cal_data['events'] if e['importance'] in ['critical', 'high']]
        
        if not high_impact:
            return "No high impact events today."
            
        return json.dumps(high_impact, indent=2)
    except Exception as e:
        return f"Failed to get events: {str(e)}"

@mcp.tool()
def get_market_risk_summary() -> str:
    """
    향후 7일간의 시장 리스크 지수와 주요 이벤트를 요약합니다.
    """
    try:
        risk = calendar.calculate_event_risk(days_ahead=7)
        return json.dumps(risk, indent=2)
    except Exception as e:
        return f"Failed to get risk summary: {str(e)}"

# ---------------------------------------------------------
# 🚀 서버 실행
# ---------------------------------------------------------
if __name__ == "__main__":
    # stdio 모드로 실행 (Claude Desktop, Antigravity 등과 연결)
    mcp.run()
