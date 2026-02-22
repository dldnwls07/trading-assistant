import logging
import time
import os
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

import google.generativeai as genai
import json

from src.agents.core.analyst import StockAnalyst
from src.agents.analysis.screener import StockScreener
from src.agents.execution.executor import OrderExecutor
from src.data.storage import get_storage
from src.utils.notifications import send_alert
from src.agents.event_calendar_api.event_calendar import EventCalendar

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auto-trader")

class AutoTrader:
    """
    자율 주행 AI 트레이더
    - 스크리너를 통해 유망 종목 발굴
    - 분석 엔진을 통해 매수/매도 타이밍 결정
    - 실행 에이전트를 통해 자동 주문 (가상/실전)
    """
    
    def __init__(self):
        self.analyst = StockAnalyst()
        self.screener = StockScreener(analyst=self.analyst)
        self.executor = OrderExecutor()
        self.storage = get_storage()
        self.calendar = EventCalendar()
        
        # Gemini 설정
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
                
                # 사용 가능한 모델 자동 탐색
                model_name = 'gemini-1.5-flash'
                try:
                    available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    if any('gemini-1.5-flash' in m for m in available):
                        model_name = 'gemini-1.5-flash'
                    elif available:
                        model_name = available[0]
                except:
                    pass
                
                self.model = genai.GenerativeModel(model_name)
                logger.info(f"AutoTrader AI 활성화: {model_name}")
            except Exception as e:
                self.model = None
                logger.warning(f"AutoTrader Gemini 초기화 실패: {e}")
        
        # 설정 로드
        self.target_market = os.getenv("TARGET_MARKET", "US")  # US 또는 KR
        self.trade_interval = int(os.getenv("TRADE_INTERVAL", "3600"))  # 기본 1시간
        self.min_score = int(os.getenv("MIN_BUY_SCORE", "75"))  # 매수 최소 점수
        self.sell_score = int(os.getenv("SELL_SCORE", "45"))   # 매도 점수

    async def _get_macro_risk(self) -> Dict[str, Any]:
        """현재 시장의 거시 경제 리스크 상태를 가져옵니다."""
        try:
            return await self.calendar.calculate_event_risk(days_ahead=2)
        except Exception as e:
            logger.error(f"Error getting macro risk: {e}")
            return {"impact_score": 0.0, "is_fomc_week": False, "critical_events": [], "event_count": 0}

    async def run_once(self):
        """1회 트레이딩 루틴 실행 (비동기)"""
        logger.info(f"자율 트레이딩 루틴 시작: {datetime.now()}")
        try:
            await self.storage.initialize()
            await self._check_and_sell()
            await self._check_and_buy()
        except Exception as e:
            logger.error(f"Auto trading error: {e}")

    async def _check_and_sell(self):
        """보유 종목 분석 후 매도 결정 (비동기)"""
        positions = await self.storage.get_virtual_positions()
        if not positions:
            logger.info("보유 종목 없음.")
            return

        from src.utils.market_utils import is_market_open, get_market_time

        for pos in positions:
            ticker = pos['ticker']
            
            # 장 시간 체크
            if not is_market_open(ticker):
                logger.info(f"Skipping SELL analysis for {ticker}: Market is closed.")
                continue
                
            logger.info(f"보유 종목 분석 중: {ticker}")
            # screener._fetch_data가 비동기로 변경됨
            daily_df = await self.screener._fetch_data(ticker, period="1y")
            if daily_df is None: continue
            
            # 매크로 리스크 확인
            macro_risk = await self._get_macro_risk()
            impact_score = macro_risk.get('impact_score', 0)

            analysis = self.analyst.analyze_ticker(ticker, daily_df)
            market_time = get_market_time(ticker)
            decision = await self._get_ai_decision(ticker, daily_df, analysis, mode="SELL", market_time=market_time, macro_risk=macro_risk)
            
            # [Macro-Aware] 리스크 점수가 높을 경우 매도 기준 강화 (평소보다 낮은 점수에서도 매도 고려)
            action = decision.get("action")
            if impact_score > 0.7 and action == "HOLD":
                 # AI가 HOLD라고 했더라도 기술적 점수가 불안정(예: 55점 이하)하면 리스크 관리 차원에서 매도 유도 가능
                 # 여기서는 AI의 판단을 존중하되 프롬프트에서 이미 리스크를 고려하도록 유도함
                 pass

            if action == "SELL":
                current_price = float(daily_df['Close'].iloc[-1])
                avg_price = float(pos.get('avg_price', current_price))
                profit_rate = ((current_price - avg_price) / avg_price) * 100 if avg_price > 0 else 0
                
                reason = decision.get("reason", "AI 판단 매도")
                logger.info(f"🚨 AI 매도 결정: {ticker} | 수익률: {profit_rate:.2f}% | 이유: {reason}")
                
                profit_emoji = "📈" if profit_rate >= 0 else "📉"
                alert_msg = (
                    f"🤖 **AI의 매도 분석**: {reason}\n"
                    f"💰 **수익률**: {profit_emoji} `{profit_rate:.2f}%`\n"
                    f"⏰ **분석 시간**: {market_time}"
                )
                
                await send_alert(alert_msg, title=f"AI Decision: {ticker} SELL")
                await self.executor.execute_trade(ticker, 'SELL', pos['quantity'], current_price)

    async def _check_and_buy(self):
        """AI 판단 매수 종목 발굴 (비동기)"""
        balance = await self.storage.get_virtual_balance()
        if balance < 100000: return

        from src.utils.market_utils import is_market_open, get_market_time
        
        # 매크로 리스크 확인
        macro_risk = await self._get_macro_risk()
        impact_score = macro_risk.get('impact_score', 0)
        critical_events = macro_risk.get('critical_events', [])
        
        # [Macro-Aware] 중대 지표(Critical) 발표 직전인 경우 신규 매수 전면 중단
        if critical_events:
            logger.info(f"⚠️ 매크로 리스크 감지: {critical_events}. 신규 매수를 관망합니다.")
            return

        # screener.get_recommendations가 비동기로 변경됨
        recommendations = await self.screener.get_recommendations(style="momentum", market=self.target_market, limit=5)
        
        for rec in recommendations['recommendations']:
            ticker = rec['ticker']
            
            # 장 시간 체크
            if not is_market_open(ticker):
                logger.info(f"Skipping BUY analysis for {ticker}: Market is closed.")
                continue
                
            positions = await self.storage.get_virtual_positions()
            if any(p['ticker'] == ticker for p in positions): continue
            
            # _fetch_data가 비동기로 변경됨
            daily_df = await self.screener._fetch_data(ticker, period="1y")
            analysis = self.analyst.analyze_ticker(ticker, daily_df)
            market_time = get_market_time(ticker)
            decision = await self._get_ai_decision(ticker, daily_df, analysis, mode="BUY", market_time=market_time, macro_risk=macro_risk)
            
            if decision.get("action") == "BUY":
                price = rec['current_price']
                
                # [Macro-Aware] 리스크 점수가 High(0.5 초과)인 경우 비중 50% 축소
                quantity = await self.executor.calculate_position_size(ticker, price)
                if impact_score > 0.5:
                    logger.info(f"📉 매크로 리스크(점수: {impact_score})로 인해 주문 비중을 50% 축소합니다.")
                    quantity = int(quantity * 0.5)

                reason = decision.get("reason", "AI 추천 매수")
                
                if quantity > 0:
                    risk_msg = f" (⚠️ 리스크 점수 {impact_score}로 비중 축소)" if impact_score > 0.5 else ""
                    logger.info(f"🎯 AI 최종 승인 완료: {ticker} | 이유: {reason}{risk_msg}")
                    
                    buy_msg = (
                        f"🎯 **AI의 매수 판단 근거**:\n{reason}\n"
                        f"💵 **예상 매수가**: `{price:,.2f}`\n"
                        f"📊 **수량**: `{quantity}주`\n"
                        f"⏰ **분석 시간**: {market_time}{risk_msg}"
                    )
                    
                    await send_alert(buy_msg, title=f"AI Approved: {ticker} BUY")
                    await self.executor.execute_trade(ticker, 'BUY', quantity, price)
                    break

    async def _get_ai_decision(self, ticker: str, df: pd.DataFrame, analysis: Dict, mode: str = "BUY", market_time: str = "", macro_risk: Dict = None) -> Dict:
        """Gemini AI 최종 투자 판단 요청 (비동기)"""
        if not self.model:
            score = analysis.get('final_score', 50)
            # 기본 점수 기준
            buy_threshold = self.min_score
            sell_threshold = self.sell_score
            
            # [Macro-Aware] 매크로 리스크에 따른 임계치 자동 조정 (AI 모델 없을 때 대비)
            if macro_risk:
                impact = macro_risk.get('impact_score', 0)
                if impact > 0.5:
                    buy_threshold += 10 # 매수 기준 강화
                    sell_threshold += 5 # 더 빨리 매도
            
            if mode == "BUY" and score >= buy_threshold: return {"action": "BUY"}
            if mode == "SELL" and score <= sell_threshold: return {"action": "SELL"}
            return {"action": "HOLD"}

        try:
            context = {
                "ticker": ticker, 
                "current_price": float(df['Close'].iloc[-1]),
                "market_time": market_time,
                "technical_score": analysis.get('final_score'), 
                "signal": analysis.get('signal'),
                "regime": analysis.get('market_regime'),
                "patterns": [p['name'] for p in analysis.get('patterns', [])[:3]],
                "rsi": float(analysis.get('daily_analysis', {}).get('rsi_value', 50)),
                "mode": mode,
                "macro_risk": macro_risk # 매크로 컨텍스트 추가
            }

            prompt = f"""
            너는 전문 퀀트 트레이더야. 아래 주식 데이터와 현재 거시 경제 리스크 상황을 보고 {mode} 여부를 결정해줘.
            데이터: {json.dumps(context, ensure_ascii=False)}
            
            [매크로 리스크 지침]
            1. macro_risk의 impact_score가 높거나 critical_events가 있다면 매우 보수적으로 판단해.
            2. 큰 지표 발표(CPI, FOMC 등)를 앞두고 있다면 확실한 기술적 우위가 없을 시 "HOLD"를 선택해.
            3. 매도(SELL) 모드일 때 매크로 리스크가 높다면 선제적 수익 실현을 긍정적으로 검토해.

            [공통 지침]
            1. 매우 보수적으로 판단해. 확실한 근거가 없으면 "HOLD"를 선택해.
            2. 응답은 반드시 JSON 형식으로만 보내: {{"action": "BUY" 또는 "SELL" 또는 "HOLD", "reason": "한 문장으로 요약된 이유"}}
            3. 기술적 지표와 시장 국면(Regime), 그리고 거시 경제 리스크를 연계해서 생각해서 답해줘.
            """
            
            # generate_content_async 사용 (비동기 지원 시)
            response = await self.model.generate_content_async(prompt)
            raw_text = response.text.strip()
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            return json.loads(raw_text)
        except Exception as e:
            logger.error(f"AI Decision Error: {e}")
            return {"action": "HOLD", "reason": f"AI 추론 오류: {e}"}

async def start_auto_trading():
    """무한 루프 실행 (비동기)"""
    import asyncio
    trader = AutoTrader()
    # await send_alert("🤖 AI 자율 트레이딩 워커(Async)가 시작되었습니다!", title="AutoTrader Start")
    logger.info("🤖 AI 자율 트레이딩 워커(Async)가 시작되었습니다!")
    
    while True:
        await trader.run_once()
        logger.info(f"다음 루틴까지 {trader.trade_interval}초 대기...")
        await asyncio.sleep(trader.trade_interval)

if __name__ == "__main__":
    import asyncio
    asyncio.run(start_auto_trading())
