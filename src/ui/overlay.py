import tkinter as tk
from tkinter import scrolledtext
import pyperclip
import threading
import time
import sys
import os
import logging
import re
from queue import Queue

# Add src to path (한 번만 추가)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.data.collector import MarketDataCollector
from src.data.parser import FinancialParser
from src.agents.analyst import StockAnalyst

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradingOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📊 Trading Assistant")
        self.root.geometry("400x500+100+100")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)
        self.root.configure(bg='#1a1a2e')
        
        # 스타일 설정 (config 사용)
        from src.config import UI_COLORS, UI_FONTS
        self.bg_color = UI_COLORS.get('bg_primary', '#1a1a2e')
        self.fg_color = UI_COLORS.get('fg_primary', '#eaeaea')
        self.accent_color = UI_COLORS.get('accent', '#00d4ff')
        self.font_family = UI_FONTS.get('primary', '맑은 고딕')
        
        self.root.configure(bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=10)
        
        self.label_title = tk.Label(
            header_frame, 
            text="🔍 티커를 복사하세요", 
            font=(self.font_family, 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        self.label_title.pack()
        
        # 신호 프레임
        signal_frame = tk.Frame(self.root, bg='#16213e', padx=10, pady=10)
        signal_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.label_ticker = tk.Label(
            signal_frame, 
            text="대기 중...", 
            font=(self.font_family, 18, "bold"),
            bg='#16213e',
            fg=self.fg_color
        )
        self.label_ticker.pack()
        
        self.label_signal = tk.Label(
            signal_frame, 
            text="--", 
            font=(self.font_family, 16, "bold"),
            bg='#16213e',
            fg='#888888'
        )
        self.label_signal.pack(pady=5)
        
        self.label_score = tk.Label(
            signal_frame, 
            text="점수: --", 
            font=(self.font_family, 12),
            bg='#16213e',
            fg='#888888'
        )
        self.label_score.pack()
        
        # 타임프레임 선택 프레임 (추가)
        tf_frame = tk.Frame(self.root, bg=self.bg_color)
        tf_frame.pack(fill=tk.X, padx=10, pady=2)
        
        self.interval_var = tk.StringVar(value="1d")
        
        intervals = [("15분", "15m"), ("1시간", "60m"), ("일봉", "1d"), ("주봉", "1wk")]
        for text, value in intervals:
            rb = tk.Radiobutton(
                tf_frame, text=text, value=value, variable=self.interval_var,
                bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color,
                activebackground=self.bg_color, activeforeground=self.accent_color,
                font=(self.font_family, 8), command=self.on_interval_change
            )
            rb.pack(side=tk.LEFT, expand=True)

        # 타점 프레임
        entry_frame = tk.Frame(self.root, bg='#0f3460', padx=10, pady=10)
        entry_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            entry_frame, 
            text="📍 매수/매도 타점", 
            font=(self.font_family, 11, "bold"),
            bg='#0f3460',
            fg=self.accent_color
        ).pack(anchor='w')
        
        self.label_entry_points = tk.Label(
            entry_frame, 
            text="티커 복사 후 표시됩니다", 
            font=(self.font_family, 10),
            bg='#0f3460',
            fg='#aaaaaa',
            justify='left'
        )
        self.label_entry_points.pack(anchor='w', pady=5)
        
        # 상세 분석 프레임
        detail_frame = tk.Frame(self.root, bg=self.bg_color)
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(
            detail_frame, 
            text="📋 상세 분석", 
            font=("맑은 고딕", 11, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(anchor='w')
        
        self.text_details = scrolledtext.ScrolledText(
            detail_frame,
            font=(self.font_family, 9),
            bg='#16213e',
            fg=self.fg_color,
            height=12,
            wrap=tk.WORD,
            borderwidth=0
        )
        self.text_details.pack(fill=tk.BOTH, expand=True, pady=5)
        self.text_details.insert(tk.END, "💡 사용 팁:\n• 종목명(예: 삼성전자, 애플) 또는\n• 티커(예: AAPL, 005930.KS)를 복사하세요.\n\n• 분봉/시봉은 최근 60일 데이터만 제공됩니다.\n• 한국 주식 검색 시 종목명이 더 정확할 수 있습니다.")
        self.text_details.config(state=tk.DISABLED)
        
        # 상태 표시
        self.label_status = tk.Label(
            self.root, 
            text="✅ 클립보드 모니터링 중...", 
            font=(self.font_family, 8),
            bg=self.bg_color,
            fg='#666666'
        )
        self.label_status.pack(pady=5)
        
        # State
        self.last_clipboard = ""
        self.queue = Queue()
        
        # Tools - 싱글톤 패턴 사용
        from src.data.storage import get_storage
        self.storage = get_storage()
        self.collector = MarketDataCollector(use_db=True)
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
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Clipboard error: {e}")
                time.sleep(1)

    def is_valid_ticker(self, text):
        """
        유효한 티커 또는 종목명인지 확인
        """
        # 공백 제거
        text = text.strip()
        if not text: return False
        
        # 1. 일반적인 티커 패턴
        if re.match(r'^\d{6}\.(KS|KQ)$', text): return True  # 한국
        if re.match(r'^\d{4}\.[A-Z]{1,2}$', text): return True # 일본
        if re.match(r'^[A-Z]{1,5}$', text): return True      # 미국
        if re.match(r'^[A-Z]{1,5}\.[A-Z]{1,2}$', text): return True # 기타 국제
        
        # 2. 한글 또는 일반 단어 (종목명으로 판단)
        # 한글이 포함되어 있거나 일반 텍스트인 경우 검색 시도 대상으로 간주
        if any(ord('가') <= ord(char) <= ord('힣') for char in text):
            return True
        if len(text) >= 2: # 최소 두 글자 이상
            return True
            
        return False

    def on_interval_change(self):
        """타임프레임 변경 시 현재 티커 재분석"""
        if self.last_clipboard and self.is_valid_ticker(self.last_clipboard):
            self.queue.put(("START", self.last_clipboard))
            threading.Thread(target=self.analyze, args=(self.last_clipboard,)).start()

    def search_ticker(self, query):
        """종목명을 티커로 변환 시도"""
        try:
            import yfinance as yf
            # 한국 주식 우선 검색 (query가 한글인 경우)
            is_korean = any(ord('가') <= ord(char) <= ord('힣') for char in query)
            
            # yfinance search API 사용
            search = yf.Search(query, max_results=5)
            results = search.quotes
            
            if not results:
                return query # 검색 결과 없으면 그대로 반환
            
            # 검색 결과 중 가장 적절한 것 선택
            # 한국 주식 검색 시 .KS 또는 .KQ 우선
            if is_korean:
                for res in results:
                    symbol = res.get('symbol', '')
                    if symbol.endswith('.KS') or symbol.endswith('.KQ'):
                        return symbol
            
            return results[0].get('symbol', query)
        except:
            return query

    def analyze(self, ticker_or_name):
        try:
            # 종목명인 경우 티커로 변환 시도
            self.queue.put(("STATUS", "종목 검색 중..."))
            ticker = self.search_ticker(ticker_or_name)
            
            interval = self.interval_var.get()
            # 타임프레임별 적절한 기간 설정
            period_map = {
                "15m": "60d",
                "60m": "60d",
                "1d": "1y",
                "1wk": "max"
            }
            period = period_map.get(interval, "1y")
            
            # 1. Fetch Data
            self.queue.put(("STATUS", f"{interval} 데이터 수집 중..."))
            price_df = self.collector.get_ohlcv(ticker, period=period, interval=interval)
            
            # 2. Fetch Financials (일봉/주봉일 때만 주로 의미있음)
            financials = self.storage.get_financials(ticker)
            if not financials and interval in ["1d", "1wk"]:
                self.queue.put(("STATUS", "재무 데이터 수집 중..."))
                self.parser.fetch_and_save_financials(ticker)
                financials = self.storage.get_financials(ticker)
            
            if price_df is None or len(price_df) < 5:
                self.queue.put(("ERROR", f"{ticker} 데이터를 찾을 수 없습니다."))
                return
                
            # 3. Run Analysis
            self.queue.put(("STATUS", "패턴 분석 중..."))
            result = self.analyst.analyze_ticker(ticker, price_df, financials)
            
            # 4. AI Report (Hugging Face)
            try:
                from src.agents.ai_analyzer import AIAnalyzer, get_stock_events
                ai = AIAnalyzer()
                events = get_stock_events(ticker)
                result['events'] = events
                
                self.queue.put(("STATUS", "AI 리포트 작성 중..."))
                report = ai.generate_report(result)
                result['full_report'] = report
            except Exception as e:
                logger.warning(f"AI Report failed: {e}")
            
            self.queue.put(("RESULT", result))
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            self.queue.put(("ERROR", f"분석 오류: {str(e)[:50]}"))

    def check_queue(self):
        while not self.queue.empty():
            msg_type, data = self.queue.get()
            
            if msg_type == "START":
                self.label_title.config(text=f"🔍 {data} 분석 중...")
                self.label_ticker.config(text=data, fg=self.accent_color)
                self.label_signal.config(text="분석 중...", fg='#888888')
                self.label_score.config(text="--")
                self.label_entry_points.config(text="계산 중...")
                self.text_details.config(state=tk.NORMAL)
                self.text_details.delete(1.0, tk.END)
                self.text_details.insert(tk.END, "데이터를 수집하고 있습니다...")
                self.text_details.config(state=tk.DISABLED)
                
            elif msg_type == "STATUS":
                self.label_status.config(text=f"⏳ {data}")
                
            elif msg_type == "RESULT":
                res = data
                
                # 신호에 따른 색상
                signal = res['signal']
                if "매수" in signal:
                    color = "#ff4757"  # 한국식 빨간색 = 상승
                elif "매도" in signal:
                    color = "#3742fa"  # 파란색 = 하락
                else:
                    color = "#ffa502"  # 노란색 = 중립
                
                self.label_title.config(text=f"📊 {res['ticker']} 분석 완료")
                self.label_ticker.config(text=res['ticker'], fg=self.fg_color)
                self.label_signal.config(text=signal, fg=color)
                self.label_score.config(text=f"종합 점수: {res['final_score']}/100")
                
                # 타점 표시
                entry = res.get('entry_points', {})
                if entry:
                    entry_text = f"현재가: {entry.get('current_price', 0):,.0f}\n"
                    entry_text += f"1차 매수: {entry.get('buy_target_1', 0):,.0f}\n"
                    entry_text += f"손절가: {entry.get('stop_loss', 0):,.0f}\n"
                    entry_text += f"1차 매도: {entry.get('sell_target_1', 0):,.0f}"
                    self.label_entry_points.config(text=entry_text)
                
                # 상세 분석 표시
                self.text_details.config(state=tk.NORMAL)
                self.text_details.delete(1.0, tk.END)
                self.text_details.insert(tk.END, res.get('full_report', '분석 결과 없음'))
                self.text_details.config(state=tk.DISABLED)
                
                self.label_status.config(text="✅ 분석 완료 - 새 티커를 복사하세요")
                
            elif msg_type == "ERROR":
                self.label_title.config(text="❌ 오류 발생")
                self.label_signal.config(text="--", fg='#888888')
                self.text_details.config(state=tk.NORMAL)
                self.text_details.delete(1.0, tk.END)
                self.text_details.insert(tk.END, f"오류: {data}")
                self.text_details.config(state=tk.DISABLED)
                self.label_status.config(text="❌ 오류 - 다시 시도하세요")

        self.root.after(100, self.check_queue)

if __name__ == "__main__":
    overlay = TradingOverlay()
