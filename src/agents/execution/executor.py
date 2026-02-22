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

    async def execute_trade(self, ticker: str, side: str, quantity: int, price: float) -> Dict[str, Any]:
        """
        단일 종목 매매 집행 (가상/실전 통합)
        """
        if self.is_virtual:
            return await self._execute_virtual_trade(ticker, side, quantity, price)
        else:
            # 실전 매매는 KIS API(동기)를 사용하므로 필요시 스레드 풀 고려
            if not self.kis:
                return {"error": "KIS 클라이언트가 없습니다."}
            
            is_domestic = ticker.isdigit() or ticker.endswith(('.KS', '.KQ'))
            clean_ticker = ticker.split('.')[0]
            
            res = self.kis.place_order(ticker=clean_ticker, quantity=quantity, is_buy=(side == 'BUY'), is_domestic=is_domestic)
            
            if res.get("status") == "success":
                msg = f"🟢 [실전 매매 SUCCESS] {ticker} {side} {quantity}주 @ {price}"
                await send_alert(msg, title="💰 Real Trading Alert")
            return res

    async def _get_exchange_rate(self) -> float:
        """실시간 USD/KRW 환율 조회 (비동기)"""
        try:
            from src.data.collector import MarketDataCollector
            collector = MarketDataCollector(use_db=False)
            df = await collector.get_ohlcv("USDKRW=X", period="1d", interval="1m")
            if df is not None and not df.empty:
                return float(df['Close'].iloc[-1])
        except Exception as e:
            logger.error(f"Failed to fetch exchange rate: {e}")
        return 1350.0

    async def _execute_virtual_trade(self, ticker: str, side: str, quantity: int, price: float) -> Dict[str, Any]:
        """가상 매매 내부 로직 (정교화된 시뮬레이션)"""
        is_usd = not (ticker.endswith(('.KS', '.KQ')) or ticker.isdigit())
        exchange_rate = (await self._get_exchange_rate()) if is_usd else 1.0
        
        # 1. 슬리피지 적용 (0.05% ~ 0.1% 무작위 또는 고정)
        slippage = 0.001 # 0.1% 슬리피지 가정
        executed_price = price * (1 + slippage) if side == 'BUY' else price * (1 - slippage)
        
        # 2. 거래 세금 및 수수료 계산
        # 한국: 매수 0.015%, 매도 0.015% + 거래세 0.18%
        # 미국: 매수 0.25%, 매도 0.25% (국내 증권사 대행 기준)
        if not is_usd:
            fee_rate = 0.00015 # 0.015%
            tax_rate = 0.0018 if side == 'SELL' else 0 # 매도 시에만 코스피/코스닥 평균 0.18%
        else:
            fee_rate = 0.0025 # 0.25%
            tax_rate = 0
            
        trade_value_krw = executed_price * quantity * exchange_rate
        fees_krw = trade_value_krw * fee_rate
        taxes_krw = trade_value_krw * tax_rate
        
        total_impact_krw = trade_value_krw + fees_krw + taxes_krw if side == 'BUY' else -(trade_value_krw - fees_krw - taxes_krw)
        
        try:
            await self.storage.initialize()
            if side == 'BUY':
                balance = await self.storage.get_virtual_balance()
                if balance < total_impact_krw:
                    return {"status": "error", "message": f"잔액 부족 (가상) - 필요: {total_impact_krw:,.0f}원"}
                
                await self.storage.update_virtual_balance(-total_impact_krw)
                await self.storage.update_virtual_position(ticker, quantity, executed_price, 'BUY')
                
            elif side == 'SELL':
                positions = await self.storage.get_virtual_positions()
                pos = next((p for p in positions if p['ticker'] == ticker), None)
                if not pos or pos['quantity'] < quantity:
                    return {"status": "error", "message": "보유 수량 부족 (가상)"}
                
                await self.storage.update_virtual_balance(-total_impact_krw) # Selling is negative impact on negative amount = addition
                await self.storage.update_virtual_position(ticker, quantity, executed_price, 'SELL')
            
            curr_sym = "$" if is_usd else "₩"
            current_balance = await self.storage.get_virtual_balance()
            
            detail_msg = f"체결가: {curr_sym}{executed_price:.2f} (슬리피지 반영)\n수수료: {fees_krw:,.0f}원, 세금: {taxes_krw:,.0f}원"
            msg = f"🔵 [가상 매매 체결] {ticker} {side} {quantity}주\n{detail_msg}\n현재 잔고: {current_balance:,.0f}원"
            
            await send_alert(msg, title="🎮 Paper Trading Detail Alert")
            return {
                "status": "success", 
                "ticker": ticker, 
                "side": side, 
                "quantity": quantity, 
                "price": executed_price,
                "fees": fees_krw,
                "taxes": taxes_krw
            }
        except Exception as e:
            logger.error(f"Virtual trade error: {e}")
            return {"status": "error", "message": str(e)}

    async def calculate_position_size(self, ticker: str, price: float) -> int:
        """비중 계산 (비동기 환율 반영)"""
        if self.is_virtual:
            await self.storage.initialize()
            balance = await self.storage.get_virtual_balance()
        else:
            balance = 10000000.0
            
        is_usd = not (ticker.endswith(('.KS', '.KQ')) or ticker.isdigit())
        exchange_rate = (await self._get_exchange_rate()) if is_usd else 1.0
        
        target_cash_krw = balance * 0.1 # 10% 비중
        shares = int(target_cash_krw / (price * exchange_rate))
        return max(1, shares)
