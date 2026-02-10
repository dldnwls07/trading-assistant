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
                financials=None,  # TODO: 재무제표 연동 시 추가
                hourly_df=None,
                sentiment_data=None  # TODO: 뉴스 감성 분석 연동 시 추가
            )
            
            # 투자 스타일 필터링 적용
            style_score = self._apply_style_filter(ticker, daily_df, analysis, investor_style)
            
            # 최종 점수 = 기본 점수 * 스타일 적합도
            final_score = analysis['final_score'] * (style_score / 100)
            
            return {
                "ticker": ticker,
                "score": round(final_score, 1),
                "base_score": analysis['final_score'],
                "style_fit": style_score,
                "signal": analysis['signal'],
                "current_price": daily_df['Close'].iloc[-1],
                "reason": self._generate_recommendation_reason(ticker, analysis, investor_style),
                "entry_points": analysis.get('entry_points', {}),
                "analysis": analysis  # 전체 분석 결과 포함
            }
            
        except Exception as e:
            logger.error(f"{ticker} 분석 중 오류: {e}")
            return None
    
    def _apply_style_filter(self, 
                           ticker: str,
                           daily_df: pd.DataFrame, 
                           analysis: Dict[str, Any],
                           style: str) -> int:
        """
        투자 스타일에 따른 적합도 점수 (0~100)
        """
        score = 50  # 기본 점수
        
        daily = analysis.get('daily_analysis', {})
        fund = analysis.get('fundamental', {})
        macro = analysis.get('macro', {})
        vol = analysis.get('volume_price', {})
        
        rsi = daily.get('rsi', 50)
        current_price = daily.get('last_close', 0)
        
        if style == "aggressive_growth":
            # 공격적 성장형: 고성장, 고변동성, 모멘텀 중시
            if rsi < 40:  # 과매도 구간 선호
                score += 20
            if vol.get('score', 50) > 60:  # 거래량 증가
                score += 15
            # TODO: 매출 성장률 > 20% 조건 추가 (재무제표 연동 후)
            
        elif style == "dividend":
            # 안정적 배당형: 저변동성, 배당 수익률 중시
            if rsi > 40 and rsi < 60:  # 안정적 구간
                score += 15
            if macro.get('score', 50) > 50:  # 거시 환경 양호
                score += 10
            # TODO: 배당 수익률 > 3% 조건 추가
            
        elif style == "value":
            # 가치 투자형: 저평가, 펀더멘털 중시
            if fund.get('score', 50) > 60:  # 재무 건전성 우수
                score += 20
            if current_price < daily_df['Close'].rolling(200).mean().iloc[-1]:  # 200일선 하회
                score += 15
            # TODO: PER, PBR 조건 추가
            
        elif style == "momentum":
            # 모멘텀 트레이딩형: 기술적 신호 중시
            macd = daily.get('macd', {})
            if macd.get('MACD', 0) > macd.get('Signal', 0):  # MACD 골든크로스
                score += 20
            if vol.get('score', 50) > 65:  # 강한 거래량
                score += 15
            
        elif style == "balanced":
            # 균형형: 모든 지표 골고루 반영
            if 40 <= analysis['final_score'] <= 70:
                score += 20
            if macro.get('score', 50) > 45:
                score += 10
        
        return max(0, min(100, score))
    
    def _generate_recommendation_reason(self, 
                                       ticker: str,
                                       analysis: Dict[str, Any],
                                       style: str) -> str:
        """추천 근거 생성 (한국어)"""
        reasons = []
        
        # 종합 신호
        signal = analysis.get('signal', '중립')
        reasons.append(f"종합 신호: {signal}")
        
        # 스타일별 맞춤 근거
        style_names = {
            "aggressive_growth": "공격적 성장형",
            "dividend": "안정적 배당형",
            "value": "가치 투자형",
            "momentum": "모멘텀 트레이딩형",
            "balanced": "균형 포트폴리오형"
        }
        
        reasons.append(f"'{style_names.get(style, style)}' 투자 스타일에 적합")
        
        # 주요 강점 추출
        daily = analysis.get('daily_analysis', {})
        if daily:
            summary = daily.get('summary', '')
            if summary:
                reasons.append(f"기술적: {summary[:50]}...")
        
        macro = analysis.get('macro', {})
        if macro and macro.get('details'):
            reasons.append(f"거시적: {macro['details'][0][:50]}...")
        
        return " | ".join(reasons)
    
    def _fetch_data(self, ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """yfinance를 통한 데이터 수집"""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            if df.empty:
                return None
            return df
        except Exception as e:
            logger.warning(f"{ticker} 데이터 수집 실패: {e}")
            return None
    
    def get_sp500_tickers(self) -> List[str]:
        """S&P 500 종목 리스트 가져오기"""
        try:
            # Wikipedia에서 S&P 500 종목 리스트 크롤링
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(url)
            df = tables[0]
            return df['Symbol'].tolist()
        except Exception as e:
            logger.error(f"S&P 500 종목 리스트 가져오기 실패: {e}")
            # 대체: 주요 종목 샘플
            return ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "V", "JNJ"]


# 사용 예시
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    screener = StockScreener()
    
    # 샘플 종목 풀 (실제로는 S&P 500 전체)
    sample_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "JPM", "V", "WMT"]
    
    # 공격적 성장형 투자자를 위한 추천
    recommendations = screener.screen_stocks(
        tickers=sample_tickers,
        investor_style="aggressive_growth",
        top_n=5
    )
    
    print("\n=== AI 추천 종목 (공격적 성장형) ===")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['ticker']} - 점수: {rec['score']}")
        print(f"   {rec['reason']}")
        print()
