from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.domains.agents.service import AgentManagerService

router = APIRouter(prefix="/api/agents", tags=["Agents"])
agent_service = AgentManagerService()

class AgentCreateRequest(BaseModel):
    name: str
    llm_weight: float = 0.5
    rl_weight: float = 0.5
    risk_tolerance: str = "medium"
    base_llm: str = "gemini"
    initial_balance: float = 10000000.0

class AgentStatusToggleRequest(BaseModel):
    is_active: int

@router.post("")
async def create_agent(req: AgentCreateRequest):
    try:
        agent = await agent_service.create_agent(
            name=req.name,
            llm_weight=req.llm_weight,
            rl_weight=req.rl_weight,
            risk_tolerance=req.risk_tolerance,
            base_llm=req.base_llm,
            initial_balance=req.initial_balance
        )
        return {"status": "success", "agent_id": agent.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
async def get_agents(active_only: bool = False):
    try:
        agents = await agent_service.get_all_agents(active_only=active_only)
        return {
            "status": "success", 
            "agents": [
                {
                    "id": a.id, "name": a.name, "llm_weight": a.llm_weight, 
                    "rl_weight": a.rl_weight, "is_active": a.is_active, 
                    "created_at": a.created_at
                } for a in agents
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leaderboard")
async def get_leaderboard():
    try:
        leaderboard = await agent_service.get_leaderboard()
        return {"status": "success", "leaderboard": leaderboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{agent_id}/toggle")
async def toggle_agent(agent_id: int, req: AgentStatusToggleRequest):
    try:
        await agent_service.toggle_agent_status(agent_id, req.is_active)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{agent_id}")
async def delete_agent(agent_id: int):
    try:
        await agent_service.delete_agent(agent_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
