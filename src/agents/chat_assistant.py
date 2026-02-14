"""
AI 채팅 어시스턴트 (Gemini Flash 통합)
Google Gemini Flash - 무료, 빠르고, 똑똑함!
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import json

# 프로젝트 도구
from src.data.storage import get_storage
from src.data.collector import MarketDataCollector

logger = logging.getLogger(__name__)

# --- 도구(Tools) 정의 ---
def set_price_alert(ticker: str, target_price: float, condition: str = "above", note: str = "") -> str:
    """주식 가격 알림을 설정합니다. (condition: 'above' 또는 'below')"""
    try:
        storage = get_storage()
        alert_id = storage.save_alert(
            ticker=ticker.upper(),
            alert_type=f"price_{condition}",
            target_value=target_price,
            note=note
        )
        return json.dumps({"status": "success", "alert_id": alert_id, "message": f"{ticker} ${target_price} {condition} 알람이 설정되었습니다."})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def get_market_data(ticker: str) -> str:
    """주식의 현재가 및 최근 데이터를 가져옵니다."""
    try:
        collector = MarketDataCollector()
        df = collector.get_ohlcv(ticker.upper(), period="5d", interval="1d")
        if df is None or df.empty:
            return json.dumps({"status": "error", "message": "데이터를 찾을 수 없습니다."})
        
        current_price = df['Close'].iloc[-1]
        return json.dumps({
            "ticker": ticker.upper(),
            "current_price": float(current_price),
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

# 도구 리스트
TRADING_TOOLS = [set_price_alert, get_market_data]

class ChatAssistant:
    """
    대화형 AI 투자 어시스턴트
    - Google Gemini Flash 사용 (무료!)
    - API 키 없어도 고급 룰 기반 시스템 작동
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Args:
            gemini_api_key: Google Gemini API 키 (선택사항, 무료)
        """
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        
        if self.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                
                # 사용 가능한 모델 자동 탐색 (404 에러 방지)
                model_name = 'gemini-pro' # 기본값
                try:
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            if 'gemini' in m.name:
                                model_name = m.name
                                break
                    logger.info(f"선택된 Gemini 모델: {model_name}")
                except Exception as e:
                    logger.warning(f"모델 목록 조회 실패 ({e}), 기본값 사용: {model_name}")

                self.model = genai.GenerativeModel(
                    model_name=model_name,
                    tools=TRADING_TOOLS
                )
                self.chat_session = self.model.start_chat(enable_automatic_function_calling=True)
                self.use_ai = True
                logger.info("✅ Google Gemini 활성화 (Tool Calling 지원 모드)")
            except Exception as e:
                self.model = None
                self.use_ai = False
                logger.warning(f"Gemini 초기화 실패: {e}. 고급 룰 기반 모드로 동작합니다.")
        else:
            self.model = None
            self.use_ai = False
            logger.info("💡 고급 룰 기반 모드로 동작합니다 (API 키 불필요)")
        
        # 대화 히스토리
        self.conversation_history: List[Dict[str, str]] = []
        
        # Gemini용 시스템 프롬프트
        self.system_prompt = """당신은 전문 투자 분석가 AI 어시스턴트입니다.

역할:
- 사용자의 투자 관련 질문에 명확하고 전문적으로 답변합니다
- 기술적 분석, 펀더멘털 분석, 시장 동향을 설명합니다
- 리스크를 항상 언급하며, 투자 결정은 사용자 책임임을 강조합니다

답변 스타일:
- 한국어로 친절하고 명확하게 답변합니다
- 전문 용어는 쉽게 풀어서 설명합니다
- 구체적인 숫자와 근거를 제시합니다
- 3~5문장으로 간결하게 답변합니다
- 이모지를 적절히 사용하여 가독성을 높입니다

주의사항:
- "투자 권유"가 아닌 "정보 제공"임을 명시합니다
- 확실하지 않은 내용은 "추정" 또는 "가능성"으로 표현합니다
- 과거 데이터는 미래를 보장하지 않음을 강조합니다"""
    
    def chat(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        사용자 메시지에 응답
        
        Args:
            user_message: 사용자 질문
            context: 추가 컨텍스트 (분석 결과, 종목 정보 등)
            
        Returns:
            AI 응답 메시지
        """
        # 대화 히스토리에 추가
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # 응답 생성
        if self.use_ai and self.model:
            try:
                response = self._generate_response_with_gemini(user_message, context)
            except Exception as e:
                logger.error(f"Gemini 응답 실패: {e}")
                response = self._generate_smart_response(user_message, context)
        else:
            response = self._generate_smart_response(user_message, context)
        
        # 응답 히스토리에 추가
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def _generate_response_with_gemini(self, message: str, context: Optional[Dict] = None) -> str:
        """Gemini Flash를 사용한 응답 생성 (Tool Calling 포함)"""
        try:
            # 컨텍스트 기반 시스템 지침 추가
            instruction = self.system_prompt
            if context:
                instruction += f"\n\n현재 컨텍스트: {json.dumps(context, ensure_ascii=False)}"
            
            # 메시지 전송 (자동 도구 실행 활성화됨)
            response = self.chat_session.send_message(message)
            
            if response and response.text:
                return response.text.strip()
            else:
                return "죄송합니다. 응답을 생성하지 못했습니다."
                
        except Exception as e:
            logger.error(f"Gemini 응답 생성 실패: {e}")
            return self._generate_smart_response(message, context)
    
    def _build_gemini_prompt(self, message: str, context: Optional[Dict] = None) -> str:
        """Gemini 프롬프트 구성"""
        prompt_parts = [self.system_prompt, "\n\n"]
        
        # 컨텍스트 추가
        if context:
            prompt_parts.append("=== 참고 정보 ===\n")
            
            if 'ticker' in context:
                prompt_parts.append(f"종목: {context['ticker']}\n")
            
            if 'current_price' in context:
                prompt_parts.append(f"현재가: ${context['current_price']:.2f}\n")
            
            if 'analysis' in context:
                analysis = context['analysis']
                prompt_parts.append(f"AI 분석 점수: {analysis.get('final_score', 'N/A')}/100\n")
                prompt_parts.append(f"신호: {analysis.get('signal', 'N/A')}\n")
            
            if 'patterns' in context:
                patterns = context['patterns']
                if patterns:
                    pattern_names = [p['name'] for p in patterns[:3]]
                    prompt_parts.append(f"감지된 패턴: {', '.join(pattern_names)}\n")
            
            prompt_parts.append("\n")
        
        # 최근 대화 히스토리 (최대 4턴)
        recent_history = self.conversation_history[-8:]
        if recent_history:
            prompt_parts.append("=== 이전 대화 ===\n")
            for msg in recent_history:
                role = "사용자" if msg['role'] == 'user' else "AI"
                prompt_parts.append(f"{role}: {msg['content']}\n")
            prompt_parts.append("\n")
        
        # 현재 질문
        prompt_parts.append(f"사용자: {message}\n")
        prompt_parts.append("AI: ")
        
        return "".join(prompt_parts)
    
    def _generate_smart_response(self, message: str, context: Optional[Dict] = None) -> str:
        """
        고급 룰 기반 응답 시스템 (API 키 불필요)
        """
        message_lower = message.lower()
        
        # 1. 인사
        if any(k in message_lower for k in ['안녕', '헬로', '하이', 'hi', 'hello']):
            return ("안녕하세요! 👋 AI 투자 분석 어시스턴트입니다.\n\n"
                    "저는 다음과 같은 도움을 드릴 수 있습니다:\n"
                    "• 종목 매수/매도 판단\n"
                    "• 차트 패턴 분석 설명\n"
                    "• 투자 리스크 평가\n"
                    "• 목표가 및 전망 제시\n\n"
                    "궁금한 것을 편하게 물어보세요!")
        
        # 2. 매수 질문
        if any(k in message_lower for k in ['사도', '살까', '매수', '사야', '투자해', '들어가']):
            return self._buy_response(context)
        
        # 3. 매도 질문
        if any(k in message_lower for k in ['팔까', '매도', '팔아야', '청산', '손절']):
            return self._sell_response(context)
        
        # 4. 전망 질문
        if any(k in message_lower for k in ['전망', '예상', '앞으로', '미래', '오를', '내릴']):
            return self._forecast_response(context)
        
        # 5. 패턴 질문
        if any(k in message_lower for k in ['패턴', '차트', '기술적']):
            return self._pattern_response(context)
        
        # 6. 목표가 질문
        if any(k in message_lower for k in ['목표가', '타겟', '얼마']):
            return self._target_response(context)
        
        # 7. 리스크 질문
        if any(k in message_lower for k in ['리스크', '위험', '손실']):
            return self._risk_response()
        
        # 8. 기본 응답
        return ("💡 **추천 질문:**\n\n"
                "• 'AAPL 지금 사도 될까요?'\n"
                "• '목표가는 얼마인가요?'\n"
                "• '차트 패턴은 무엇인가요?'\n"
                "• '투자 리스크는?'\n\n"
                "자유롭게 투자 관련 질문을 해주세요!")
    
    def _buy_response(self, context: Optional[Dict]) -> str:
        """매수 판단 응답"""
        # 컨텍스트가 없으면 일반적인 조언을 하되, 메시지 내에 정보가 있을 수 있으므로 차단하지 않음
        if not context or 'ticker' not in context:
            # 혹시 메시지 자체에 분석 요청이 포함되어 있을 수 있으므로 Gemini에게 넘김 (여기서 리턴 X)
            pass
        
        if not context or 'analysis' not in context:
             # Gemini가 처리하도록 유도 (프롬프트 인젝션된 경우)
             return self._generate_response_with_gemini("매수 관점에서 분석해줘 (데이터는 위 메시지에 있음)", context)

        ticker = context['ticker']
        score = context.get('analysis', {}).get('final_score', 50)
        signal = context.get('analysis', {}).get('signal', '중립')
        
        response = f"**{ticker} 매수 판단:**\n\n"
        response += f"📊 AI 분석 점수: **{score}/100**\n"
        response += f"📈 신호: **{signal}**\n\n"
        
        if score >= 75:
            response += "✅ **매수 추천**\n"
            response += "점수가 매우 높습니다. 현재 기술적, 펀더멘털, 거시 환경이 모두 우호적입니다.\n\n"
            response += "**추천 전략:**\n"
            response += "• 분할 매수 (2~3회)\n"
            response += "• 손절가: 현재가 -7% 설정\n"
            response += "• 목표 수익률: +15~20%"
        elif score >= 60:
            response += "💡 **긍정적 신호**\n"
            response += "점수가 양호합니다. 매수를 고려할 수 있으나, 진입 타이밍을 신중히 선택하세요.\n\n"
            response += "**추천 전략:**\n"
            response += "• 조정 시 분할 매수\n"
            response += "• 손절가: 현재가 -10% 설정"
        elif score >= 45:
            response += "⚠️ **중립**\n"
            response += "점수가 중립적입니다. 추가 분석이 필요하며, 급하게 진입하지 마세요."
        else:
            response += "🚫 **매수 비추천**\n"
            response += "점수가 낮습니다. 현재 시점에서의 매수는 리스크가 높습니다."
        
        response += "\n\n⚠️ *최종 결정은 본인의 투자 성향과 리스크 감내도를 고려하여 신중히 내리세요.*"
        return response
    
    def _sell_response(self, context: Optional[Dict]) -> str:
        """매도 판단 응답"""
        if not context or 'ticker' not in context:
            return "구체적인 종목 데이터가 없어 매도 판단이 어렵습니다."
        
        ticker = context['ticker']
        score = context.get('analysis', {}).get('final_score', 50)
        
        response = f"**{ticker} 매도 판단:**\n\n"
        response += f"📊 현재 점수: **{score}/100**\n\n"
        
        if score < 35:
            response += "🚨 **즉시 매도 권장**\n추가 하락 리스크가 높습니다."
        elif score < 50:
            response += "⚠️ **매도 고려**\n일부 차익 실현을 고려하세요."
        elif score < 65:
            response += "💡 **보유 또는 일부 매도**\n목표 수익률에 따라 판단하세요."
        else:
            response += "✅ **보유 권장**\n급하게 매도할 필요는 없습니다."
        
        return response
    
    def _forecast_response(self, context: Optional[Dict]) -> str:
        """전망 응답"""
        if context and 'ticker' in context:
            score = context.get('analysis', {}).get('final_score', 50)
            
            if score >= 70:
                return "📈 **상승 전망**\n기술적, 펀더멘털 지표가 모두 긍정적입니다."
            elif score >= 50:
                return "➡️ **중립 전망**\n혼조세가 예상됩니다."
            else:
                return "📉 **하락 전망**\n부정적 신호가 우세합니다."
        
        return "종목 상세 데이터가 확인되지 않아 일반적인 전망만 가능합니다."
    
    def _pattern_response(self, context: Optional[Dict]) -> str:
        """패턴 응답"""
        if context and 'patterns' in context:
            patterns = context['patterns']
            if patterns:
                response = "**감지된 차트 패턴:**\n\n"
                for i, p in enumerate(patterns[:5], 1):
                    response += f"{i}. **{p['name']}** (신뢰도: {p['reliability']}/5.0 ⭐)\n"
                return response
            else:
                return "현재 뚜렷한 차트 패턴이 감지되지 않았습니다."
        
        return "종목 데이터가 없어 패턴 분석이 불가능합니다."
    
    def _target_response(self, context: Optional[Dict]) -> str:
        """목표가 응답"""
        if context and 'patterns' in context:
            patterns = context['patterns']
            targets = [p for p in patterns if p.get('target')]
            
            if targets:
                response = "**패턴 기반 목표가:**\n\n"
                for p in targets[:3]:
                    response += f"• {p['name']}: **${p['target']:.2f}**\n"
                return response
        
        return "목표가 산출을 위한 충분한 패턴 데이터가 없습니다."
    
    def _risk_response(self) -> str:
        """리스크 응답"""
        return ("**투자 리스크:**\n\n"
                "1. 시장 리스크 📉\n"
                "2. 기업 리스크 🏢\n"
                "3. 거시 경제 리스크 🌍\n\n"
                "**리스크 관리:**\n"
                "✅ 분산 투자\n"
                "✅ 손절매 설정 (5~10%)\n"
                "✅ 정기 점검")
    
    def clear_history(self):
        """대화 히스토리 초기화"""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """대화 히스토리 반환"""
        return self.conversation_history
    
    def suggest_questions(self, context: Optional[Dict] = None) -> List[str]:
        """추천 질문 생성"""
        if context and 'ticker' in context:
            ticker = context['ticker']
            return [
                f"{ticker} 지금 사도 될까요?",
                f"{ticker} 목표가는 얼마인가요?",
                f"{ticker} 어떤 패턴이 나왔나요?"
            ]
        else:
            return [
                "투자 전략은 어떻게 세우나요?",
                "분산 투자는 어떻게 하나요?",
                "리스크 관리 방법은?"
            ]
