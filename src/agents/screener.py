"""
AI 추천 종목 스크리너 - 인베스팅닷컴 스타일
다중 관점(기술적/거시적/심리적/수급) 종합 분석을 통한 유망 종목 발굴
"""
import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import yfinance as yf

from src.agents.analyst import StockAnalyst

logger = logging.getLogger(__name__)

class StockScreener:
    """
    종합 종목 스크리너 - 투자 스타일 기반 추천
    """
    
    def __init__(self, analyst: StockAnalyst = None):
        self.analyst = analyst or StockAnalyst()
    
    def _fetch_data(self, ticker: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """yfinance를 통한 주가 데이터 수집"""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)
            return df if not df.empty else None
        except Exception as e:
            logger.warning(f"{ticker} 데이터 수집 실패: {e}")
            return None
        
    def screen_stocks(self, 
                     tickers: List[str], 
                     investor_style: str = "balanced",
                     top_n: int = 10,
                     index_ticker: str = "^GSPC") -> List[Dict[str, Any]]:
        """
        종목 풀에서 투자 스타일에 맞는 상위 N개 종목 추천
        
        Args:
            tickers: 스크리닝할 종목 리스트 (예: S&P 500)
            investor_style: 투자 스타일 ("aggressive_growth", "dividend", "value", "momentum", "balanced")
            top_n: 추천할 종목 개수
            index_ticker: 비교 지수 (기본값: S&P 500)
            
        Returns:
            추천 종목 리스트 (점수 높은 순)
        """
        logger.info(f"스크리닝 시작: {len(tickers)}개 종목, 스타일={investor_style}")
        
        # 지수 데이터 미리 로드
        index_df = self._fetch_data(index_ticker, period="1y")
        
        # 병렬 처리로 각 종목 분석
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self._analyze_single_stock, ticker, index_df, investor_style): ticker 
                for ticker in tickers
            }
            
            for future in as_completed(futures):
                ticker = futures[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        logger.info(f"✓ {ticker}: 점수 {result['score']}")
                except Exception as e:
                    logger.warning(f"✗ {ticker} 분석 실패: {e}")
        
        # 점수 기준 정렬 및 상위 N개 선택
        results.sort(key=lambda x: x['score'], reverse=True)
        top_picks = results[:top_n]
        
        logger.info(f"스크리닝 완료: 상위 {len(top_picks)}개 종목 선정")
        return top_picks
    
    def _analyze_single_stock(self, 
                             ticker: str, 
                             index_df: pd.DataFrame,
                             investor_style: str) -> Optional[Dict[str, Any]]:
        """단일 종목 분석 및 스타일 적합도 평가"""
        try:
            # 데이터 수집
            daily_df = self._fetch_data(ticker, period="1y")
            if daily_df is None or len(daily_df) < 50:
                return None
            
            # 종합 분석 수행
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
    
    def _apply_style_filter(self, ticker: str, df: pd.DataFrame, analysis: Dict, style: str) -> float:
        """투자 스타일별 가중치 적용 (분석 결과 구조에 맞춰 수정)"""
        if style == "aggressive_growth":
            # 공격적 성장: 기술적 지표 + 수급/에너지
            tech = analysis.get('daily_analysis', {}).get('score', 50)
            vol = analysis.get('volume_price', {}).get('score', 50)
            return (tech * 0.6 + vol * 0.4)
        
        elif style == "dividend":
            # 배당: 펀더멘털 + 심리 안정성
            fund = analysis.get('fundamental', {}).get('score', 50)
            psych = analysis.get('psychology', {}).get('score', 50)
            return (fund * 0.7 + psych * 0.3)
        
        elif style == "value":
            # 가치투자: 펀더멘털 최우선
            fund = analysis.get('fundamental', {}).get('score', 50)
            macro = analysis.get('macro', {}).get('score', 50)
            return (fund * 0.8 + macro * 0.2)
        
        elif style == "momentum":
            # 모멘텀: 기술적 지세 + 수급
            tech = analysis.get('daily_analysis', {}).get('score', 50)
            vol = analysis.get('volume_price', {}).get('score', 50)
            return (tech * 0.7 + vol * 0.3)
        
        else:  # balanced
            return 100
    
    def _generate_reason(self, analysis: Dict, style: str) -> str:
        """스타일별 특화된 추천 이유 생성"""
        tech_score = analysis.get('daily_analysis', {}).get('score', 50)
        fund_score = analysis.get('fundamental', {}).get('score', 50)
        vol_score = analysis.get('volume_price', {}).get('score', 50)
        psych_score = analysis.get('psychology', {}).get('score', 50)
        
        if style == "aggressive_growth":
            return f"강한 모멘텀({tech_score}점)과 에너지 유입({vol_score}점) 포착"
        elif style == "dividend":
            return f"안정적 펀더멘털({fund_score}점) 및 심리 저점 형성"
        elif style == "value":
            return f"저평가 매력({fund_score}점) 및 안전 마진 확보"
        elif style == "momentum":
            return f"추세 추종 적합. 기술적 완성도 {tech_score}점 달성"
        else:
            return f"종합 점수 {analysis.get('final_score', 0)}점으로 균형 잡힌 성장세"

    def get_market_tickers(self, market: str = "US", limit: int = 50) -> List[str]:
        """시장별 주요 종목 리스트 반환"""
        if market == "US":
            return [
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "JPM", "V",
                "JNJ", "WMT", "PG", "MA", "HD", "DIS", "PYPL", "NFLX", "ADBE", "CRM",
                "INTC", "CSCO", "PFE", "KO", "PEP", "ABT", "MRK", "TMO", "ABBV", "COST",
                "AVGO", "ACN", "NKE", "TXN", "LIN", "DHR", "UNP", "NEE", "ORCL", "PM",
                "HON", "UPS", "RTX", "QCOM", "BMY", "LMT", "LOW", "AMD", "BA", "IBM"
            ][:limit]
        elif market == "KR":
            return [
                "005930.KS", "000660.KS", "035420.KS", "035720.KS", "051910.KS",
                "006400.KS", "005380.KS", "068270.KS", "207940.KS", "005490.KS",
                "000270.KS", "105560.KS", "055550.KS", "096770.KS", "012330.KS",
                "028260.KS", "066570.KS", "003550.KS", "017670.KS", "034730.KS",
                "009150.KS", "032830.KS", "018260.KS", "003670.KS", "015760.KS",
                "086520.KQ", "247540.KQ", "373220.KS", "000100.KS", "011170.KS",
                "000810.KS", "033780.KS", "010950.KS", "086790.KS", "005935.KS",
                "036570.KS", "066970.KS", "034220.KS", "010130.KS", "001500.KS",
                "004020.KS", "030200.KS", "267250.KS", "011070.KS", "090430.KS"
            ][:limit]
        else:
            return []
    
    def get_recommendations(self, style: str = "balanced", market: str = "US", limit: int = 10) -> Dict[str, Any]:
        """AI 추천 종목 조회"""
        tickers = self.get_market_tickers(market, limit=50)
        recommendations = self.screen_stocks(tickers, investor_style=style, top_n=limit)
        
        return {
            "style": style,
            "market": market,
            "recommendations": recommendations,
            "timestamp": pd.Timestamp.now().isoformat()
        }
    
    def get_top_movers(self, market: str = "US") -> Dict[str, Any]:
        """급등/급락 종목 조회"""
        tickers = self.get_market_tickers(market, limit=30)
        
        gainers = []
        losers = []
        
        # 병렬로 가격 변동 확인
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self._get_stock_change, ticker): ticker for ticker in tickers}
            for future in as_completed(futures):
                res = future.result()
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

    def _get_stock_change(self, ticker: str) -> Optional[Dict[str, Any]]:
        """단일 종목의 당일 변동률 조회"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            if len(hist) < 2: return None
            
            prev_close = hist['Close'].iloc[-2]
            current_close = hist['Close'].iloc[-1]
            change_pct = ((current_close - prev_close) / prev_close) * 100
            
            return {
                "ticker": ticker,
                "price": round(current_close, 2),
                "change": round(change_pct, 2)
            }
        except:
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
