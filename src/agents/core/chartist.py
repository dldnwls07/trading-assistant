"""
차트 마스터 - 기술적 분석 및 패턴 전문가 에이전트
유튜버 '아인주식' 스타일의 직관적이고 날카로운 차트 해석 제공
"""
import logging
import pandas as pd
from typing import Dict, Any, List, Optional
from src.agents.core.analyst import TechnicalAnalyzer
from src.utils.advanced_indicators import AdvancedIndicators

logger = logging.getLogger(__name__)

class ChartMaster:
    """
    전문 차티스트 에이전트
    - 캔들 패턴, 지지/저항, 추세선 분석 전문
    - 복잡한 지표를 일반인이 이해하기 쉽게 풀어서 설명
    """
    
    def __init__(self):
        self.tech = TechnicalAnalyzer()
        
    def analyze_chart(self, ticker: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        차트를 기술적으로 분석하고 전문가 관점의 코멘트 생성
        """
        if df is None or df.empty:
            return {"error": "데이터가 부족하여 분석할 수 없습니다."}
            
        # 1. 기술적 지표 계산
        tech_res = self.tech.analyze(df)
        
        # 2. 고급 패턴 감지
        patterns = self.tech.detect_patterns(df)
        
        # 3. 추가 지표 (Advanced)
        df_advanced = AdvancedIndicators.calculate_all(df.copy())
        current = df_advanced.iloc[-1]
        
        # 4. 차티스트의 핵심 인사이트 (비즈니스 로직)
        insight = self._generate_chartist_insight(ticker, tech_res, patterns, current)
        
        entry = tech_res.get('entry_points', {})
        
        return {
            "ticker": ticker,
            "summary": insight['summary'],
            "signal": tech_res.get('signal_text', '중립'), # signal_text가 없으면 기본값
            "score": tech_res['score'],
            "support": entry.get('buy', 'N/A'),
            "resistance": entry.get('target', 'N/A'),
            "patterns": [p['name'] for p in patterns[:3]],
            "commentary": insight['commentary']
        }
        
    def _generate_chartist_insight(self, ticker: str, tech: Dict, patterns: List, current: pd.Series) -> Dict[str, str]:
        """전문 차티스트의 어조로 인사이트 생성"""
        
        # 상태 파악 (TechnicalAnalyzer 반환 키에 맞춤)
        rsi = tech.get('rsi', 50)
        signal = tech.get('signal', 0)
        
        # sma_20 등이 current(AdvancedIndicators 결과)에 있는지 확인
        ma_status = "정배열" if current.get('sma_20', 0) > current.get('sma_60', 0) else "역배열"
        
        summary = f"현재 {ticker}는 {ma_status} 상태에서 "
        if rsi > 70: summary += "과매수 구간에 진입하여 단기 조정 가능성이 높습니다."
        elif rsi < 30: summary += "과매도 구간에서 바닥 다지기를 시도 중입니다."
        else: summary += "추세 형성을 위한 에너지를 응축하고 있습니다."
        
        # 상세 코멘터리 (유튜버 스타일)
        commentary = f"안녕하십니까. {ticker} 차트 분석입니다. "
        
        if patterns:
            best_pattern = patterns[0]['name']
            commentary += f"현재 차트에서 가장 눈에 띄는 건 '{best_pattern}' 패턴입니다. 이건 세력들이 물량을 매집하거나 털어낼 때 자주 나오는 형태죠. "
        
        # entry_points에서 지지/저항 활용
        entry = tech.get('entry_points', {})
        sup_price = entry.get('buy', '직전 저점')
        res_price = entry.get('target', '전고점')
        
        commentary += f"현재 지지선은 {sup_price} 부근으로 보입니다. "
        commentary += f"여기서 거래량이 실리면서 {res_price}을(를) 돌파해준다면 아주 강력한 슈팅이 나올 수 있는 자리입니다. "
        
        # 점수 기반 신호 판단 (0~100)
        score = tech.get('score', 50)
        if score >= 75:
            commentary += "지금은 공격적으로 비중을 늘려가기 아주 좋은 셋업입니다. 손절가는 짧게 잡고 대응해보시길 권합니다."
        elif score <= 35:
            commentary += "욕심 부릴 자리가 아닙니다. 일단 수익 실현하고 관망하면서 현금을 확보하는 게 상책입니다."
        else:
            commentary += "방향성이 나올 때까지 분할 매수로 접근하며 대응 영역으로 남겨두는 게 좋겠습니다."
            
        return {
            "summary": summary,
            "commentary": commentary
        }

# 사용 예시
if __name__ == "__main__":
    from src.data.collector import MarketDataCollector
    import asyncio
    
    async def test():
        collector = MarketDataCollector(use_db=False)
        df = await collector.get_ohlcv("AAPL", period="1y")
        master = ChartMaster()
        res = master.analyze_chart("AAPL", df)
        print(f"[{res['ticker']}] {res['summary']}")
        print(f"의견: {res['commentary']}")
        
    asyncio.run(test())
