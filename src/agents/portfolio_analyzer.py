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
    
    def _get_exchange_rate(self) -> float:
        """실시간 USD/KRW 환율 가져오기 (yfinance)"""
        try:
            import yfinance as yf
            ticker = yf.Ticker("USDKRW=X")
            data = ticker.history(period="1d")
            if not data.empty:
                return float(data['Close'].iloc[-1])
            return 1350.0  # 폴백 값
        except Exception as e:
            logger.warning(f"환율 수집 실패: {e}")
            return 1350.0

    def analyze_portfolio(self, 
                         holdings: List[Dict[str, Any]],
                         index_ticker: str = "^GSPC") -> Dict[str, Any]:
        """
        포트폴리오 종합 분석 (실시간 환율 반영)
        """
        logger.info(f"포트폴리오 분석 시작: {len(holdings)}개 종목")
        
        # 실시간 환율 적용
        USD_KRW = self._get_exchange_rate()
        logger.info(f"적용 환율: 1 USD = {USD_KRW} KRW")
        
        # 1. 각 종목 개별 분석 및 통화 통합
        stock_analyses = []
        total_value_usd = 0
        total_cost_usd = 0
        
        for holding in holdings:
            ticker = holding['ticker']
            shares = holding.get('shares', 0)
            avg_price = holding.get('avg_price', 0)
            
            # 현재 가격 및 분석
            analysis = self._analyze_holding(ticker, index_ticker)
            if analysis:
                current_price = analysis['current_price']
                
                # 통화 판별 (.KS, .KQ면 원화)
                is_krw = ticker.endswith(('.KS', '.KQ'))
                
                pos_value_native = shares * current_price
                cost_value_native = shares * avg_price
                
                # 달러로 통합
                pos_value_usd = pos_value_native / USD_KRW if is_krw else pos_value_native
                cost_value_usd = cost_value_native / USD_KRW if is_krw else cost_value_native
                
                total_value_usd += pos_value_usd
                total_cost_usd += cost_value_usd
                
                stock_analyses.append({
                    "ticker": ticker,
                    "shares": shares,
                    "avg_price": avg_price,
                    "current_price": current_price,
                    "position_value": pos_value_native,
                    "position_value_usd": pos_value_usd,
                    "profit_loss": (current_price - avg_price) * shares,
                    "profit_loss_pct": ((current_price - avg_price) / avg_price * 100) if avg_price > 0 else 0,
                    "ai_score": analysis['final_score'],
                    "signal": analysis['signal'],
                    "sector": analysis.get('sector', 'Unknown'),
                    "is_krw": is_krw,
                    "analysis": analysis
                })
        
        # 2. 비중 계산 (달러 가치 기준)
        for stock in stock_analyses:
            stock['weight'] = (stock['position_value_usd'] / total_value_usd * 100) if total_value_usd > 0 else 0
        
        # 3. 포트폴리오 종합 점수 (가중 평균)
        portfolio_score = sum(s['ai_score'] * s['weight'] / 100 for s in stock_analyses)
        
        # 4. 상관관계 분석 (추가)
        correlations = self._calculate_correlations([s['ticker'] for s in stock_analyses])
        
        # 5. 분산도 평가 (상관계수 반영)
        diversification = self._evaluate_diversification(stock_analyses, correlations)
        
        # 6. 리스크 밸런스 평가
        risk_balance = self._evaluate_risk_balance(stock_analyses)
        
        # 7. 투자 스타일 일치도 평가
        style_alignment = self._evaluate_style_alignment(stock_analyses)
        
        # 8. 리밸런싱 제안 생성
        rebalancing = self._generate_rebalancing_suggestions(stock_analyses, total_value_usd)
        
        return {
            "portfolio_score": round(portfolio_score, 1),
            "total_value": round(total_value_usd, 2),
            "total_profit_loss": round(total_value_usd - total_cost_usd, 2),
            "total_profit_loss_pct": round(((total_value_usd - total_cost_usd) / total_cost_usd * 100), 2) if total_cost_usd > 0 else 0,
            "holdings": stock_analyses,
            "correlations": correlations,
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
    
    def _calculate_correlations(self, tickers: List[str]) -> Dict[str, Any]:
        """종목 간 상관관계 계산"""
        if len(tickers) < 2:
            return {"matrix": {}, "avg_correlation": 0}
            
        try:
            import yfinance as yf
            # 최근 6개월 데이터 수집
            data = yf.download(tickers, period="6mo")['Close']
            returns = data.pct_change().dropna()
            
            corr_matrix = returns.corr()
            
            # JSON 직렬화 가능하도록 변환
            matrix_dict = corr_matrix.to_dict()
            
            # 평균 상관계수 (자기 자신 제외)
            avg_corr = (corr_matrix.sum().sum() - len(tickers)) / (len(tickers)**2 - len(tickers))
            
            return {
                "matrix": matrix_dict,
                "avg_correlation": round(avg_corr, 3)
            }
        except Exception as e:
            logger.error(f"상관관계 계산 실패: {e}")
            return {"matrix": {}, "avg_correlation": 0.5}

    def _evaluate_diversification(self, holdings: List[Dict[str, Any]], correlations: Dict[str, Any]) -> Dict[str, Any]:
        """분산도 평가 (섹터 집중도 + 상관관계 반영)"""
        sectors = [h['sector'] for h in holdings]
        sector_counts = Counter(sectors)
        
        # 1. 섹터 집중도 (HHI)
        sector_weights = [h['weight'] for h in holdings]
        hhi = sum(w**2 for w in sector_weights)
        
        # 2. 상관관계 점수 (평균 상관계수가 낮을수록 좋음)
        avg_corr = correlations.get("avg_correlation", 0.5)
        corr_score = max(0, 100 - (avg_corr * 100))
        
        # 3. 종합 분산 점수 (HHI 60% + 상관관계 40%)
        # HHI 점수 변환 (10000 -> 0, 0 -> 100)
        hhi_score = max(0, 100 - (hhi / 100))
        
        total_score = (hhi_score * 0.6) + (corr_score * 0.4)
        
        if total_score >= 80:
            grade = "우수"
            msg = "✅ 종목 및 섹터 분산이 매우 잘 되어 있으며 상관관계도 낮습니다."
        elif total_score >= 60:
            grade = "양호"
            msg = "✅ 전반적으로 양호한 분산 상태를 보입니다."
        elif total_score >= 40:
            grade = "보통"
            msg = "💡 분산도가 보통 수준입니다. 상관관계가 높은 종목이 있는지 확인하세요."
        else:
            grade = "집중"
            msg = "⚠️ 특정 종목/섹터에 과도하게 집중되었거나 종목 간 동조화가 강합니다."
        
        return {
            "score": round(total_score, 1),
            "grade": grade,
            "hhi": round(hhi, 1),
            "avg_correlation": avg_corr,
            "sector_distribution": dict(sector_counts),
            "message": msg
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
