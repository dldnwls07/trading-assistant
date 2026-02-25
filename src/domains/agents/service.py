import logging
from typing import List, Dict, Any
from src.data.storage import get_storage, CustomAgent

logger = logging.getLogger(__name__)

class AgentManagerService:
    def __init__(self):
        self.storage = get_storage()

    async def create_agent(self, name: str, llm_weight: float, rl_weight: float, risk_tolerance: str, base_llm: str, initial_balance: float) -> CustomAgent:
        agent = await self.storage.create_custom_agent(
            name=name, llm_weight=llm_weight, rl_weight=rl_weight,
            risk_tolerance=risk_tolerance, base_llm=base_llm, initial_balance=initial_balance
        )
        # Create initial virtual account for this agent
        await self.storage.get_virtual_balance(agent_id=agent.id)
        return agent

    async def get_all_agents(self, active_only: bool = False) -> List[CustomAgent]:
        return await self.storage.get_custom_agents(active_only=active_only)
        
    async def get_agent(self, agent_id: int) -> CustomAgent:
        return await self.storage.get_custom_agent(agent_id)

    async def toggle_agent_status(self, agent_id: int, is_active: int):
        await self.storage.update_custom_agent_status(agent_id, is_active)
        
    async def delete_agent(self, agent_id: int):
        await self.storage.delete_custom_agent(agent_id)

    async def get_leaderboard(self) -> List[Dict[str, Any]]:
        agents = await self.get_all_agents()
        leaderboard = []
        
        # In MVP we evaluate portfolio by balance + (qty * avg_price).
        # In a real scenario we could fetch real-time market prices here.
        for agent in agents:
            balance = await self.storage.get_virtual_balance(agent_id=agent.id)
            positions = await self.storage.get_virtual_positions(agent_id=agent.id)
            
            total_position_value = sum(p['quantity'] * p['avg_price'] for p in positions)
            total_value = balance + total_position_value
            initial_balance = agent.initial_balance if hasattr(agent, 'initial_balance') else 10000000.0
            roi = ((total_value - initial_balance) / initial_balance) * 100
            
            leaderboard.append({
                "agent_id": agent.id,
                "name": agent.name,
                "llm_weight": agent.llm_weight,
                "rl_weight": agent.rl_weight,
                "risk_tolerance": agent.risk_tolerance,
                "base_llm": agent.base_llm,
                "initial_balance": initial_balance,
                "total_value": total_value,
                "roi": roi,
                "is_active": agent.is_active,
                "positions_count": len(positions)
            })
            
        # Sort by ROI descending
        leaderboard.sort(key=lambda x: x['roi'], reverse=True)
        
        for i, item in enumerate(leaderboard):
            item['rank'] = i + 1
            
        return leaderboard
