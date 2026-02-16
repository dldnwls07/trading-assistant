import pandas as pd
import numpy as np
import logging
import asyncio
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.agents.analyst import StockAnalyst
from src.data.collector import MarketDataCollector
from src.agents.multi_timeframe import MultiTimeframeAnalyzer

logger = logging.getLogger(__name__)

class StockScreener:
    """
    종합 종목 스크리너 - 투자 스타일 기반 추천
    다중 시간 프레임(Multi-Timeframe) 분석 통합
    """
    
    def __init__(self, analyst: StockAnalyst = None):
        self.analyst = analyst or StockAnalyst()
        self.collector = MarketDataCollector(use_db=False)
        self.multi_analyzer = MultiTimeframeAnalyzer(analyst=self.analyst, collector=self.collector)
    
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
        
        # 지수 데이터 미리 로드 (필요 시)
        # MultiTimeframeAnalyzer는 내부적으로 처리하지만, 속도를 위해 index_ticker만 전달
        
        # asyncio.gather를 사용하여 비동기 병렬 처리
        tasks = [self._analyze_single_stock(ticker, index_ticker, investor_style) for ticker in tickers]
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
                             index_ticker: str,
                             investor_style: str) -> Optional[Dict[str, Any]]:
        """단일 종목 다중 시간 프레임 분석 및 스타일 적합도 평가"""
        try:
            # 다중 시간 프레임 분석 실행 (Short/Mid/Long Coverage)
            mt_result = await self.multi_analyzer.analyze_all_timeframes(ticker, index_ticker)
            
            # 분석 실패 시 중단
            if not mt_result or not mt_result.get('medium_term'):
                return None
            
            # 핵심 데이터 추출 (중기 분석 결과가 기존 Daily Analysis와 유사)
            medium_term = mt_result['medium_term']
            full_analysis = medium_term.get('full_analysis', {})
            
            # 데이터 수집 (스타일 필터링용, 분석 결과에 포함된 daily_df 활용 가능하면 좋으나 여기선 full_analysis만 있음)
            # MultiTimeframeAnalyzer가 DF를 리턴하진 않으므로, price 정보는 result에서 가져옴
            current_price = medium_term.get('current_price', 0)
            
            # 투자 스타일 필터링 적용
            # full_analysis에 지표들이 다 있음
            style_score = self._apply_style_filter(ticker, full_analysis, investor_style)
            
            # 최종 점수 = 앙상블 점수(또는 컨센서스 점수) * 스타일 적합도
            base_score = mt_result['consensus'].get('avg_score', 50)
            final_score = base_score * (style_score / 100)
            
            # 등락률 계산 (Short term info or calculate from price)
            # 여기서는 편의상 medium_term의 신호 참고
            
            return {
                "ticker": ticker,
                "score": round(final_score, 1),
                "signal": mt_result['consensus'].get('consensus', '알 수 없음'),
                "reason": self._generate_reason(mt_result, investor_style),
                "current_price": current_price,
                "change_1d": 0.0 # TODO: change_1d는 별도로 구하거나 mt_result에 포함시켜야 함. 우선 0 처리.
            }
        except Exception as e:
            logger.error(f"{ticker} 분석 중 오류: {e}")
            return None

    def get_market_tickers(self, market: str = "US", limit: int = 20) -> List[str]:
        """시장별 주요 감시 종목 리스트 반환"""
        if market == "KR":
            # 한국 시장 주요 종목 (삼성전자, SK하이닉스 등)
            return ["005930.KS", "000660.KS", "035420.KS", "035720.KS", "005380.KS", 
                    "000270.KS", "068270.KS", "005490.KS", "247540.KQ", "086520.KQ"][:limit]
        else:
            # 미국 시장 주요 종목 (Magnificent 7 + 주요 성장주)
            return ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AMD", 
                    "AVGO", "NFLX", "COST", "PYPL", "INTC", "QCOM", "V", "MA"][:limit]

    def _apply_style_filter(self, ticker: str, analysis: Dict[str, Any], style: str) -> float:
        """투자 스타일에 따른 적합도 점수 계산 (0~100)"""
        score = 100
        signal = analysis.get('signal', 'HOLD')
        
        if style == "momentum":
            # 모멘텀: RSI 50 이상, 추세 강도 높음
            rsi = analysis.get('daily_analysis', {}).get('rsi_value', 50) # daily_analysis 구조 확인 필요
            # Analyst.analyze_ticker 구조상 analysis['daily_analysis']['rsi'] 임
            daily = analysis.get('daily_analysis', {})
            if isinstance(daily, dict):
                rsi = daily.get('rsi', 50)
            else: 
                rsi = 50
                
            if rsi < 50: score -= 30
            if signal == 'STRONG_BUY': score += 20
        elif style == "value":
            # 가치: 과매도권 선호 (RSI 낮은 종목)
            daily = analysis.get('daily_analysis', {})
            if isinstance(daily, dict):
                rsi = daily.get('rsi', 50)
            else: 
                rsi = 50
                
            if rsi > 60: score -= 30
            if rsi < 40: score += 20
        elif style == "aggressive_growth":
            # 공격적 성장: 변동성이 크더라도 상승세인 종목
            if signal in ['BUY', 'STRONG_BUY']: score += 10
            
        return max(50, min(150, score)) # 50~150 사이 가중치 반환

    
    def _generate_reason(self, mt_result: Dict[str, Any], style: str) -> str:
        """분석 결과를 바탕으로 사람 친화적인 추천 이유 생성 (다중 시간 프레임 반영)"""
        consensus = mt_result.get('consensus', {})
        short_term = mt_result.get('short_term', {})
        medium_term = mt_result.get('medium_term', {})
        long_term = mt_result.get('long_term', {})
        
        # 1. 3단 시간 프레임 신호 요약
        s_sig = short_term.get('signal', 'N/A') if short_term else 'N/A'
        m_sig = medium_term.get('signal', 'N/A') if medium_term else 'N/A'
        l_sig = long_term.get('signal', 'N/A') if long_term else 'N/A'
        
        # 2. 시장 국면 (Market Regime) - 중기 분석 기준
        full_analysis = medium_term.get('full_analysis', {}) if medium_term else {}
        regime = full_analysis.get('market_regime', {})
        regime_label = "횡보/알수없음"
        
        if isinstance(regime, dict):
            regime_label = regime.get('label', '알 수 없음')
        elif isinstance(regime, str):
            regime_label = regime # 혹시라도 문자열이면 그대로 사용
            
        # 3. 종합 추천 문구 생성
        total_score = consensus.get('avg_score', 0)
        
        reason = f"🔍 [AI 종합] {consensus.get('consensus', '분석 중')} ({total_score}점)\n"
        reason += f"   • 시장 국면: {regime_label}\n"
        reason += f"   • 시계열 분석: 단기({s_sig}) → 중기({m_sig}) → 장기({l_sig})\n"
        reason += f"   • {style} 전략 적합도 반영됨"
            
        return reason
    
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
