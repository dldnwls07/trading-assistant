import os
from src.data.collector import MarketDataCollector
from src.data.storage import get_storage
from src.data.parser import FinancialParser
from src.agents.core.analyst import StockAnalyst
from src.agents.analysis.ai_analyzer import AIAnalyzer
from src.agents.chat.chat_assistant import ChatAssistant
from src.agents.calendar.event_calendar import EventCalendar
from src.agents.analysis.portfolio_analyzer import PortfolioAnalyzer
from src.agents.analysis.screener import StockScreener
from src.agents.core.chartist import ChartMaster
from slowapi import Limiter
from slowapi.util import get_remote_address

# === 전역 인스턴스 (싱글톤) ===
storage = get_storage()
collector = MarketDataCollector(use_db=True)
parser = FinancialParser(use_db=True)
analyst = StockAnalyst()
ai_analyzer = AIAnalyzer()

# 신규 기능 인스턴스
chat_assistant = ChatAssistant(gemini_api_key=os.getenv("GEMINI_API_KEY"))
event_calendar = EventCalendar()
portfolio_analyzer = PortfolioAnalyzer()
screener = StockScreener()
chart_master = ChartMaster()

# === Rate Limiting (DoS Protection) ===
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
