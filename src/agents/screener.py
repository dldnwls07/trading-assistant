"""
AI 추천 종목 스크리너 - 인베스팅닷컴 스타일
다중 관점(기술적/거시적/심리적/수급) 종합 분석을 통한 유망 종목 발굴
"""
import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.agents.analyst import StockAnalyst
from src.data.collector import MarketDataCollector

logger = logging.getLogger(__name__)

class StockScreener:
    """
    종합 종목 스크리너 - 투자 스타일 기반 추천
    """
    
    def __init__(self, analyst: StockAnalyst = None):
        self.analyst = analyst or StockAnalyst()
        self.collector = MarketDataCollector(use_db=False)
    
    async def _fetch_data(self, ticker: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """MarketDataCollector를 통한 통합 데이터 수집 (비동기)"""
        return await self.collector.get_ohlcv(ticker, period=period, interval=interval)
        
    async def screen_stocks(self, 
                      tickers: List[str], 
                      investor_style: str = "balanced",
                      top_n: int = 10,
                      index_ticker: str = "^GSPC") -> List[Dict[str, Any]]:
        """
        종목 풀에서 투자 스타일에 맞는 상위 N개 종목 추천 (비동기 병렬 처리)
        """
        logger.info(f"스크리닝 시작: {len(tickers)}개 종목, 스타일={investor_style}")
        
        # 지수 데이터 미리 로드
        index_df = await self._fetch_data(index_ticker, period="1y")
        
        # asyncio.gather를 사용하여 비동기 병렬 처리
        tasks = [self._analyze_single_stock(ticker, index_df, investor_style) for ticker in tickers]
        results_raw = await asyncio.gather(*tasks)
        
        # None 제외 및 결과 정리
        results = [r for r in results_raw if r]
        
        # 점수 기준 정렬 및 상위 N개 선택
        results.sort(key=lambda x: x['score'], reverse=True)
        top_picks = results[:top_n]
        
        logger.info(f"스크리닝 완료: 상위 {len(top_picks)}개 종목 선정")
        return top_picks
    
    async def _analyze_single_stock(self, 
                             ticker: str, 
                             index_df: pd.DataFrame,
                             investor_style: str) -> Optional[Dict[str, Any]]:
        """단일 종목 분석 및 스타일 적합도 평가 (비동기)"""
        try:
            # 데이터 수집 (await 적용)
            daily_df = await self._fetch_data(ticker, period="1y")
            if daily_df is None or len(daily_df) < 50:
                return None
            
            # 종합 분석 수행 (동기 함수인 경우 그대로 호출하거나 asyncio.to_thread 고려)
            # 여기서는 CPU 연산이 많으므로 복잡할 경우 to_thread가 나을 수 있으나 우선 직접 호출
            analysis = self.analyst.analyze_ticker(
                ticker=ticker,
                daily_df=daily_df,
                index_df=index_df,
                financials=None,
                hourly_df=None,
                sentiment_data=None
            )
            
            # 투자 스타일 필터링 적용
            style_score = self._apply_style_filter(ticker, daily_df, analysis, investor_style)
            
            # 최종 점수 = 기본 점수 * 스타일 적합도
            final_score = analysis['final_score'] * (style_score / 100)
            
            return {
                "ticker": ticker,
                "score": round(final_score, 1),
                "signal": analysis['signal'],
                "reason": self._generate_reason(analysis, investor_style),
                "current_price": daily_df['Close'].iloc[-1],
                "change_1d": ((daily_df['Close'].iloc[-1] - daily_df['Close'].iloc[-2]) / daily_df['Close'].iloc[-2] * 100) if len(daily_df) >= 2 else 0
            }
        except Exception as e:
            logger.error(f"{ticker} 분석 중 오류: {e}")
            return None

    # ... (생략된 중간 메서드들: _apply_style_filter, _generate_reason, get_market_tickers 동일) ...
    
    async def get_recommendations(self, style: str = "balanced", market: str = "US", limit: int = 10) -> Dict[str, Any]:
        """AI 추천 종목 조회 (비동기)"""
        tickers = self.get_market_tickers(market, limit=30) # 병목 방지를 위해 limit 조정
        recommendations = await self.screen_stocks(tickers, investor_style=style, top_n=limit)
        
        return {
            "style": style,
            "market": market,
            "recommendations": recommendations,
            "timestamp": pd.Timestamp.now().isoformat()
        }
    
    async def get_top_movers(self, market: str = "US") -> Dict[str, Any]:
        """급등/급락 종목 조회 (비동기)"""
        tickers = self.get_market_tickers(market, limit=30)
        
        # asyncio.gather 활용
        tasks = [self._get_stock_change(ticker) for ticker in tickers]
        results = await asyncio.gather(*tasks)
        
        gainers = []
        losers = []
        for res in results:
            if res:
                if res['change'] > 0:
                    gainers.append(res)
                else:
                    losers.append(res)
        
        # 정렬
        gainers.sort(key=lambda x: x['change'], reverse=True)
        losers.sort(key=lambda x: x['change'])
        
        return {
            "market": market,
            "gainers": gainers[:5],
            "losers": losers[:5]
        }

    async def _get_stock_change(self, ticker: str) -> Optional[Dict[str, Any]]:
        """단일 종목의 당일 변동률 조회 (비동기)"""
        try:
            hist = await self.collector.get_ohlcv(ticker, period="5d", interval="1d")
            if hist is None or len(hist) < 2: return None
            
            prev_close = hist['Close'].iloc[-2]
            current_close = hist['Close'].iloc[-1]
            change_pct = ((current_close - prev_close) / prev_close) * 100
            
            return {
                "ticker": ticker,
                "price": round(float(current_close), 2),
                "change": round(float(change_pct), 2)
            }
        except Exception as e:
            logger.debug(f"Change fetch error for {ticker}: {e}")
            return None
        except Exception as e:
            logger.debug(f"Change fetch error for {ticker}: {e}")
            return None

# 사용 예시
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    screener = StockScreener()
    
    # 공격적 성장형 투자자를 위한 추천
    recommendations = screener.get_recommendations(style="aggressive_growth", market="US")
    
    print("\n=== AI 추천 종목 (공격적 성장형) ===")
    for i, rec in enumerate(recommendations['recommendations'], 1):
        print(f"{i}. {rec['ticker']} - 점수: {rec['score']}")
        print(f"   {rec['reason']}")
    
    movers = screener.get_top_movers(market="US")
    print("\n=== 시장 급등 종목 ===")
    for m in movers['gainers']:
        print(f"{m['ticker']}: {m['change']}%")
