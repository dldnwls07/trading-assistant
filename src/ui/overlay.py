import tkinter as tk
from tkinter import scrolledtext
import pyperclip
import threading
import time
import sys
import os
import logging
import re
from datetime import datetime

# 윈도우 콘솔 한글/이모지 인코딩 문제 해결
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# sys path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.data.collector import MarketDataCollector
from src.agents.analyst import StockAnalyst
from src.agents.ai_analyzer import AIAnalyzer
from src.data.storage import get_storage

# Setup logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradingOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Premium Trading Assistant")
        self.root.geometry("400x600+100+100")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.98)
        
        # Premium Colors (Navy & Cyan)
        self.bg_color = '#0f172a'      
        self.card_color = '#1e293b'    
        self.accent_color = '#06b6d4'  
        self.text_primary = '#f8fafc'  
        self.text_secondary = '#94a3b8' 
        
        self.root.configure(bg=self.bg_color)
        
        # Main Layout
        self._setup_ui()
        
        # Shared State
        self.last_clipboard = ""
        self.is_analyzing = False
        
        # Backend Components
        self.storage = get_storage()
        self.collector = MarketDataCollector(use_db=True)
        self.analyst = StockAnalyst()
        self.ai_analyzer = AIAnalyzer()
        
        # Start Clipboard Monitor
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Premium Trading Assistant UI Initialized")

    def _setup_ui(self):
        main_container = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        # 1. Header
        header_frame = tk.Frame(main_container, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.label_ticker = tk.Label(
            header_frame, 
            text="READY TO ANALYZE", 
            font=("Inter", 20, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        self.label_ticker.pack(anchor='w')
        
        # 2. Score Badge
        self.score_frame = tk.Frame(main_container, bg=self.card_color, padx=15, pady=15)
        self.score_frame.pack(fill=tk.X, pady=10)
        
        self.label_signal = tk.Label(
            self.score_frame, 
            text="종목 코드를 복사하세요", 
            font=("Inter", 14, "bold"),
            bg=self.card_color,
            fg=self.text_primary
        )
        self.label_signal.pack()
        
        self.label_score = tk.Label(
            self.score_frame, 
            text="AI 분석 확률: --%", 
            font=("Inter", 10),
            bg=self.card_color,
            fg=self.text_secondary
        )
        self.label_score.pack(pady=(5, 0))

        # 3. Entry Points Card
        entry_card = tk.LabelFrame(
            main_container, 
            text=" AI TRADING GUIDE ", 
            font=("Inter", 9, "bold"),
            bg=self.bg_color,
            fg=self.text_secondary,
            padx=15,
            pady=15,
            labelanchor='n'
        )
        entry_card.pack(fill=tk.X, pady=15)
        
        self.label_entry_points = tk.Label(
            entry_card, 
            text="📍 매수가: --\n🎯 목표가: --\n🛡️ 손절가: --", 
            font=("Inter", 10),
            bg=self.bg_color,
            fg=self.text_primary,
            justify='left'
        )
        self.label_entry_points.pack(fill=tk.X)

        # 4. AI Report Area
        tk.Label(
            main_container, 
            text="📝 SMART ANALYSIS REPORT", 
            font=("Inter", 9, "bold"),
            bg=self.bg_color,
            fg=self.text_secondary
        ).pack(anchor='w', pady=(10, 5))
        
        self.text_details = scrolledtext.ScrolledText(
            main_container,
            font=("Inter", 10),
            bg=self.card_color,
            fg=self.text_primary,
            height=12,
            padx=10,
            pady=10,
            borderwidth=0,
            highlightthickness=0,
            wrap=tk.WORD
        )
        self.text_details.pack(fill=tk.BOTH, expand=True)
        self.text_details.insert(tk.END, "복사된 종목에 대해 실시간 AI 분석을 수행합니다.\n(예: 애플, 삼성전자, NVDA 등)")
        self.text_details.config(state=tk.DISABLED)
        
        # 5. Status Bar
        self.label_status = tk.Label(
            self.root, 
            text="● Brain Active", 
            font=("Inter", 8),
            bg=self.bg_color,
            fg='#10b981'
        )
        self.label_status.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

    def monitor_clipboard(self):
        while self.running:
            try:
                content = pyperclip.paste().strip()
                if content and content != self.last_clipboard:
                    self.last_clipboard = content
                    if self.is_valid_ticker(content):
                        # Start analysis in a separate thread
                        threading.Thread(target=self.run_full_analysis, args=(content,), daemon=True).start()
                time.sleep(1.0)
            except Exception as e:
                logger.error(f"Clipboard monitor error: {e}")
                time.sleep(2.0)

    def is_valid_ticker(self, text):
        if not text or len(text) > 30: return False
        # Ticket pattern or Korean name
        if re.match(r'^[A-Z0-9.]{2,10}$', text.upper()): return True
        if any(ord('가') <= ord(char) <= ord('힣') for char in text): return True
        return False

    def search_ticker(self, query):
        """Map name to ticker (KR priority)"""
        try:
            import yfinance as yf
            is_korean = any(ord('가') <= ord(char) <= ord('힣') for char in query)
            search = yf.Search(query, max_results=5)
            results = search.quotes
            if not results: return query
            
            if is_korean:
                for res in results:
                    sym = res.get('symbol', '')
                    if sym.endswith('.KS') or sym.endswith('.KQ'): return sym
            return results[0].get('symbol', query)
        except:
            return query

    def run_full_analysis(self, raw_input):
        if self.is_analyzing: return
        self.is_analyzing = True
        
        try:
            # 1. Ticker Mapping
            ticker = self.search_ticker(raw_input)
            self._update_status(f"Analysing {ticker}...", "#38bdf8")
            
            # 2. Data Fetch
            daily_df = self.collector.get_ohlcv(ticker, period="1y", interval="1d")
            hourly_df = self.collector.get_ohlcv(ticker, period="60d", interval="60m")
            
            if daily_df is None:
                self._report_error(f"Data not found for {ticker}")
                return

            # 3. Smart Analysis
            financials = self.storage.get_financials(ticker)
            analysis_res = self.analyst.analyze_ticker(ticker, daily_df, financials, hourly_df)
            
            # 4. AI Report
            report = self.ai_analyzer.generate_report(analysis_res)
            analysis_res['full_report'] = report
            
            # 5. UI Update
            self.root.after(0, lambda: self._apply_results(analysis_res))
            
        except Exception as e:
            logger.error(f"Analysis loop error: {e}")
            self._report_error(str(e))
        finally:
            self.is_analyzing = False

    def _update_status(self, text, color):
        self.root.after(0, lambda: self.label_status.config(text=f"● {text}", fg=color))
        self.root.after(0, lambda: self.label_ticker.config(text=f"🔍 {text.split()[1] if ' ' in text else text}"))

    def _apply_results(self, res):
        ticker = res['ticker']
        score = res['final_score']
        signal = res['signal']
        report = res.get('full_report', "Report generation failed.")
        
        # Colors based on score
        sig_color = '#ef4444' if score < 40 else ('#10b981' if score > 60 else self.text_primary)
        
        self.label_ticker.config(text=ticker)
        self.label_signal.config(text=signal, fg=sig_color)
        self.label_score.config(text=f"AI 분석 신뢰도: {score}%")
        
        # Entry points
        eps = res.get('entry_points', {})
        et = f"📍 매수가: {eps.get('buy', 'N/A')}\n🎯 목표가: {eps.get('target', 'N/A')}\n🛡️ 손절가: {eps.get('stop', 'N/A')}"
        self.label_entry_points.config(text=et)
        
        # Report
        self.text_details.config(state=tk.NORMAL)
        self.text_details.delete(1.0, tk.END)
        self.text_details.insert(tk.END, report)
        self.text_details.config(state=tk.DISABLED)
        
        self.label_status.config(text="● Analysis Complete", fg='#10b981')

    def _report_error(self, msg):
        self.root.after(0, lambda: self.label_ticker.config(text="ERROR"))
        self.root.after(0, lambda: self.label_signal.config(text="NO DATA FOUND", fg='#ef4444'))
        self.root.after(0, lambda: self.label_status.config(text="● Error Stopped", fg='#ef4444'))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TradingOverlay()
    app.run()
