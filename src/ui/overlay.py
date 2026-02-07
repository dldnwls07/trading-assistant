import tkinter as tk
import pyperclip
import threading
import time
import sys
import os
import logging
from queue import Queue

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.collector import MarketDataCollector
from src.data.storage import DataStorage
from src.data.parser import FinancialParser
from src.agents.analyst import StockAnalyst

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradingOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Trading Assistant")
        self.root.geometry("300x150+100+100")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.9) # Slight transparency
        
        # UI Elements
        self.label_ticker = tk.Label(self.root, text="대기 중...", font=("맑은 고딕", 16, "bold"))
        self.label_ticker.pack(pady=5)
        
        self.label_signal = tk.Label(self.root, text="--", font=("맑은 고딕", 14))
        self.label_signal.pack()
        
        self.label_score = tk.Label(self.root, text="점수: --", font=("맑은 고딕", 10))
        self.label_score.pack(pady=2)
        
        self.label_info = tk.Label(self.root, text="티커를 복사하여 분석하세요", font=("맑은 고딕", 8))
        self.label_info.pack(pady=5)
        
        # State
        self.last_clipboard = ""
        self.queue = Queue()
        
        # Tools
        self.collector = MarketDataCollector(use_db=True)
        self.storage = DataStorage("trading_assistant.db")
        self.parser = FinancialParser(use_db=True)
        self.analyst = StockAnalyst()
        
        # Start Threads
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_clipboard)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        # Start UI Loop
        self.check_queue()
        self.root.mainloop()
        
    def monitor_clipboard(self):
        while self.running:
            try:
                content = pyperclip.paste().strip().upper()
                if content != self.last_clipboard:
                    self.last_clipboard = content
                    if self.is_valid_ticker(content):
                        self.queue.put(("START", content))
                        self.analyze(content)
                time.sleep(1)
            except Exception as e:
                logger.error(f"Clipboard error: {e}")
                time.sleep(1)

    def is_valid_ticker(self, text):
        # Simple validation: 1-5 alpha chars
        return text.isalpha() and 1 <= len(text) <= 5

    def analyze(self, ticker):
        try:
            # 1. Fetch Data
            price_df = self.collector.get_daily_ohlcv(ticker, period="1y")
            # Financials usually need explicit run if not cached, 
            # for now assume verify_parser run or implementing auto-fetch in parser
            # But let's check storage first
            financials = self.storage.get_financials(ticker)
            if not financials:
                self.queue.put(("INFO", "재무 데이터 수집 중..."))
                self.parser.fetch_and_save_financials(ticker)
                financials = self.storage.get_financials(ticker)
            
            if price_df is None:
                self.queue.put(("ERROR", "데이터 없음"))
                return
                
            # 2. Run Analysis
            result = self.analyst.analyze_ticker(ticker, price_df, financials)
            self.queue.put(("RESULT", result))
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            self.queue.put(("ERROR", "Error"))

    def check_queue(self):
        while not self.queue.empty():
            msg_type, data = self.queue.get()
            
            if msg_type == "START":
                self.label_ticker.config(text=f"{data} 분석 중...", fg="blue")
                self.label_signal.config(text="--")
                self.label_score.config(text="--")
                
            elif msg_type == "RESULT":
                res = data
                color = "black"
                if "BUY" in res['signal'] or "매수" in res['signal']: color = "red" # Korean Stock Color (Red=Up)
                elif "SELL" in res['signal'] or "매도" in res['signal']: color = "blue" # Korean Stock Color (Blue=Down)
                
                self.label_ticker.config(text=res['ticker'], fg="black")
                self.label_signal.config(text=res['signal'], fg=color)
                self.label_score.config(text=f"점수: {res['final_score']}")
                self.label_info.config(text=res['technical']['summary'][:40] + "...")
                
            elif msg_type == "ERROR":
                self.label_ticker.config(text="오류", fg="red")
                self.label_info.config(text=data)
                
            elif msg_type == "INFO":
                self.label_info.config(text=data)

        self.root.after(100, self.check_queue)

if __name__ == "__main__":
    overlay = TradingOverlay()
