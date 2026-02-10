"""
AI 채팅 페이지
대화형 투자 상담
"""
import streamlit as st
from src.agents.chat_assistant import ChatAssistant
from datetime import datetime

def show():
    st.title("💬 AI 투자 상담")
    st.markdown("### 궁금한 것을 물어보세요!")
    
    # 세션 상태 초기화
    if 'chat_assistant' not in st.session_state:
        st.session_state.chat_assistant = ChatAssistant()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'current_context' not in st.session_state:
        st.session_state.current_context = None
    
    # 사이드바 - 컨텍스트 설정
    with st.sidebar:
        st.subheader("📊 분석 컨텍스트")
        
        context_ticker = st.text_input("종목 심볼", "AAPL", key="context_ticker")
        
        if st.button("컨텍스트 로드", type="primary"):
            with st.spinner("분석 중..."):
                try:
                    from src.agents.multi_timeframe import MultiTimeframeAnalyzer
                    import yfinance as yf
                    
                    analyzer = MultiTimeframeAnalyzer()
                    result = analyzer.analyze_all_timeframes(context_ticker.upper())
                    
                    ticker_data = yf.Ticker(context_ticker.upper())
                    current_price = ticker_data.history(period="1d")['Close'].iloc[-1]
                    
                    st.session_state.current_context = {
                        "ticker": context_ticker.upper(),
                        "current_price": current_price,
                        "analysis": result['medium_term']['full_analysis'] if result['medium_term'] else {},
                        "patterns": result['all_patterns'][:5]
                    }
                    
                    st.success(f"✅ {context_ticker.upper()} 컨텍스트 로드 완료!")
                    
                except Exception as e:
                    st.error(f"컨텍스트 로드 실패: {e}")
        
        if st.session_state.current_context:
            st.markdown("---")
            st.markdown("**현재 컨텍스트:**")
            ctx = st.session_state.current_context
            st.write(f"종목: {ctx['ticker']}")
            st.write(f"현재가: ${ctx['current_price']:.2f}")
            st.write(f"패턴: {len(ctx.get('patterns', []))}개")
        
        st.markdown("---")
        
        if st.button("대화 초기화"):
            st.session_state.chat_history = []
            st.session_state.chat_assistant.clear_history()
            st.success("대화가 초기화되었습니다.")
            st.rerun()
    
    # 추천 질문
    st.markdown("**💡 추천 질문:**")
    
    suggestions = st.session_state.chat_assistant.suggest_questions(
        st.session_state.current_context
    )
    
    cols = st.columns(len(suggestions[:3]))
    for i, suggestion in enumerate(suggestions[:3]):
        with cols[i]:
            if st.button(suggestion, key=f"suggest_{i}"):
                # 추천 질문 클릭 시 자동 전송
                st.session_state.pending_message = suggestion
    
    st.markdown("---")
    
    # 대화 히스토리 표시
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                with st.chat_message("user"):
                    st.write(msg['content'])
                    st.caption(msg.get('timestamp', ''))
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(msg['content'])
                    st.caption(msg.get('timestamp', ''))
    
    # 입력창
    user_input = st.chat_input("메시지를 입력하세요...")
    
    # 추천 질문 처리
    if 'pending_message' in st.session_state:
        user_input = st.session_state.pending_message
        del st.session_state.pending_message
    
    if user_input:
        # 사용자 메시지 추가
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': timestamp
        })
        
        # AI 응답 생성
        with st.spinner("AI가 답변을 생성하는 중..."):
            try:
                response = st.session_state.chat_assistant.chat(
                    user_input,
                    context=st.session_state.current_context
                )
                
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
            except Exception as e:
                error_msg = f"죄송합니다. 오류가 발생했습니다: {str(e)}"
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': error_msg,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        st.rerun()
    
    # 안내 메시지
    if not st.session_state.chat_history:
        st.info("""
        👋 안녕하세요! AI 투자 상담 어시스턴트입니다.
        
        **사용 방법:**
        1. 왼쪽 사이드바에서 종목을 입력하고 '컨텍스트 로드'를 클릭하세요.
        2. 위의 추천 질문을 클릭하거나, 직접 질문을 입력하세요.
        3. AI가 분석 결과를 바탕으로 답변해 드립니다.
        
        **예시 질문:**
        - "AAPL 지금 사도 될까요?"
        - "어떤 차트 패턴이 나왔나요?"
        - "투자 리스크는 무엇인가요?"
        """)
    
    # 푸터
    st.markdown("---")
    st.caption("⚠️ AI 응답은 참고용이며, 투자 권유가 아닙니다. 최종 결정은 본인의 책임입니다.")
