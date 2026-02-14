import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class Backtester:
    """
    고속 벡터화 백테스팅 엔진
    과거 데이터를 바탕으로 매매 신호의 유효성을 검증
    """
    
    @staticmethod
    def backtest_vectorized(df: pd.DataFrame, signals: pd.Series, initial_capital: float = 10000.0) -> Dict[str, Any]:
        """
        벡터화된 방식을 활용한 초고속 백테스트 (Long 전용 기준)
        signals: 1 (매수), 0 (관망), -1 (매도)
        """
        try:
            if df.empty or signals.empty:
                return {"success": False, "message": "데이터가 부족합니다."}
            
            # 신호와 수익률 정렬
            returns = df['Close'].pct_change().shift(-1) # 오늘 신호로 내일 수익률을 먹음
            
            # 거래 비용 (0.1% 가정)
            commission = 0.001
            
            # 포지션 변경 감지 (거래 비용 계산용)
            trades = signals.diff().abs().fillna(0)
            
            # 전략 수익률 계산
            strategy_returns = signals * returns
            net_returns = strategy_returns - (trades * commission)
            
            # 누적 수익률
            cum_returns = (1 + net_returns).cumprod()
            portfolio_value = initial_capital * cum_returns
            
            # 메트릭 산출
            total_return = (cum_returns.iloc[-1] - 1) * 100 if not cum_returns.empty else 0
            
            # 승률 계산
            trade_results = net_returns[signals != 0]
            win_rate = (trade_results > 0).mean() * 100 if not trade_results.empty else 0
            
            # MDD (Max Drawdown)
            peak = portfolio_value.expanding(min_periods=1).max()
            drawdown = (portfolio_value - peak) / peak
            mdd = drawdown.min() * 100
            
            # 손익비 (Profit Factor)
            gross_profits = net_returns[net_returns > 0].sum()
            gross_losses = abs(net_returns[net_returns < 0].sum())
            profit_factor = gross_profits / gross_losses if gross_losses != 0 else float('inf')
            
            return {
                "success": True,
                "total_return_pct": round(total_return, 2),
                "win_rate": round(win_rate, 2),
                "mdd_pct": round(mdd, 2),
                "profit_factor": round(profit_factor, 2),
                "final_value": round(portfolio_value.iloc[-1], 2) if not portfolio_value.empty else initial_capital,
                "num_trades": int(trades.sum())
            }
            
        except Exception as e:
            logger.error(f"백테스트 중 오류 발생: {e}")
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_summary_text(results: Dict[str, Any]) -> str:
        """분석 결과 요약 텍스트 생성"""
        if not results.get("success"):
            return "백테스트 데이터를 산출할 수 없습니다."
            
        return (f"최근 1년 백테스트 결과: 승률 {results['win_rate']}% | "
                f"수익률 {results['total_return_pct']}% | "
                f"손익비 {results['profit_factor']} | "
                f"MDD {results['mdd_pct']}%")
