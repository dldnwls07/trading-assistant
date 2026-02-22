import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self, collector_client, chart_master_client, integration_service_client):
        self.collector = collector_client
        self.chart_master = chart_master_client
        self.integration_service = integration_service_client

    async def get_technical_analysis(self, final_ticker: str) -> Dict[str, Any]:
        """단일 종목 기술적/차트 분석 수행"""
        df = await self.collector.get_ohlcv(final_ticker, period="1y", interval="1d")
        if df is None or df.empty:
            return None
            
        return self.chart_master.analyze_chart(final_ticker, df)

    async def get_multi_timeframe_analysis(self, final_ticker: str) -> Dict[str, Any]:
        """멀티 타임프레임 분석 및 통합 정보 생성"""
        timeframes = {
            "1h": await self.collector.get_ohlcv(final_ticker, period="60d", interval="60m"),
            "4h": await self.collector.get_ohlcv(final_ticker, period="120d", interval="1h"),
            "1d": await self.collector.get_ohlcv(final_ticker, period="1y", interval="1d"),
            "1wk": await self.collector.get_ohlcv(final_ticker, period="5y", interval="1wk"),
        }
        
        analyses = {}
        for interval, df in timeframes.items():
            if df is not None and not df.empty:
                from src.agents.core.analyst import TechnicalAnalyzer
                ta = TechnicalAnalyzer()
                
                analysis = {
                    "interval": interval,
                    "current_price": float(df['Close'].iloc[-1]),
                    "trend": "상승" if df['Close'].iloc[-1] > df['Close'].iloc[-20] else "하락",
                    "rsi": float(ta.calculate_rsi(df).iloc[-1]) if len(df) > 14 else None,
                }
                analyses[interval] = analysis
        
        return {
            "ticker": final_ticker,
            "timeframes": analyses,
            "timestamp": datetime.now().isoformat()
        }

    async def run_comprehensive_analysis(self, ticker: str, final_ticker: str) -> Dict[str, Any]:
        """에이전트 연합 전체 종합 분석 실행 및 yfinance 메타데이터 병합"""
        raw_result = await self.integration_service.run_comprehensive_analysis(final_ticker)
        
        if raw_result.get("status") == "error":
            return raw_result
        
        try:
            import yfinance as yf
            stock = yf.Ticker(final_ticker)
            info = stock.info
            name = info.get('longName') or info.get('shortName') or final_ticker
            raw_result["display_name"] = f"{name} ({final_ticker})"
        except:
            raw_result["display_name"] = final_ticker

        return raw_result
