"""
AI 분석 모듈 - Hugging Face 연동
금융 감성 분석 + 전문가급 리포트 생성
"""
import os
import json
import base64
import logging
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import google.generativeai as genai

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

from src.config import settings

class AIAnalyzer:
    """
    AI 기반 종합 분석 리포트 생성기
    - Gemini Vision API (차트 이미지 분석)
    - Groq API (텍스트 기반 분석)
    """
    
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY # Changed to use settings
        self.groq_key = settings.GROQ_API_KEY # Changed to use settings
        self.hf_token = settings.HF_TOKEN # Changed to use settings
        
        logger.info(f"AIAnalyzer Init: Gemini key present={bool(self.gemini_key)}, Groq key present={bool(self.groq_key)}, HF token present={bool(self.hf_token)}")
        
        # Gemini Vision API 설정
        self.gemini_model = None
        if self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
                # 실제 API 모델 리스트에서 확인된 gemini-2.0-flash 사용
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
                logger.info("✅ Google Gemini Configured: gemini-2.0-flash")
            except Exception as e:
                logger.warning(f"Gemini Init Failed: {e}")
                self.gemini_model = None
        
        # Hugging Face 클라이언트 설정
        self.hf_client = None # Initialize hf_client
        if self.hf_token:
            try:
                self.hf_client = InferenceClient(token=self.hf_token)
                logger.info("✅ AIAnalyzer: Hugging Face connected")
            except Exception as e:
                logger.warning(f"Hugging Face connection failed: {e}")
        else:
            logger.warning("AIAnalyzer: HF_TOKEN is missing. Some AI features may be limited.")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        뉴스/텍스트 감성 분석 (Hugging Face Inference API)
        """
        if not self.hf_client:
            logger.warning("Hugging Face client not initialized")
            return {"label": "unknown", "score": 0.0, "error": "API 미연결"} # Added error for consistency
        
        try:
            # FinBERT 모델 사용
            result = self.hf_client.text_classification( # Changed to self.hf_client
                text,
                model="ProsusAI/finbert" # Reverted to original FinBERT model
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
    
    def generate_report(self, analysis_data: Dict[str, Any], image_bytes: Optional[bytes] = None, lang: str = "ko") -> Dict[str, Any]:
        """
        LLM에 모든 원본 지표 데이터를 전달하여 점수, 신호, 리포트를 생성하도록 요청합니다.
        Returns: Dict containing 'score', 'signal', 'report'
        """
        try:
            # 1. Try Gemini API (Vision capable)
            if self.gemini_key and self.gemini_model:
                try:
                    report_dict = self._generate_with_gemini(analysis_data, image_bytes, lang)
                    if report_dict:
                        return report_dict
                except Exception as e:
                    logger.warning(f"Gemini generation failed: {e}")
            
            # 2. Try Groq API (Text only fallback)
            if self.groq_key:
                report_dict = self._generate_with_groq_simple(analysis_data, lang)
                if report_dict:
                    return report_dict

            # 3. All APIs failed
            logger.warning("All AI APIs (Gemini, Groq) failed or unavailable. Returning default response.")

        except Exception as e:
            logger.error(f"AI Report generation failed: {e}", exc_info=True)
        
        # If all APIs fail, return a default error Dict
        return {
            "score": 50,
            "signal": "ERROR",
            "report": "모든 AI 분석 모델 호출에 실패했습니다. API 키 또는 네트워크 연결을 확인해주세요."
        }

    def _generate_with_gemini(self, analysis_data: Dict[str, Any], image_bytes: Optional[bytes], lang: str) -> Optional[Dict[str, Any]]:
        """Google Gemini API (Vision + Text)"""
        ticker = analysis_data.get("ticker", "UNKNOWN")
        logger.info(f"Generating AI report for {ticker} with Gemini (Image present: {bool(image_bytes)})")
        
        prompt = f"""
You are a professional financial analyst. Analyze the provided stock data (and chart image if available) for {ticker}.
Answer in {lang}.

Focus on:
1. Current Trend (Uptrend/Downtrend/Sideways) based on Moving Averages.
2. Key Support/Resistance Levels.
3. Momentum Indicators (RSI, MACD).
4. Volume Analysis.
5. Actionable Trading Strategy.

Input Data:
{json.dumps(analysis_data.get('medium_term_indicators', {}), indent=2)}

Output Requirements:
- Return ONLY valid JSON.
- Keys: "score" (0-100), "signal" (STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL), "report" (string).
- The "report" should be concise, professional, and directly address the user. Do NOT use markdown in the JSON string.
"""
        try:
            # Gemini Vision API는 inlineData 형식으로 이미지를 받음
            content = [prompt]
            
            if image_bytes:
                # Base64 인코딩
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                content.append({
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": base64_image
                    }
                })
            
            logger.info("Sending request to Gemini...")
            response = self.gemini_model.generate_content(
                content,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            result_json = json.loads(response.text)
            logger.info("Gemini API call successful!")
            return result_json
            
        except Exception as e:
            logger.warning(f"Gemini Vision API error: {e}")
            
            # 만약 이미지가 있어서 실패했을 수 있으므로, 이미지를 빼고 텍스트로만 재시도
            if image_bytes:
                logger.info("Retrying Gemini with TEXT ONLY (skipping image)...")
                try:
                    response = self.gemini_model.generate_content(
                        [prompt], # 이미지 제외
                        generation_config=genai.GenerationConfig(
                            response_mime_type="application/json"
                        )
                    )
                    result_json = json.loads(response.text)
                    logger.info("Gemini Text-Only retry successful!")
                    return result_json
                except Exception as e2:
                    logger.error(f"Gemini Text-Only retry failed: {e2}")
            
            return None

    def _generate_with_groq_simple(self, analysis_data: Dict[str, Any], lang: str) -> Optional[Dict[str, Any]]:
        """Groq API (Llama-3)를 간소화된 프롬프트로 사용 - 공식 라이브러리 사용"""
        logger.info("Attempting AI report generation with Groq (Simplified Prompt)...")
        ticker = analysis_data.get("ticker", "UNKNOWN")
        
        # Extract only the most critical indicators for a simpler prompt
        med_indicators = analysis_data.get("medium_term_indicators", {})
        
        if not med_indicators:
            return None

        # Build a simple text-based summary of indicators
        summary_lines = [f"Stock: {ticker}"]
        key_indicators = {
            "Price": med_indicators.get('Close'),
            "RSI": med_indicators.get('rsi'),
            "MACD Hist": med_indicators.get('Hist'),
            "Stochastic %K": med_indicators.get('stoch_k'),
            "ADX": med_indicators.get('adx'),
            "Price vs SMA50": "Above" if med_indicators.get('Close', 0) > med_indicators.get('sma_50', 0) else "Below",
            "Price vs SMA200": "Above" if med_indicators.get('Close', 0) > med_indicators.get('sma_200', 0) else "Below"
        }
        for name, value in key_indicators.items():
            if value is not None:
                summary_lines.append(f"- {name}: {value:.2f}" if isinstance(value, float) else f"- {name}: {value}")

        prompt_text = "\n".join(summary_lines)

        prompt = f"""You are an expert trading analyst. Analyze the following summary of technical indicators for {ticker}.
Based on this data, provide a final 'score' from 0-100, a 'signal' ('STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL'), and a 'report' explaining your reasoning in {lang}.

You MUST reply with a single, valid JSON object with the keys "score", "signal", and "report".

[Indicator Summary]
{prompt_text}
"""
        try:
            # 공식 Groq 라이브러리 사용
            from groq import Groq
            client = Groq(api_key=self.groq_key)
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            
            # DEBUG: Log the raw content
            logger.info(f"Groq raw response: {content[:500]}")
            
            # Parse JSON content from string to Dict
            try:
                parsed_content = json.loads(content)
                logger.info(f"✅ Groq parsed successfully: score={parsed_content.get('score')}, signal={parsed_content.get('signal')}")
                return parsed_content
            except json.JSONDecodeError as jde:
                logger.error(f"Groq returned invalid JSON: {content[:200]}")
                logger.error(f"JSON decode error: {jde}")
                return None
                
        except Exception as e:
            logger.error(f"Groq API (Simplified Prompt) failed: {e}", exc_info=True)
            return None
    
    # Old _generate_with_groq is no longer needed
    
def get_stock_events(ticker: str) -> Dict[str, Any]:
    # ... (This function remains unchanged) ...
    import yfinance as yf
    
    events = {}
    
    try:
        stock = yf.Ticker(ticker)
        
        try:
            calendar = stock.calendar
            if calendar is not None and not isinstance(calendar, bool):
                if isinstance(calendar, dict):
                    if 'Earnings Date' in calendar:
                        earnings_dates = calendar['Earnings Date']
                        if earnings_dates:
                            events['earnings_date'] = str(earnings_dates[0].date() if hasattr(earnings_dates[0], 'date') else earnings_dates[0])
                    if 'Ex-Dividend Date' in calendar:
                        ex_div = calendar['Ex-Dividend Date']
                        if ex_div:
                            events['ex_dividend_date'] = str(ex_div.date() if hasattr(ex_div, 'date') else ex_div)
        except Exception as e:
            logger.warning(f"Failed to get calendar events for {ticker}: {e}")
        
        try:
            info = stock.info
            if info:
                events['dividend_yield'] = info.get('dividendYield')
                events['market_cap'] = info.get('marketCap')
                events['sector'] = info.get('sector')
                events['industry'] = info.get('industry')
        except Exception as e:
            logger.warning(f"Failed to get basic info for {ticker}: {e}")
            
    except Exception as e:
        logger.error(f"이벤트 정보 수집 오류: {e}")
    
    return events