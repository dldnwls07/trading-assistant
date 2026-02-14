import logging
import os
from typing import Dict, Any, List
from src.utils.kis_client import KISClient
from src.data.storage import get_storage
from src.utils.notifications import send_alert

logger = logging.getLogger(__name__)

class OrderExecutor:
    """
    매매 집행 에이전트
    AI의 분석 결과를 바탕으로 실제 또는 가상 주문을 수행
    """
    
    def __init__(self, kis_client: KISClient = None):
        self.kis = kis_client
        self.storage = get_storage()
        # 가상 계좌 모드 여부 (.env에서 관리)
        self.is_virtual = os.getenv("IS_VIRTUAL", "True").lower() == "true"

    def execute_trade(self, ticker: str, side: str, quantity: int, price: float) -> Dict[str, Any]:
        """
        단일 종목 매매 집행 (가상/실전 통합)
        """
        if self.is_virtual:
            return self._execute_virtual_trade(ticker, side, quantity, price)
        else:
            if not self.kis:
                return {"error": "KIS 클라이언트가 없습니다. 가상 모드로 전환하거나 API 설정을 완료하세요."}
            
            is_domestic = ticker.isdigit() or ticker.endswith(('.KS', '.KQ'))
            clean_ticker = ticker.split('.')[0]
            
            res = self.kis.place_order(
                ticker=clean_ticker,
                quantity=quantity,
                is_buy=(side == 'BUY'),
                is_domestic=is_domestic
            )
            
            if res.get("status") == "success":
                msg = f"🟢 [실전 매매 SUCCESS] {ticker} {side} {quantity}주 @ {price}"
                send_alert(msg, title="💰 Real Trading Alert")
            return res

    def _get_exchange_rate(self) -> float:
        """실시간 USD/KRW 환율 조회"""
        try:
            import yfinance as yf
            rate_data = yf.Ticker("USDKRW=X").history(period="1d")
            if not rate_data.empty:
                return float(rate_data['Close'].iloc[-1])
        except Exception as e:
            logger.error(f"Failed to fetch exchange rate: {e}")
        return 1350.0  # Fallback

    def _execute_virtual_trade(self, ticker: str, side: str, quantity: int, price: float) -> Dict[str, Any]:
        """가상 매매 내부 로직"""
        is_usd = not (ticker.endswith(('.KS', '.KQ')) or ticker.isdigit())
        exchange_rate = self._get_exchange_rate() if is_usd else 1.0
        
        total_amount_krw = price * quantity * exchange_rate
        
        try:
            if side == 'BUY':
                balance = self.storage.get_virtual_balance()
                if balance < total_amount_krw:
                    return {"status": "error", "message": f"잔액 부족 (가상) - 필요: {total_amount_krw:,.0f}원"}
                
                self.storage.update_virtual_balance(-total_amount_krw)
                self.storage.update_virtual_position(ticker, quantity, price, 'BUY')
                
            elif side == 'SELL':
                positions = self.storage.get_virtual_positions()
                pos = next((p for p in positions if p['ticker'] == ticker), None)
                if not pos or pos['quantity'] < quantity:
                    return {"status": "error", "message": "보유 수량 부족 (가상)"}
                
                self.storage.update_virtual_balance(total_amount_krw)
                self.storage.update_virtual_position(ticker, quantity, price, 'SELL')
            
            curr_sym = "$" if is_usd else "₩"
            msg = f"🔵 [가상 매매 체결] {ticker} {side} {quantity}주 @ {curr_sym}{price:.2f}"
            if is_usd:
                msg += f" (환율: {exchange_rate:.2f})"
            msg += f"\n현재 잔고: {self.storage.get_virtual_balance():,.0f}원"
            
            send_alert(msg, title="🎮 Paper Trading Alert")
            return {"status": "success", "ticker": ticker, "side": side, "quantity": quantity, "price": price}
            
        except Exception as e:
            logger.error(f"Virtual trade error: {e}")
            return {"status": "error", "message": str(e)}

    def calculate_position_size(self, ticker: str, price: float) -> int:
        """단순 비중 계산: 가용한 현금의 10%를 한 종목에 배정"""
        if self.is_virtual:
            balance = self.storage.get_virtual_balance()
        else:
            balance = 10000000.0 # 임시
            
        is_usd = not (ticker.endswith(('.KS', '.KQ')) or ticker.isdigit())
        exchange_rate = self._get_exchange_rate() if is_usd else 1.0
        
        target_cash_krw = balance * 0.1
        shares = int(target_cash_krw / (price * exchange_rate))
        return max(1, shares)
