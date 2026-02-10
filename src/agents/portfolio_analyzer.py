"""
포트폴리오 AI 평가 및 리밸런싱 제안 시스템
사용자의 보유 포트폴리오를 종합 분석하고 최적화 방안 제시
"""
import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any, Optional
from collections import Counter

from src.agents.analyst import StockAnalyst
from src.agents.profiler import InvestorProfiler
from src.agents.screener import StockScreener

logger = logging.getLogger(__name__)

class PortfolioAnalyzer:
    """
    포트폴리오 종합 평가 및 리밸런싱 제안
    """
    
    def __init__(self):
        self.analyst = StockAnalyst()
        self.profiler = InvestorProfiler()
        self.screener = StockScreener(self.analyst)
    
    def analyze_portfolio(self, 
                         holdings: List[Dict[str, Any]],
                         index_ticker: str = "^GSPC") -> Dict[str, Any]:
        """
        포트폴리오 종합 분석
        
        Args:
            holdings: 보유 종목 리스트
                예: [{"ticker": "AAPL", "shares": 10, "avg_price": 150}, ...]
            index_ticker: 비교 지수
            
        Returns:
            종합 평가 결과
        """
        logger.info(f"포트폴리오 분석 시작: {len(holdings)}개 종목")
        
        # 1. 각 종목 개별 분석
        stock_analyses = []
        total_value = 0
        
        for holding in holdings:
            ticker = holding['ticker']
            shares = holding.get('shares', 0)
            avg_price = holding.get('avg_price', 0)
            
            # 현재 가격 및 분석
            analysis = self._analyze_holding(ticker, index_ticker)
            if analysis:
                current_price = analysis['current_price']
                position_value = shares * current_price
                total_value += position_value
                
                stock_analyses.append({
                    "ticker": ticker,
                    "shares": shares,
                    "avg_price": avg_price,
                    "current_price": current_price,
                    "position_value": position_value,
                    "profit_loss": (current_price - avg_price) * shares,
                    "profit_loss_pct": ((current_price - avg_price) / avg_price * 100) if avg_price > 0 else 0,
                    "ai_score": analysis['final_score'],
                    "signal": analysis['signal'],
                    "sector": analysis.get('sector', 'Unknown'),
                    "analysis": analysis
                })
        
        # 2. 비중 계산
        for stock in stock_analyses:
            stock['weight'] = (stock['position_value'] / total_value * 100) if total_value > 0 else 0
        
        # 3. 포트폴리오 종합 점수 (가중 평균)
        portfolio_score = sum(s['ai_score'] * s['weight'] / 100 for s in stock_analyses)
        
        # 4. 분산도 평가
        diversification = self._evaluate_diversification(stock_analyses)
        
        # 5. 리스크 밸런스 평가
        risk_balance = self._evaluate_risk_balance(stock_analyses)
        
        # 6. 투자 스타일 일치도 평가
        style_alignment = self._evaluate_style_alignment(stock_analyses)
        
        # 7. 리밸런싱 제안 생성
        rebalancing = self._generate_rebalancing_suggestions(stock_analyses, total_value)
        
        return {
            "portfolio_score": round(portfolio_score, 1),
            "total_value": total_value,
            "total_profit_loss": sum(s['profit_loss'] for s in stock_analyses),
            "total_profit_loss_pct": (sum(s['profit_loss'] for s in stock_analyses) / 
                                     sum(s['avg_price'] * s['shares'] for s in stock_analyses) * 100) 
                                     if sum(s['avg_price'] * s['shares'] for s in stock_analyses) > 0 else 0,
            "holdings": stock_analyses,
            "diversification": diversification,
            "risk_balance": risk_balance,
            "style_alignment": style_alignment,
            "rebalancing": rebalancing,
            "summary": self._generate_summary(portfolio_score, diversification, risk_balance, style_alignment)
        }
    
    def _analyze_holding(self, ticker: str, index_ticker: str) -> Optional[Dict[str, Any]]:
        """개별 종목 분석"""
        try:
            import yfinance as yf
            
            # 데이터 수집
            stock = yf.Ticker(ticker)
            daily_df = stock.history(period="1y")
            index_df = yf.Ticker(index_ticker).history(period="1y")
            
            if daily_df.empty:
                return None
            
            # 종합 분석
            analysis = self.analyst.analyze_ticker(
                ticker=ticker,
                daily_df=daily_df,
                index_df=index_df,
                financials=None,
                hourly_df=None,
                sentiment_data=None
            )
            
            # 섹터 정보 추가
            info = stock.info
            analysis['sector'] = info.get('sector', 'Unknown')
            analysis['current_price'] = daily_df['Close'].iloc[-1]
            
            return analysis
            
        except Exception as e:
            logger.error(f"{ticker} 분석 실패: {e}")
            return None
    
    def _evaluate_diversification(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """분산도 평가 (섹터/종목 집중도)"""
        sectors = [h['sector'] for h in holdings]
        sector_counts = Counter(sectors)
        
        # 섹터 집중도 (HHI: Herfindahl-Hirschman Index)
        sector_weights = [h['weight'] for h in holdings]
        hhi = sum(w**2 for w in sector_weights)
        
        # 점수 산출 (HHI가 낮을수록 분산이 잘 됨)
        if hhi < 2000:
            score = 90
            grade = "우수"
        elif hhi < 4000:
            score = 70
            grade = "양호"
        elif hhi < 6000:
            score = 50
            grade = "보통"
        else:
            score = 30
            grade = "집중"
        
        return {
            "score": score,
            "grade": grade,
            "hhi": round(hhi, 1),
            "sector_distribution": dict(sector_counts),
            "message": f"포트폴리오가 {len(sector_counts)}개 섹터에 분산되어 있습니다. 집중도: {grade}"
        }
    
    def _evaluate_risk_balance(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """리스크 밸런스 평가"""
        high_risk_weight = sum(h['weight'] for h in holdings if h['ai_score'] < 40)
        medium_risk_weight = sum(h['weight'] for h in holdings if 40 <= h['ai_score'] < 70)
        low_risk_weight = sum(h['weight'] for h in holdings if h['ai_score'] >= 70)
        
        # 균형 점수 (중위험 비중이 높을수록 좋음)
        if high_risk_weight > 50:
            score = 40
            message = "⚠️ 고위험 종목 비중이 과도합니다. 리스크 관리가 필요합니다."
        elif medium_risk_weight > 40:
            score = 80
            message = "✅ 리스크가 적절히 분산되어 있습니다."
        else:
            score = 60
            message = "💡 안정적이지만 수익 기회가 제한적일 수 있습니다."
        
        return {
            "score": score,
            "high_risk_pct": round(high_risk_weight, 1),
            "medium_risk_pct": round(medium_risk_weight, 1),
            "low_risk_pct": round(low_risk_weight, 1),
            "message": message
        }
    
    def _evaluate_style_alignment(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """투자 스타일 일치도 평가"""
        user_style = self.profiler.get_style()
        
        if not user_style:
            return {
                "score": 50,
                "message": "투자 스타일이 설정되지 않았습니다. 프로파일을 먼저 설정해 주세요."
            }
        
        # 스타일별 이상적인 점수 범위
        ideal_ranges = {
            "aggressive_growth": (60, 100),
            "dividend": (50, 80),
            "value": (40, 70),
            "momentum": (55, 90),
            "balanced": (45, 75)
        }
        
        ideal_min, ideal_max = ideal_ranges.get(user_style, (40, 80))
        
        # 포트폴리오 평균 점수가 이상 범위에 있는지 확인
        avg_score = np.mean([h['ai_score'] for h in holdings])
        
        if ideal_min <= avg_score <= ideal_max:
            alignment_score = 90
            message = f"✅ 포트폴리오가 '{self.profiler.STYLES[user_style]['name']}' 스타일에 잘 맞습니다."
        else:
            alignment_score = 50
            message = f"💡 포트폴리오가 '{self.profiler.STYLES[user_style]['name']}' 스타일과 다소 차이가 있습니다."
        
        return {
            "score": alignment_score,
            "user_style": user_style,
            "style_name": self.profiler.STYLES[user_style]['name'],
            "message": message
        }
    
    def _generate_rebalancing_suggestions(self, 
                                         holdings: List[Dict[str, Any]],
                                         total_value: float) -> Dict[str, Any]:
        """리밸런싱 제안 생성"""
        suggestions = {
            "sell": [],
            "buy": [],
            "adjust": []
        }
        
        # 1. 매도 추천 (점수 낮음 or 비중 과다)
        for h in holdings:
            if h['ai_score'] < 35:
                suggestions["sell"].append({
                    "ticker": h['ticker'],
                    "reason": f"AI 점수가 {h['ai_score']}로 매우 낮습니다. {h['signal']}",
                    "current_weight": h['weight'],
                    "action": "전량 매도 고려"
                })
            elif h['weight'] > 30:
                suggestions["adjust"].append({
                    "ticker": h['ticker'],
                    "reason": f"비중이 {h['weight']:.1f}%로 과도합니다. 리스크 분산이 필요합니다.",
                    "current_weight": h['weight'],
                    "target_weight": 20,
                    "action": f"비중을 20% 이하로 조정"
                })
        
        # 2. 매수 추천 (사용자 스타일에 맞는 신규 종목)
        user_style = self.profiler.get_style()
        if user_style:
            # 현재 보유하지 않은 유망 종목 찾기
            current_tickers = {h['ticker'] for h in holdings}
            sample_pool = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "WMT", "JNJ", "PG"]
            candidates = [t for t in sample_pool if t not in current_tickers]
            
            if candidates:
                top_picks = self.screener.screen_stocks(
                    tickers=candidates[:5],  # 샘플로 5개만
                    investor_style=user_style,
                    top_n=2
                )
                
                for pick in top_picks:
                    suggestions["buy"].append({
                        "ticker": pick['ticker'],
                        "reason": pick['reason'],
                        "ai_score": pick['score'],
                        "action": f"신규 매수 고려 (목표 비중: 10%)"
                    })
        
        return suggestions
    
    def _generate_summary(self, 
                         portfolio_score: float,
                         diversification: Dict[str, Any],
                         risk_balance: Dict[str, Any],
                         style_alignment: Dict[str, Any]) -> str:
        """종합 평가 요약"""
        lines = []
        lines.append(f"📊 포트폴리오 종합 점수: {portfolio_score:.1f}/100")
        lines.append(f"")
        lines.append(f"🎯 분산도: {diversification['grade']} ({diversification['score']}점)")
        lines.append(f"⚖️ 리스크 밸런스: {risk_balance['score']}점")
        lines.append(f"🎨 스타일 일치도: {style_alignment['score']}점")
        lines.append(f"")
        
        if portfolio_score >= 70:
            lines.append("✅ 전반적으로 우수한 포트폴리오입니다. 현재 전략을 유지하세요.")
        elif portfolio_score >= 50:
            lines.append("💡 양호한 포트폴리오이나, 일부 개선이 필요합니다. 리밸런싱 제안을 참고하세요.")
        else:
            lines.append("⚠️ 포트폴리오 점검이 필요합니다. 리밸런싱을 적극 고려하세요.")
        
        return "\n".join(lines)


# 사용 예시
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = PortfolioAnalyzer()
    
    # 샘플 포트폴리오
    my_holdings = [
        {"ticker": "AAPL", "shares": 10, "avg_price": 150},
        {"ticker": "MSFT", "shares": 5, "avg_price": 300},
        {"ticker": "GOOGL", "shares": 3, "avg_price": 2500},
    ]
    
    result = analyzer.analyze_portfolio(my_holdings)
    
    print(result['summary'])
    print("\n=== 리밸런싱 제안 ===")
    if result['rebalancing']['sell']:
        print("\n[매도 추천]")
        for s in result['rebalancing']['sell']:
            print(f"  • {s['ticker']}: {s['reason']}")
