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

from src.config import HF_TOKEN

class AIAnalyzer:
    """
    Hugging Face API를 활용한 AI 분석기
    - FinBERT: 금융 뉴스 감성 분석
    - LLM: 전문가 리포트 생성
    """
    
    def __init__(self):
        self.hf_token = HF_TOKEN
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
    
    def generate_report(self, analysis_data: Dict[str, Any]) -> str:
        """
        분석 데이터를 바탕으로 전문가급 투자 리포트 생성
        """
        if not self.client:
            return self._generate_fallback_report(analysis_data)
        
        # 프롬프트 구성 (Magnifi/Danelfin 스타일 가이드 반영)
        ticker = analysis_data.get("ticker", "UNKNOWN")
        score = analysis_data.get("final_score", 50)
        signal = analysis_data.get("signal", "중립")
        
        # 신규 구조 적용 (Daily Analysis 기준)
        daily = analysis_data.get("daily_analysis", {})
        fund = analysis_data.get("fundamental", {})
        events = analysis_data.get("events", {})
        
        rsi_val = daily.get('rsi', 'N/A')
        current_price = daily.get('last_close', 'N/A')
        macd_summary = daily.get('summary', '데이터 없음')
        
        # 차트 패턴 정보
        patterns = daily.get('patterns', [])
        pattern_str = "\n".join([f"- {p['name']}: {p['desc']}" for p in patterns]) if patterns else "감지된 주요 패턴 없음"
        
        prompt = f"""당신은 Wall Street 15년 경력의 시니어 퀀트 애널리스트입니다. 아래 정밀 분석 데이터를 바탕으로 개인 투자자를 위한 프리미엄 리포트를 작성해주세요.

[분석 타겟] 티커: {ticker}
[AI 확률 스코어] {score}/100
[종합 투자의견] {signal}

[기술적 분석 데이터]
- 현재가: {current_price}
- RSI (14일): {rsi_val}
- MACD 상태: {macd_summary}
- 포착된 핵심 차트 패턴:
{pattern_str}

[기업 기본 분석]
- 재무 건전성 요약: {fund.get('summary', '정보 없음')}

[주요 일정 및 리스크]
- 주요 일정(실적/배당): {events.get('earnings_date', '미정')}
- 주의사항: RSI가 70이상이면 과열, 30이하면 과매도 가능성이 높음.

작성 가이드라인:
1. '마켓 인사이트': 현재 차트 패턴이 시사하는 바와 기술적 위치를 명확히 설명.
2. '트레이딩 포인트': 구체적인 진입 타점과 목표가를 확률적으로 제시.
3. '리스크 경고': 투자자가 가장 조심해야 할 1가지를 명시.
4. '최종 컨설팅': 보수적이지만 단호한 어조로 최종 행동 지침 제언.

최소 300자 이상의 한국어로 전문성 있게 작성하되, 가독성을 위해 불렛 포인트를 사용하세요."""

        try:
            # 경량 LLM 사용
            response = self.client.text_generation(
                prompt,
                model="microsoft/Phi-3-mini-4k-instruct",
                max_new_tokens=400,
                temperature=0.7
            )
            
            if response:
                return response.strip()
                
        except Exception as e:
            logger.error(f"리포트 생성 오류: {e}")
            # 모델이 안 되면 다른 모델 시도
            try:
                response = self.client.text_generation(
                    prompt,
                    model="HuggingFaceH4/zephyr-7b-beta",
                    max_new_tokens=300,
                    temperature=0.7
                )
                if response:
                    return response.strip()
            except:
                pass
        
        return self._generate_fallback_report(analysis_data)
    
    def _generate_fallback_report(self, analysis_data: Dict[str, Any]) -> str:
        """AI API 실패 시 규칙 기반 리포트 생성 (이모지 없는 버전)"""
        ticker = analysis_data.get("ticker", "UNKNOWN")
        score = analysis_data.get("final_score", 50)
        signal = analysis_data.get("signal", "관망")
        # 신호에서 이모지 제거
        signal_clean = signal.replace('📈', '').replace('📉', '').replace('⚠️', '').replace('🔥', '').strip()
        
        daily = analysis_data.get("daily_analysis", {})
        entry = analysis_data.get("entry_points", {})
        events = analysis_data.get("events", {})
        
        report = []
        report.append(f"[{ticker}] 투자 분석 리포트 (Fallback)")
        report.append("=" * 40)
        report.append("")
        
        # 현재 상황 요약
        if score >= 70:
            report.append(f"[+] 상황 요약: 기술적/기본적 지표가 모두 긍정적입니다. 매수 우위 시장.")
        elif score >= 50:
            report.append(f"[=] 상황 요약: 혼조세가 강합니다. 박스권 매매 또는 관망을 제안합니다.")
        else:
            report.append(f"[-] 상황 요약: 하향 압력이 거셉니다. 리스크 관리가 최우선입니다.")
        
        report.append("")
        
        # 매수/매도 타점
        if entry:
            # 타점에 이미 포맷팅된 문자열이 있음 (buy, target, stop)
            report.append("[*] AI 추천 정밀 타점:")
            report.append(f"    - 현재가: {entry.get('current_price', 0):,.0f}")
            report.append(f"    - 매수가: {entry.get('buy', 'N/A')}")
            report.append(f"    - 목표가: {entry.get('target', 'N/A')}")
            report.append(f"    - 손절가: {entry.get('stop', 'N/A')}")
        
        report.append("")
        
        # 이벤트 정보
        if events:
            earnings = events.get('earnings_date')
            if earnings:
                report.append(f"[!] 알림: {earnings} 실적 발표 예정. 변동성 주의.")
        
        report.append("")
        
        # 리스크
        rsi = daily.get('rsi', 50)
        if isinstance(rsi, (int, float)):
            if rsi > 70:
                report.append(f"[주의] 단기 과열: RSI {rsi:.1f}로 조정 가능성 존재.")
            elif rsi < 30:
                report.append(f"[기회] 낙폭 과대: RSI {rsi:.1f}로 기술적 반등 기대 가능.")
        
        report.append("")
        report.append(f">>> 최종 결론: {signal_clean} (신뢰도 {score}%)")
        
        return "\n".join(report)


def get_stock_events(ticker: str) -> Dict[str, Any]:
    """
    yfinance를 통해 주요 이벤트 일정 수집
    - 실적 발표일
    - 배당락일
    - 주주총회
    """
    import yfinance as yf
    
    events = {}
    
    try:
        stock = yf.Ticker(ticker)
        
        # 실적 발표일
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
                    if 'Dividend Date' in calendar:
                        div_date = calendar['Dividend Date']
                        if div_date:
                            events['dividend_date'] = str(div_date.date() if hasattr(div_date, 'date') else div_date)
        except:
            pass
        
        # 배당 정보
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
