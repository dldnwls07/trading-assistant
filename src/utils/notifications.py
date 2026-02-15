import logging
import aiohttp
import asyncio
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class DiscordNotifier:
    """
    Async Discord Webhook Notifier.
    Uses aiohttp to prevent blocking the main thread during network requests.
    """
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
        self._session: Optional[aiohttp.ClientSession] = None
        
        if not self.webhook_url:
            logger.warning("⚠️ Discord Webhook URL not set. Notifications will be skipped.")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Reuse aiohttp session for better performance"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Cleanup session resource"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def send_message(self, content: str, title: str = "🚨 Trading Alert", color: int = 3447003, fields: list = None):
        """
        Sends a message to Discord asynchronously.
        
        Args:
            content: Main body text
            title: Embed title
            color: Sidebar color (Decimal color code, e.g. 3447003=Blue, 15158332=Red, 3066993=Green)
            fields: List of dicts for key-value pairs [{"name": "Price", "value": "100", "inline": True}]
        """
        if not self.webhook_url:
            return False
            
        embed = {
            "title": title,
            "description": content,
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "footer": {"text": "🤖 AI Trading Assistant v2.1 (Async)"}
        }
        
        if fields:
            embed["fields"] = fields
            
        payload = {"embeds": [embed]}
        
        # Fire-and-forget pattern using asyncio.create_task is safer for high-frequency loops,
        # but here we await to ensure delivery in critical paths. 
        # For non-critical logs, you can wrap this call in asyncio.create_task() at the caller side.
        try:
            session = await self._get_session()
            async with session.post(self.webhook_url, json=payload) as response:
                if 200 <= response.status < 300:
                    return True
                else:
                    logger.error(f"❌ Discord API Error: {response.status} - {await response.text()}")
                    return False
        except Exception as e:
            logger.error(f"❌ Failed to send Discord alert: {e}")
            return False

# Global instance for easy access
_notifier_instance = None

def get_notifier() -> DiscordNotifier:
    global _notifier_instance
    if _notifier_instance is None:
        _notifier_instance = DiscordNotifier()
    return _notifier_instance

async def send_alert(message: str, title: str = "🚨 Trading Alert"):
    """
    Global helper helper for one-off alerts.
    Note: For frequent usage, instantiate DiscordNotifier and reuse it.
    """
    notifier = get_notifier()
    await notifier.send_message(content=message, title=title)

