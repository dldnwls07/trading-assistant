"""
AI 분석 모듈 - Hugging Face 연동
금융 감성 분석 + 전문가급 리포트 생성
"""
import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

from src.config import HF_TOKEN, GEMINI_API_KEY, GROQ_API_KEY
import requests
import json

class AIAnalyzer:
    """
    Hugging Face API를 활용한 AI 분석기
    - FinBERT: 금융 뉴스 감성 분석
    - LLM: 전문가 리포트 생성
    """
    
    def __init__(self):
        self.hf_token = HF_TOKEN
        self.gemini_key = GEMINI_API_KEY
        self.groq_key = GROQ_API_KEY
        self.client = None
        
        if self.hf_token and self.hf_token != "여기에_발급받은_토큰을_입력하세요":
            try:
                from huggingface_hub import InferenceClient
                self.client = InferenceClient(token=self.hf_token)
                logger.info("Hugging Face API 연결 성공")
            except Exception as e:
                logger.warning(f"Hugging Face 연결 실패: {e}")
        else:
            logger.warning("HF_TOKEN이 설정되지 않았습니다. AI 분석 기능이 제한됩니다.")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        FinBERT를 사용한 금융 뉴스 감성 분석
        Returns: {"label": "positive/negative/neutral", "score": 0.0-1.0}
        """
        if not self.client:
            return {"label": "unknown", "score": 0.0, "error": "API 미연결"}
        
        try:
            # FinBERT 모델 사용
            result = self.client.text_classification(
                text,
                model="ProsusAI/finbert"
            )
            
            if result:
                top = result[0]
                return {
                    "label": top.get("label", "unknown"),
                    "score": round(top.get("score", 0.0), 3)
                }
        except Exception as e:
            logger.error(f"감성 분석 오류: {e}")
        
        return {"label": "unknown", "score": 0.0}
    
    def generate_report(self, analysis_data: Dict[str, Any], lang: str = "ko") -> str:
        """
        30여 가지 정밀 데이터를 바탕으로 AI가 스스로 판단하여 전문가급 투자 리포트 생성
        lang: ko, en, zh, ja 지원
        """
        if not self.client:
            return self._generate_fallback_report(analysis_data)
        
        ticker = analysis_data.get("ticker", "UNKNOWN")
        score = analysis_data.get("final_score", 50)
        signal = analysis_data.get("signal", "중립")
        
        # 다중 시간 프레임 데이터
        short = analysis_data.get("short_term", {})
        medium = analysis_data.get("medium_term", {})
        long = analysis_data.get("long_term", {})
        consensus = analysis_data.get("consensus", {})
        
        # 기타 가용 데이터
        fund = analysis_data.get("fundamental", {})
        macro = analysis_data.get("macro", {})
        vol_price = analysis_data.get("volume_price", {})
        psych = analysis_data.get("psychology", {})
        events = analysis_data.get("events", {})
        patterns = analysis_data.get("all_patterns", [])

        # 언어별 페르소나 설정
        lang_map = {
            "ko": "시니어 퀀트 애널리스트 (한국어)",
            "en": "Senior Quant Analyst (English)",
            "zh": "资深量化分析师 (Chinese)",
            "ja": "シニアクオンツアナリスト (Japanese)"
        }
        persona = lang_map.get(lang, lang_map["ko"])

        scenarios = analysis_data.get("price_scenarios", {})
        
        prompt = f"""You are a {persona} with 15 years of experience.
Analyze following 30+ precision data points and generate a strategic report in {lang}.
Do NOT just list the data. INTERPRET them and JUDGE what is most critical.

[Target Symbol] {ticker}
[AI Confidence] {score}/100 | Opinion: {signal}

[Detailed Multi-Layer Data]
1. Short-Term (Snapshot: 1 month): Score {short.get('score', 'N/A')}, Momentum {short.get('specialized_insights', {}).get('quick_momentum', {}).get('momentum', 'N/A')}, RSI {short.get('full_analysis', {}).get('rsi', 'N/A')}
2. Mid-Term (Snapshot: 6 months): Score {medium.get('score', 'N/A')}, Zone {medium.get('specialized_insights', {}).get('swing_zones', {}).get('zone', 'N/A')}, Trend {medium.get('specialized_insights', {}).get('trend_strength', {}).get('strength', 'N/A')}
3. Long-Term (1 year+): Score {long.get('score', 'N/A')}, Phase {long.get('specialized_insights', {}).get('accumulation_phase', {}).get('phase', 'N/A')}, 52W Trend {long.get('specialized_insights', {}).get('long_term_trend', {}).get('trend', 'N/A')}
4. Fundamentals: {fund.get('summary', 'N/A')}, Market Cap {events.get('market_cap', 'N/A')}, Sector {events.get('sector', 'N/A')}
5. Macro/Sentiment: Correlation {macro.get('score', 'N/A')}, OBV energy {vol_price.get('score', 'N/A')}, Psychological disparity {psych.get('score', 'N/A')}
6. Patterns: {len(patterns)} patterns detected. {patterns[0]['name'] if patterns else 'None'}
7. Future Events & Scenarios: 
   - Upcoming Events: {events.get('earnings_date', 'N/A')}, Ex-Div {events.get('ex_dividend_date', 'N/A')}
   - Bearish Scenario: {scenarios.get('bearish', 'N/A')}
   - Bullish Scenario: {scenarios.get('bullish', 'N/A')}

Instructions:
1. 'Critical Insight': Pick the TOP 3 most important indicators.
2. 'Event Impact': Analyze how the upcoming events (if any) might change the current trend.
3. 'Scenario Planning': Based on the Bearish/Bullish scenarios provided, give specific advice for both cases.
4. 'Trading Plan': Give precise Entry/Target points based on the consensus.
5. 'Risk Alert': What is the single biggest risk today?

Write in a professional, decisive tone in {lang}."""

        try:
            # 1. 시도: Gemini API (가장 강력한 무료)
            if self.gemini_key:
                return self._generate_with_gemini(prompt)
            
            # 2. 시도: Groq API (가장 빠른 무료)
            if self.groq_key:
                return self._generate_with_groq(prompt)

            # 3. 시도: Hugging Face (기존 방식)
            if self.client:
                response = self.client.text_generation(
                    prompt,
                    model="microsoft/Phi-3-mini-4k-instruct",
                    max_new_tokens=800,
                    temperature=0.7
                )
                if response: return response.strip()
        except Exception as e:
            logger.error(f"AI Report generation failed: {e}")
        
        return self._generate_fallback_report(analysis_data)
    
    def _generate_with_gemini(self, prompt: str) -> str:
        """Google Gemini 1.5 API 사용"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            response = requests.post(url, headers=headers, json=data)
            res_json = response.json()
            if 'candidates' not in res_json:
                logger.error(f"Gemini API Error: {res_json}")
                raise KeyError(f"Missing 'candidates' in Gemini response: {res_json}")
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception as e:
            logger.warning(f"Gemini API failed: {e}")
            raise e

    def _generate_with_groq(self, prompt: str) -> str:
        """Groq API (Llama-3-70B) 사용"""
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5
            }
            response = requests.post(url, headers=headers, json=data)
            res_json = response.json()
            return res_json['choices'][0]['message']['content'].strip()
        except Exception as e:
            logger.warning(f"Groq API failed: {e}")
            raise e
    
    def _generate_fallback_report(self, analysis_data: Dict[str, Any]) -> str:
        """AI API 실패 시 규칙 기반 리포트 생성 (전문가급 상세 버전)"""
        ticker = analysis_data.get("ticker", "UNKNOWN")
        score = analysis_data.get("final_score", 50)
        signal = analysis_data.get("signal", "관망")
        
        # 시간 프레임별 데이터 추출
        short = analysis_data.get("short_term", {})
        medium = analysis_data.get("medium_term", {})
        long = analysis_data.get("long_term", {})
        consensus = analysis_data.get("consensus", {})
        events = analysis_data.get("events", {})
        patterns = analysis_data.get("all_patterns", [])
        fundamental = analysis_data.get("fundamental", {})
        macro = analysis_data.get("macro", {})
        vol_price = analysis_data.get("volume_price", {})
        psychology = analysis_data.get("psychology", {})
        
        report = []
        report.append(f"╔═══════════════════════════════════════════════════╗")
        report.append(f"║  [{ticker}] 전문가급 AI 종합 분석 리포트         ║")
        report.append(f"╚═══════════════════════════════════════════════════╝")
        report.append("")
        report.append(f"📊 **최종 투자 의견**: {signal} (AI 신뢰도: {score}/100)")
        report.append("=" * 60)
        report.append("")
        
        # ===== 1. 핵심 요약 =====
        report.append("🎯 **핵심 요약 (Executive Summary)**")
        report.append("-" * 60)
        consensus_rec = consensus.get('recommendation', '데이터 분석 중...')
        report.append(f"  {consensus_rec}")
        report.append("")
        
        # 시장 포지션
        if events:
            sector = events.get('sector', 'N/A')
            industry = events.get('industry', 'N/A')
            market_cap = events.get('market_cap', 0)
            if market_cap:
                cap_str = f"${market_cap/1e9:.2f}B" if market_cap > 1e9 else f"${market_cap/1e6:.2f}M"
                report.append(f"  📌 섹터: {sector} | 산업: {industry} | 시가총액: {cap_str}")
                report.append("")
        
        # ===== 2. 다중 시간 프레임 분석 =====
        report.append("📈 **다중 시간 프레임 분석**")
        report.append("-" * 60)
        
        # 단기
        report.append("🔹 **단기 전망 (1개월)**")
        if short:
            sh_score = short.get('score', 0)
            sh_signal = short.get('signal', '중립')
            sh_insights = short.get('specialized_insights', {})
            sh_full = short.get('full_analysis', {})
            
            report.append(f"   • 점수: {sh_score}/100 | 신호: {sh_signal}")
            
            momentum_data = sh_insights.get('quick_momentum', {})
            if momentum_data:
                report.append(f"   • 단기 모멘텀: {momentum_data.get('message', 'N/A')}")
            
            vol_data = sh_insights.get('intraday_volatility', {})
            if vol_data:
                report.append(f"   • 변동성: {vol_data.get('interpretation', 'N/A')}")
            
            rsi = sh_full.get('rsi')
            if rsi is not None:
                rsi_status = "과매수" if rsi > 70 else "과매도" if rsi < 30 else "중립"
                report.append(f"   • RSI(14): {rsi:.1f} ({rsi_status})")
            else:
                report.append(f"   • RSI(14): 분석 중/중립 (50.0)")
            
            entry = short.get('entry_points', {})
            if entry:
                buy_zone = entry.get('buy_zone', [])
                if buy_zone:
                    buy_p = buy_zone[0].get('price', 0)
                    tp_p = entry.get('take_profit', 0)
                    sl_p = entry.get('stop_loss', 0)
                    report.append(f"   • **추천 타점**: 매수 ${buy_p:,.2f} | 목표 ${tp_p:,.2f} | 손절 ${sl_p:,.2f}")
        report.append("")
        
        # 중기
        report.append("🔹 **중기 전망 (6개월)**")
        if medium:
            md_score = medium.get('score', 0)
            md_signal = medium.get('signal', '중립')
            md_insights = medium.get('specialized_insights', {})
            
            report.append(f"   • 점수: {md_score}/100 | 신호: {md_signal}")
            
            trend_data = md_insights.get('trend_strength', {})
            if trend_data:
                report.append(f"   • 추세 강도: {trend_data.get('message', 'N/A')}")
            
            zone_data = md_insights.get('swing_zones', {})
            if zone_data:
                report.append(f"   • 현재 구간: {zone_data.get('zone', 'N/A')}")
            
            entry = medium.get('entry_points', {})
            if entry:
                buy_zone = entry.get('buy_zone', [])
                if buy_zone:
                    buy_p = buy_zone[0].get('price', 0)
                    tp_p = entry.get('take_profit', 0)
                    report.append(f"   • **스윙 전략**: 매입 ${buy_p:,.2f} | 목표 ${tp_p:,.2f}")
        report.append("")
        
        # 장기
        report.append("🔹 **장기 전망 (1년+)**")
        if long:
            lg_score = long.get('score', 0)
            lg_signal = long.get('signal', '중립')
            lg_insights = long.get('specialized_insights', {})
            
            report.append(f"   • 점수: {lg_score}/100 | 신호: {lg_signal}")
            
            trend_data = lg_insights.get('long_term_trend', {})
            if trend_data:
                report.append(f"   • 연간 추세: {trend_data.get('message', 'N/A')}")
            
            phase_data = lg_insights.get('accumulation_phase', {})
            if phase_data:
                report.append(f"   • 매집 단계: {phase_data.get('message', 'N/A')}")
        report.append("")
        
        # ===== 3. 차트 패턴 =====
        if patterns:
            report.append("🔍 **차트 패턴 분석**")
            report.append("-" * 60)
            for i, pattern in enumerate(patterns[:3], 1):
                name = pattern.get('name', 'Unknown')
                ptype = pattern.get('type', 'N/A')
                reliability = pattern.get('reliability', 0)
                desc = pattern.get('desc', '')
                report.append(f"   {i}. **{name}** ({ptype}) - 신뢰도: {reliability:.1f}/5.0")
                report.append(f"      {desc}")
            report.append("")
        
        # ===== 4. 리스크 요인 =====
        report.append("⚠️ **주요 리스크 요인**")
        report.append("-" * 60)
        
        if events:
            earnings = events.get('earnings_date')
            if earnings:
                report.append(f"   • 📅 실적 발표: {earnings} (변동성 극대화 예상)")
        
        if short:
            rsi = short.get('full_analysis', {}).get('rsi', 0)
            if rsi > 70:
                report.append(f"   • 🔴 과매수 구간 (RSI {rsi:.1f}) - 단기 조정 가능성")
            elif rsi < 30:
                report.append(f"   • 🟢 과매도 구간 (RSI {rsi:.1f}) - 반등 가능성")
        
        report.append("")
        
        # ===== 5. 최종 결론 =====
        report.append("🎯 **최종 투자 전략**")
        report.append("=" * 60)
        
        if score >= 70:
            report.append("   ✅ **강력 매수**: 현재 시점에서 매수 포지션 진입을 적극 권장합니다.")
        elif score >= 60:
            report.append("   ✅ **매수**: 긍정적 신호가 우세합니다. 분할 매수 전략을 고려하세요.")
        elif score >= 50:
            report.append("   ⚪ **중립**: 관망이 적절합니다. 추가 신호를 기다리세요.")
        elif score >= 40:
            report.append("   ⚠️ **매도**: 부정적 신호가 감지됩니다. 보유 시 손절 라인 설정 필수.")
        else:
            report.append("   🔴 **강력 매도**: 즉시 청산을 검토하세요.")
        
        report.append("")
        report.append("=" * 60)
        report.append("📌 본 리포트는 AI 알고리즘 기반 참고 자료이며,")
        report.append("   실제 투자 판단 및 손익은 전적으로 투자자 본인의 책임입니다.")
        report.append("=" * 60)
        
        return "\n".join(report)


def get_stock_events(ticker: str) -> Dict[str, Any]:
    """
    yfinance를 통해 주요 이벤트 일정 수집
    """
    import yfinance as yf
    
    events = {}
    
    try:
        stock = yf.Ticker(ticker)
        
        try:
            calendar = stock.calendar
            if calendar is not None:
                if isinstance(calendar, dict):
                    if 'Earnings Date' in calendar:
                        earnings_dates = calendar['Earnings Date']
                        if earnings_dates:
                            events['earnings_date'] = str(earnings_dates[0].date() if hasattr(earnings_dates[0], 'date') else earnings_dates[0])
                    if 'Ex-Dividend Date' in calendar:
                        ex_div = calendar['Ex-Dividend Date']
                        if ex_div:
                            events['ex_dividend_date'] = str(ex_div.date() if hasattr(ex_div, 'date') else ex_div)
        except:
            pass
        
        try:
            info = stock.info
            if info:
                events['dividend_yield'] = info.get('dividendYield')
                events['market_cap'] = info.get('marketCap')
                events['sector'] = info.get('sector')
                events['industry'] = info.get('industry')
        except:
            pass
            
    except Exception as e:
        logger.error(f"이벤트 정보 수집 오류: {e}")
    
    return events
