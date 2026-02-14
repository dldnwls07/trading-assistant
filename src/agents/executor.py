import logging
from typing import Dict, Any, List
from src.utils.kis_client import KISClient

logger = logging.getLogger(__name__)

class OrderExecutor:
    """
    매매 집행 에이전트
    AI의 분석 결과를 바탕으로 실제 주문을 수행
    """
    
    def __init__(self, kis_client: KISClient):
        self.kis = kis_client

    def execute_rebalancing(self, suggestions: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        리밸런싱 제안에 따라 일괄 매매 집행
        """
        results = []
        
        # 1. 매도(Sell) 및 비중 축소(Adjust) 먼저 처리 (현금 확보)
        for item in suggestions.get("sell", []):
            res = self.place_smart_order(item['ticker'], item['shares'], is_buy=False)
            results.append({"action": "SELL", "ticker": item['ticker'], "result": res})
            
        for item in suggestions.get("adjust", []):
            # 비중 축소 로직 (현재 수량 대비 목표 수량 계산 필요)
            # 여기서는 예시로 로직 생략하고 로그만 남김
            logger.info(f"Adjusting weight for {item['ticker']}")
            
        # 2. 매수(Buy) 처리
        for item in suggestions.get("buy", []):
            # 목표 금액 또는 수량 계산 로직 필요
            # 예시로 1주만 매수 테스트
            res = self.place_smart_order(item['ticker'], 1, is_buy=True)
            results.append({"action": "BUY", "ticker": item['ticker'], "result": res})
            
        return results

    def calculate_position_size(self, total_capital: float, price: float, atr: float, risk_factor: float = 0.01) -> int:
        """
        리스크 기반 포지션 사이징 (ATR 활용)
        - risk_factor: 전체 자산 중 한 종목에서 감수할 최대 손실 (기본 1%)
        - 정규식: (전체자본 * 리스크계수) / (ATR * 2) = 적정 수량
        """
        if price <= 0 or atr <= 0:
            return 1
            
        # 1-R 리스크 모델 (ATR의 2배를 스탑로스로 가정)
        risk_amount = total_capital * risk_factor
        shares = int(risk_amount / (atr * 2))
        
        # 자산 대비 너무 큰 포지션 방지 (최대 20% 제한)
        max_shares = int((total_capital * 0.2) / price)
        
        return max(1, min(shares, max_shares))

    def place_smart_order(self, ticker: str, quantity: int, is_buy: bool = True) -> Dict[str, Any]:
        """
        종목 코드 정제 및 주문 실행
        """
        # 티커 정제 (.KS, .KQ 제거)
        clean_ticker = ticker.split('.')[0]
        is_domestic = ticker.endswith(('.KS', '.KQ')) or clean_ticker.isdigit()
        
        logger.info(f"주문 실행: {ticker} ({'매수' if is_buy else '매도'}) - {quantity}주")
        
        if not self.kis:
            return {"error": "KIS 클라이언트가 초기화되지 않았습니다."}
            
        return self.kis.place_order(
            ticker=clean_ticker,
            quantity=quantity,
            is_buy=is_buy,
            is_domestic=is_domestic
        )
