import asyncio
from src.data.storage import get_storage
from src.domains.agents.service import AgentManagerService
import os

os.environ['IS_VIRTUAL'] = 'True'

async def main():
    print("Testing AgentManagerService...")
    storage = get_storage()
    await storage.initialize() # Ensure DB is created
    
    service = AgentManagerService()
    
    # Create agent
    agent = await service.create_agent("Growth Bot", 0.7, 0.3, "high", "gemini")
    print(f"Created Agent: {agent.name} (ID: {agent.id})")
    
    # Toggle off
    await service.toggle_agent_status(agent.id, 0)
    print("Toggled status to off")
    
    # Toggle on
    await service.toggle_agent_status(agent.id, 1)
    print("Toggled status to on")
    
    # Get leaderboard
    lb = await service.get_leaderboard()
    print("\nLeaderboard fetched:")
    for l in lb:
        print(f"[{l['rank']}] {l['name']} (ROI: {l['roi']}%) -> Active: {l['is_active']}")

if __name__ == "__main__":
    asyncio.run(main())
