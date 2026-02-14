from datetime import datetime
import requests
import json
import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class DiscordNotifier:
    """디스코드 웹훅을 통한 알림 시스템"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
        
    def send_message(self, content: str, title: str = "🚨 Trading Alert", color: int = 3447003):
        """디스코드 채널로 메시지 전송"""
        if not self.webhook_url:
            logger.warning("Discord Webhook URL not set. Alert not sent.")
            return False
            
        payload = {
            "embeds": [
                {
                    "title": title,
                    "description": content,
                    "color": color,
                    "timestamp": datetime.now().isoformat(),
                    "footer": {"text": "AI Trading Assistant v2.0"}
                }
            ]
        }
        
        try:
            response = requests.post(
                self.webhook_url, 
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")
            return False

def send_alert(message: str, title: str = "🚨 Trading Alert"):
    """전역 알림 함수"""
    notifier = DiscordNotifier()
    return notifier.send_message(message, title)
