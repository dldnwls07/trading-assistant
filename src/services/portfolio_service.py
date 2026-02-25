import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PortfolioService:
    def __init__(self, storage_client, collector_client, portfolio_analyzer_client):
        self.storage = storage_client
        self.collector = collector_client
        self.portfolio_analyzer = portfolio_analyzer_client

    def analyze_portfolio(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """포트폴리오 AI 분석 수행"""
        return self.portfolio_analyzer.analyze_portfolio(holdings)

    async def get_virtual_account_info(self, agent_id: int = None) -> Dict[str, Any]:
        """가상 계좌 잔고 및 수익률 정보 계산"""
        balance = await self.storage.get_virtual_balance(agent_id)
        
        initial_balance = 10000000.0
        if agent_id:
            agent = await self.storage.get_custom_agent(agent_id)
            if agent:
                initial_balance = agent.initial_balance
                
        profit = balance - initial_balance
        
        return {
            "balance": balance,
            "currency": "KRW",
            "initial_balance": initial_balance,
            "total_profit": profit,
            "profit_rate": (profit / initial_balance) * 100 if initial_balance > 0 else 0
        }

    async def get_virtual_positions_with_current_prices(self, usd_krw_rate: float, agent_id: int = None) -> List[Dict[str, Any]]:
        """가상 계좌 보유 종목과 현재가 및 수익률 명세 계산"""
        positions = await self.storage.get_virtual_positions(agent_id)
        
        processed_positions = []
        for pos in positions:
            ticker = pos['ticker']
            is_usd = not (ticker.endswith(('.KS', '.KQ')) or ticker.isdigit())
            
            df = await self.collector.get_ohlcv(ticker, period="1d", interval="1m")
            current_price = df['Close'].iloc[-1] if df is not None and not df.empty else pos['avg_price']
            
            price_in_krw = current_price * usd_krw_rate if is_usd else current_price
            avg_in_krw = pos['avg_price'] * usd_krw_rate if is_usd else pos['avg_price']
            
            profit_krw = (price_in_krw - avg_in_krw) * pos['quantity']
            profit_rate = ((current_price - pos['avg_price']) / pos['avg_price']) * 100
            
            processed_positions.append({
                **pos,
                "is_usd": is_usd,
                "current_price": current_price,
                "current_price_krw": price_in_krw,
                "profit_krw": profit_krw,
                "profit_rate": profit_rate,
                "total_value_native": current_price * pos['quantity'],
                "total_value_krw": price_in_krw * pos['quantity']
            })
            
        return processed_positions
