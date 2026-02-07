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

class AIAnalyzer:
    """
    Hugging Face API를 활용한 AI 분석기
    - FinBERT: 금융 뉴스 감성 분석
    - LLM: 전문가 리포트 생성
    """
    
    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN")
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
        
        # 프롬프트 구성
        ticker = analysis_data.get("ticker", "UNKNOWN")
        score = analysis_data.get("final_score", 50)
        signal = analysis_data.get("signal", "관망")
        tech = analysis_data.get("technical", {})
        fund = analysis_data.get("fundamental", {})
        events = analysis_data.get("events", {})
        
        # RSI 값 안전하게 포맷팅
        rsi_val = tech.get('rsi', None)
        rsi_str = f"{rsi_val:.1f}" if isinstance(rsi_val, (int, float)) else "N/A"
        current_price = tech.get('current_price', 'N/A')
        if isinstance(current_price, (int, float)):
            current_price = f"{current_price:,.0f}"
        
        prompt = f"""당신은 10년 경력의 전문 증권 애널리스트입니다. 아래 데이터를 바탕으로 한국어로 간결한 투자 의견을 작성해주세요.

[종목 정보]
- 티커: {ticker}
- 종합 점수: {score}/100
- 현재 신호: {signal}

[기술적 분석]
- RSI: {rsi_str}
- MACD 상태: {tech.get('summary', 'N/A')}
- 현재가: {current_price}

[기본적 분석]
- {fund.get('summary', '데이터 없음')}

[주요 일정]
- 실적발표일: {events.get('earnings_date', '미정')}
- 배당락일: {events.get('ex_dividend_date', '미정')}

위 정보를 바탕으로:
1. 현재 시장 상황 요약 (1줄)
2. 매수/매도 타점 추천 (가격 제시)
3. 리스크 요인 (1줄)
4. 결론 (1줄)

간결하게 작성해주세요."""

        try:
            # 경량 LLM 사용 (무료 Inference API 지원)
            response = self.client.text_generation(
                prompt,
                model="microsoft/Phi-3-mini-4k-instruct",
                max_new_tokens=300,
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
        
        tech = analysis_data.get("technical", {})
        entry = analysis_data.get("entry_points", {})
        events = analysis_data.get("events", {})
        
        report = []
        report.append(f"[{ticker}] 투자 분석 리포트")
        report.append("=" * 40)
        report.append("")
        
        # 현재 상황 요약
        if score >= 70:
            report.append(f"[+] 현재 상황: 기술적/기본적 지표가 모두 긍정적입니다. 매수 관점 유효.")
        elif score >= 50:
            report.append(f"[=] 현재 상황: 혼조세입니다. 추가 확인 후 진입을 권장합니다.")
        else:
            report.append(f"[-] 현재 상황: 하락 신호가 우세합니다. 신규 매수는 자제하세요.")
        
        report.append("")
        
        # 매수/매도 타점
        if entry:
            current = entry.get('current_price', 0)
            buy1 = entry.get('buy_target_1', 0)
            sell1 = entry.get('sell_target_1', 0)
            stop = entry.get('stop_loss', 0)
            
            report.append("[*] 추천 매매 전략:")
            report.append(f"    - 현재가: {current:,.0f}")
            report.append(f"    - 1차 매수가: {buy1:,.0f} (볼린저 하단)")
            report.append(f"    - 목표가: {sell1:,.0f}")
            report.append(f"    - 손절가: {stop:,.0f}")
        
        report.append("")
        
        # 이벤트 정보
        if events:
            earnings = events.get('earnings_date')
            dividend = events.get('ex_dividend_date')
            if earnings:
                report.append(f"[!] 실적발표일: {earnings}")
                report.append("    -> 실적 발표 전후 변동성 확대 가능. 포지션 조절 권장.")
            if dividend:
                report.append(f"[!] 배당락일: {dividend}")
        
        report.append("")
        
        # 리스크
        rsi = tech.get('rsi', 50)
        if rsi > 70:
            report.append(f"[주의] 리스크: RSI {rsi:.1f}로 과매수 구간. 단기 조정 가능성.")
        elif rsi < 30:
            report.append(f"[기회] RSI {rsi:.1f}로 과매도 구간. 반등 가능성 주시.")
        
        report.append("")
        report.append(f">>> 결론: {signal_clean} (종합점수 {score}/100)")
        
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
