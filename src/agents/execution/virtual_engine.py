import asyncio
import logging
from typing import Optional
from src.domains.agents.service import AgentManagerService
from src.agents.execution.executor import OrderExecutor
from src.agents.core.analyst import StockAnalyst
from src.agents.analysis.screener import StockScreener
from src.utils.market_utils import is_market_open
from src.data.storage import get_storage

logger = logging.getLogger(__name__)

class VirtualTradingEngine:
    def __init__(self):
        self.agent_service = AgentManagerService()
        self.executor = OrderExecutor()
        self.analyst = StockAnalyst()
        self.screener = StockScreener(analyst=self.analyst)
        self.storage = get_storage()
        self.is_running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("🚀 Virtual Trading Engine Started")

    async def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("🛑 Virtual Trading Engine Stopped")

    async def _run_loop(self):
        while self.is_running:
            try:
                agents = await self.agent_service.get_all_agents(active_only=True)
                if not agents:
                    await asyncio.sleep(60)
                    continue
                
                # 매 1분마다 한번씩 스크리너 추천 종목(US) 가져오기
                recommendations = await self.screener.get_recommendations(style="momentum", market="US", limit=5)
                recs_list = recommendations.get('recommendations', [])

                for agent in agents:
                    logger.debug(f"Processing Real-time logic for Agent: {agent.name} (LLM: {agent.llm_weight}, RL: {agent.rl_weight})")
                    
                    # 1. SELL LOGIC: 기존 보유 종목 체크 후 매도 판단
                    positions = await self.storage.get_virtual_positions(agent_id=agent.id)
                    for pos in positions:
                        ticker = pos['ticker']
                        if not is_market_open(ticker): continue
                        
                        daily_df = await self.screener._fetch_data(ticker, period="1y")
                        if daily_df is None: continue
                        
                        analysis = self.analyst.analyze_ticker(ticker, daily_df)
                        score = analysis.get('final_score', 50)
                        
                        # 위험 선호도에 따른 매도 임계치 설정 (보수적일수록 빨리 팖)
                        sell_threshold = 45
                        if agent.risk_tolerance == 'high':
                            sell_threshold = 35  # 더 오래 버팀
                        elif agent.risk_tolerance == 'low':
                            sell_threshold = 55  # 하락하면 빨리 팖
                            
                        # RL 비중이 높을수록 기술적 스코어에 엄격하게 반응
                        adjusted_sell_threshold = sell_threshold + (agent.rl_weight * 5)
                        
                        if score <= adjusted_sell_threshold:
                            current_price = float(daily_df['Close'].iloc[-1])
                            logger.info(f"[{agent.name}] 🚨 SELL Signal for {ticker} (Score: {score} <= {adjusted_sell_threshold})")
                            await self.executor.execute_trade(ticker, 'SELL', pos['quantity'], current_price, agent_id=agent.id)

                    # 2. BUY LOGIC: 충분한 자금 있을 때 추천 종목 매수 판단
                    balance = await self.storage.get_virtual_balance(agent_id=agent.id)
                    if balance < 100000: continue
                    
                    for rec in recs_list:
                        ticker = rec['ticker']
                        if not is_market_open(ticker): continue
                        if any(p['ticker'] == ticker for p in positions): continue # 이미 보유 중이면 스킵
                        
                        daily_df = await self.screener._fetch_data(ticker, period="1y")
                        if daily_df is None: continue
                        
                        analysis = self.analyst.analyze_ticker(ticker, daily_df)
                        score = analysis.get('final_score', 50)
                        
                        buy_threshold = 75
                        if agent.risk_tolerance == 'high':
                            buy_threshold = 65  # 쉽게 매수
                        elif agent.risk_tolerance == 'low':
                            buy_threshold = 80  # 확실할 때만 매수
                            
                        # LLM 비중이 높으면 더 고집스럽게(점수 임계치 상향), RL이 높으면 트렌드 추종(임계치 완화)
                        adjusted_buy_threshold = buy_threshold + (agent.llm_weight * 5) - (agent.rl_weight * 5)

                        if score >= adjusted_buy_threshold:
                            price = rec['current_price']
                            
                            exchange_rate = 1350.0  # 기본값, 실제 executor 내부에서 재계산됨
                            trade_value_limit = balance * 0.2  # 1회 최대 20%만 투자
                            
                            shares = int(trade_value_limit / (price * exchange_rate))
                            if shares > 0:
                                logger.info(f"[{agent.name}] 🎯 BUY Signal for {ticker} (Score: {score} >= {adjusted_buy_threshold})")
                                await self.executor.execute_trade(ticker, 'BUY', shares, price, agent_id=agent.id)
                                break  # Loop당 에이전트별 최대 1종목만 신규 진입
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in VirtualTradingEngine loop: {e}")
                
            # Run every 60 seconds
            await asyncio.sleep(60)
            
# Singleton instance
virtual_engine = VirtualTradingEngine()
