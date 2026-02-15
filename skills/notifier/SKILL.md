---
name: Notifier Expert
description: Expert guidelines for implementing async, non-blocking notification systems in the trading bot.
version: 1.1.0
---

# 🔔 Notifier Expert Skill (Project Specific)

<role>
You are a **System Reliability Engineer** responsible for the project's alert system.
Your goal is to transition the current synchronous notification system to a **fully asynchronous** architecture to prevent blocking critical trading loops.
</role>

<current_status>
- **Existing Module**: `src/utils/notifications.py`
- **Issue**: Uses `requests` (blocking I/O). If Discord API is slow, the entire bot freezes.
- **Goal**: Refactor to use `aiohttp` for non-blocking execution.
</current_status>

<core_principles>
1.  **Async-First**: 
    -   All notification functions MUST be `async def`.
    -   Use `aiohttp.ClientSession` instead of `requests`.

2.  **Fire-and-Forget (Background Tasks)**:
    -   Notifications should not delay the return of an API response.
    -   Use `asyncio.create_task()` to send alerts in the background.

3.  **Rich Formatting**:
    -   Use **Embeds** for trade signals (Green for Buy, Red for Sell).
    -   Include critical context: Time, Symbol, Price, Strategy Name.

4.  **Error Handling**:
    -   If Discord is down, log the error and **continue operation**.
    -   Do not let a failed notification crash the trading bot.
</core_principles>

<implementation_guide>
### Recommended Async Pattern
```python
# src/utils/notifications.py (Refactored)

import aiohttp
import logging
import asyncio

logger = logging.getLogger(__name__)

class AsyncDiscordNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send(self, content: str, embed: dict = None):
        if not self.webhook_url:
            return
            
        payload = {"content": content, "embeds": [embed] if embed else []}
        
        # Don't wait for response, just fire
        asyncio.create_task(self._post(payload))

    async def _post(self, payload: dict):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as resp:
                    if resp.status >= 400:
                        logger.error(f"Discord Value Error: {resp.status}")
        except Exception as e:
            logger.error(f"Discord Network Error: {e}")
```
</implementation_guide>
