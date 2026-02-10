"""
포트폴리오 평가 페이지
"""
import streamlit as st
from src.agents.portfolio_analyzer import PortfolioAnalyzer
import pandas as pd

def show():
    st.title("💼 포트폴리오 AI 평가")
    st.markdown("### 보유 종목 분석 및 리밸런싱 제안")
    
    # 포트폴리오 입력
    st.subheader("📝 보유 종목 입력")
    
    # 세션 상태 초기화
    if 'portfolio_holdings' not in st.session_state:
        st.session_state.portfolio_holdings = []
    
    # 입력 폼
    with st.form("add_holding"):
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            ticker = st.text_input("종목 심볼", "AAPL")
        with col2:
            shares = st.number_input("보유 수량", min_value=0.01, value=10.0, step=0.01)
        with col3:
            avg_price = st.number_input("평균 단가", min_value=0.01, value=150.0, step=0.01)
        with col4:
            st.write("")
            st.write("")
            add_btn = st.form_submit_button("➕ 추가", use_container_width=True)
        
        if add_btn and ticker:
            st.session_state.portfolio_holdings.append({
                "ticker": ticker.upper(),
                "shares": shares,
                "avg_price": avg_price
            })
            st.success(f"✅ {ticker.upper()} 추가됨!")
            st.rerun()
    
    # 현재 포트폴리오 표시
    if st.session_state.portfolio_holdings:
        st.markdown("---")
        st.subheader("📊 현재 포트폴리오")
        
        df = pd.DataFrame(st.session_state.portfolio_holdings)
        df['투자금액'] = df['shares'] * df['avg_price']
        
        st.dataframe(df, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ 전체 초기화"):
                st.session_state.portfolio_holdings = []
                st.rerun()
        
        with col2:
            if st.button("📊 AI 평가 시작", type="primary", use_container_width=True):
                with st.spinner("포트폴리오 분석 중... (시간이 걸릴 수 있습니다)"):
                    try:
                        analyzer = PortfolioAnalyzer()
                        result = analyzer.analyze_portfolio(st.session_state.portfolio_holdings)
                        
                        st.session_state.portfolio_result = result
                        st.success("✅ 분석 완료!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"분석 실패: {e}")
    
    # 분석 결과 표시
    if 'portfolio_result' in st.session_state:
        result = st.session_state.portfolio_result
        
        st.markdown("---")
        st.subheader("📈 분석 결과")
        
        # 종합 점수
        score = result['portfolio_score']
        
        if score >= 70:
            color = "green"
            grade = "우수"
        elif score >= 50:
            color = "orange"
            grade = "양호"
        else:
            color = "red"
            grade = "개선 필요"
        
        st.markdown(f"### 포트폴리오 점수: <span style='color:{color}; font-size:2em'>{score:.1f}/100</span> ({grade})", unsafe_allow_html=True)
        
        # 주요 지표
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 가치", f"${result['total_value']:,.2f}")
        
        with col2:
            pnl = result['total_profit_loss']
            pnl_pct = result['total_profit_loss_pct']
            st.metric("총 손익", f"${pnl:,.2f}", f"{pnl_pct:+.2f}%")
        
        with col3:
            st.metric("분산도", result['diversification']['grade'])
        
        with col4:
            st.metric("리스크 밸런스", f"{result['risk_balance']['score']}/100")
        
        # 보유 종목 상세
        st.markdown("---")
        st.subheader("📋 보유 종목 상세")
        
        holdings_df = pd.DataFrame(result['holdings'])
        
        # 주요 컬럼만 표시
        display_df = holdings_df[[
            'ticker', 'shares', 'current_price', 'position_value',
            'profit_loss_pct', 'weight', 'ai_score', 'signal'
        ]].copy()
        
        display_df.columns = [
            '종목', '수량', '현재가', '평가액',
            '수익률(%)', '비중(%)', 'AI점수', '신호'
        ]
        
        st.dataframe(display_df, use_container_width=True)
        
        # 분산도 분석
        st.markdown("---")
        st.subheader("🎯 분산도 분석")
        
        div = result['diversification']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("HHI 지수", f"{div['hhi']}")
            st.caption("낮을수록 분산이 잘 됨 (2000 이하 권장)")
        
        with col2:
            st.metric("섹터 수", len(div['sector_distribution']))
        
        st.info(div['message'])
        
        # 리스크 밸런스
        st.markdown("---")
        st.subheader("⚖️ 리스크 밸런스")
        
        risk = result['risk_balance']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("고위험", f"{risk['high_risk_pct']:.1f}%")
        
        with col2:
            st.metric("중위험", f"{risk['medium_risk_pct']:.1f}%")
        
        with col3:
            st.metric("저위험", f"{risk['low_risk_pct']:.1f}%")
        
        st.info(risk['message'])
        
        # 리밸런싱 제안
        st.markdown("---")
        st.subheader("🔄 AI 리밸런싱 제안")
        
        rebal = result['rebalancing']
        
        # 매도 추천
        if rebal['sell']:
            st.markdown("#### 🔴 매도 추천")
            for suggestion in rebal['sell']:
                with st.expander(f"{suggestion['ticker']} - {suggestion['action']}"):
                    st.write(f"**이유:** {suggestion['reason']}")
        
        # 매수 추천
        if rebal['buy']:
            st.markdown("#### 🟢 매수 추천")
            for suggestion in rebal['buy']:
                with st.expander(f"{suggestion['ticker']} - {suggestion['action']}"):
                    st.write(f"**이유:** {suggestion['reason']}")
        
        # 비중 조정
        if rebal['adjust']:
            st.markdown("#### 🟡 비중 조정")
            for suggestion in rebal['adjust']:
                with st.expander(f"{suggestion['ticker']} - {suggestion['action']}"):
                    st.write(f"**이유:** {suggestion['reason']}")
        
        if not rebal['sell'] and not rebal['buy'] and not rebal['adjust']:
            st.success("✅ 현재 포트폴리오가 양호합니다. 리밸런싱이 필요하지 않습니다.")
        
        # 종합 요약
        st.markdown("---")
        st.subheader("📝 종합 요약")
        st.write(result['summary'])
    
    else:
        if not st.session_state.portfolio_holdings:
            st.info("""
            💼 **포트폴리오 AI 평가 사용 방법:**
            
            1. 보유 종목을 하나씩 추가하세요
            2. 'AI 평가 시작' 버튼을 클릭하세요
            3. 분석 결과 및 리밸런싱 제안을 확인하세요
            
            **평가 항목:**
            - 종합 점수 (가중 평균)
            - 분산도 (HHI 지수)
            - 리스크 밸런스
            - 투자 스타일 일치도
            - AI 리밸런싱 제안
            """)
