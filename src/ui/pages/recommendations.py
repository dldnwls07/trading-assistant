"""
AI 추천 종목 페이지
"""
import streamlit as st
from src.agents.screener import StockScreener
from src.agents.profiler import InvestorProfiler

def show():
    st.title("🎯 AI 추천 종목")
    st.markdown("### 투자 스타일 맞춤형 종목 추천")
    
    # 투자 스타일 선택
    profiler = InvestorProfiler()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        style = st.selectbox(
            "투자 스타일 선택",
            options=list(profiler.STYLES.keys()),
            format_func=lambda x: profiler.STYLES[x]['name']
        )
        
        style_info = profiler.STYLES[style]
        st.info(f"**{style_info['name']}**: {style_info['description']}")
    
    with col2:
        top_n = st.number_input("추천 종목 수", min_value=1, max_value=20, value=10)
    
    # 종목 리스트 선택
    st.markdown("---")
    st.subheader("📋 스크리닝 대상")
    
    source = st.radio(
        "종목 소스",
        ["S&P 500 (자동)", "직접 입력"]
    )
    
    if source == "직접 입력":
        ticker_input = st.text_area(
            "종목 심볼 입력 (쉼표로 구분)",
            "AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, NFLX, AMD, INTC"
        )
        tickers = [t.strip().upper() for t in ticker_input.split(",")]
    else:
        tickers = None  # S&P 500 자동 로드
    
    # 스크리닝 시작
    if st.button("🔍 추천 종목 찾기", type="primary"):
        with st.spinner("AI가 종목을 분석하는 중... (시간이 걸릴 수 있습니다)"):
            try:
                screener = StockScreener()
                
                # S&P 500 로드
                if tickers is None:
                    with st.status("S&P 500 종목 로딩 중..."):
                        tickers = screener.get_sp500_tickers()
                        st.write(f"✅ {len(tickers)}개 종목 로드 완료")
                        # 상위 50개만 사용 (속도 향상)
                        tickers = tickers[:50]
                        st.write(f"⚡ 상위 {len(tickers)}개 종목만 스크리닝")
                
                recommendations = screener.screen_stocks(
                    tickers=tickers,
                    investor_style=style,
                    top_n=top_n
                )
                
                st.session_state.recommendations = recommendations
                st.success(f"✅ {len(recommendations)}개 추천 종목 발견!")
                
            except Exception as e:
                st.error(f"스크리닝 실패: {e}")
    
    # 추천 결과 표시
    if 'recommendations' in st.session_state:
        recs = st.session_state.recommendations
        
        if recs:
            st.markdown("---")
            st.subheader(f"💎 추천 종목 ({len(recs)}개)")
            
            for i, rec in enumerate(recs, 1):
                with st.expander(f"{i}. {rec['ticker']} - 점수: {rec['score']:.1f} ({rec['signal']})"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**추천 이유:**")
                        st.write(rec['reason'])
                        
                        if 'entry_points' in rec and rec['entry_points']:
                            st.markdown("**매수 타점:**")
                            for zone in rec['entry_points'].get('buy_zone', [])[:2]:
                                st.write(f"• ${zone['price']:.2f} - {zone['reason']}")
                    
                    with col2:
                        st.metric("기본 점수", f"{rec['base_score']}/100")
                        st.metric("스타일 적합도", f"{rec['style_fit']}/100")
                        st.metric("현재가", f"${rec['current_price']:.2f}")
                    
                    # 상세 분석 버튼
                    if st.button(f"📊 {rec['ticker']} 상세 분석", key=f"detail_{rec['ticker']}"):
                        st.session_state.analysis_ticker = rec['ticker']
                        st.info(f"'{rec['ticker']}' 종목을 '종목 분석' 페이지에서 확인하세요.")
        else:
            st.warning("추천할 종목이 없습니다. 필터 조건을 변경해 보세요.")
    
    else:
        st.info("""
        🎯 **AI 추천 종목 사용 방법:**
        
        1. 투자 스타일을 선택하세요
        2. 스크리닝 대상을 선택하세요 (S&P 500 또는 직접 입력)
        3. '추천 종목 찾기' 버튼을 클릭하세요
        
        **투자 스타일:**
        - 공격적 성장형: 고성장 기술주 선호
        - 안정적 배당형: 배당 수익률 중시
        - 가치 투자형: 저평가 종목 발굴
        - 모멘텀 트레이딩형: 단기 상승 모멘텀
        - 균형 포트폴리오형: 성장과 안정성 균형
        """)
