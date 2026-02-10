"""
종목 분석 페이지
다중 시간 프레임 종합 분석
"""
import streamlit as st
from src.agents.multi_timeframe import MultiTimeframeAnalyzer
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

def show():
    st.title("📊 종목 분석")
    st.markdown("### 다중 시간 프레임 종합 분석")
    
    # 입력
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input("종목 심볼 입력", "AAPL", key="analysis_ticker")
    
    with col2:
        st.write("")
        st.write("")
        analyze_btn = st.button("분석 시작", type="primary", use_container_width=True)
    
    if analyze_btn and ticker:
        with st.spinner(f"{ticker.upper()} 분석 중... (약 10초 소요)"):
            try:
                analyzer = MultiTimeframeAnalyzer()
                result = analyzer.analyze_all_timeframes(ticker.upper())
                
                st.session_state.analysis_result = result
                st.success("✅ 분석 완료!")
                
            except Exception as e:
                st.error(f"분석 실패: {e}")
                return
    
    # 분석 결과 표시
    if 'analysis_result' in st.session_state:
        result = st.session_state.analysis_result
        
        # 헤더
        st.markdown("---")
        st.subheader(f"📈 {result['ticker']} 분석 결과")
        st.caption(f"분석 시간: {result['timestamp']}")
        
        # 컨센서스
        consensus = result['consensus']
        st.markdown(f"### {consensus['consensus']}")
        st.progress(consensus['confidence'] / 100)
        st.caption(f"확신도: {consensus['confidence']}% | 평균 점수: {consensus['avg_score']:.1f}/100")
        
        with st.expander("📝 종합 추천"):
            st.write(consensus['recommendation'])
        
        # 시간 프레임별 분석
        st.markdown("---")
        st.subheader("⏱️ 시간 프레임별 분석")
        
        tabs = st.tabs(["단기 (데이 트레이딩)", "중기 (스윙)", "장기 (포지션)"])
        
        timeframes = [
            ('short_term', result['short_term']),
            ('medium_term', result['medium_term']),
            ('long_term', result['long_term'])
        ]
        
        for tab, (tf_key, tf_data) in zip(tabs, timeframes):
            with tab:
                if tf_data:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("점수", f"{tf_data.get('score', 'N/A')}/100")
                    
                    with col2:
                        st.metric("신호", tf_data.get('signal', 'N/A'))
                    
                    with col3:
                        current_price = tf_data.get('current_price', 0)
                        if current_price > 0:
                            st.metric("현재가", f"${current_price:.2f}")
                        else:
                            st.metric("현재가", "N/A")
                    
                    # 매수/매도 타점
                    st.markdown("#### 💰 매수/매도 타점")
                    
                    entry_points = tf_data.get('entry_points', {})
                    
                    if entry_points:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**매수 존:**")
                            for zone in entry_points.get('buy_zone', []):
                                st.write(f"• ${zone['price']:.2f} - {zone['reason']}")
                        
                        with col2:
                            st.markdown("**매도 존:**")
                            for zone in entry_points.get('sell_zone', []):
                                st.write(f"• ${zone['price']:.2f} - {zone['reason']}")
                        
                        st.markdown("**손절/익절:**")
                        st.write(f"• 손절가: ${entry_points.get('stop_loss', 0):.2f}")
                        st.write(f"• 목표가: ${entry_points.get('take_profit', 0):.2f}")
                        st.write(f"• 리스크/보상 비율: {entry_points.get('risk_reward_ratio', 0):.2f}")
                        
                        if 'fibonacci_levels' in entry_points:
                            with st.expander("📐 피보나치 되돌림 레벨"):
                                for level, price in entry_points['fibonacci_levels'].items():
                                    st.write(f"• {level}: ${price:.2f}")
                    
                    # 감지된 패턴
                    patterns = tf_data.get('patterns', [])
                    if patterns:
                        st.markdown("#### 📊 감지된 차트 패턴")
                        
                        for i, pattern in enumerate(patterns[:5], 1):
                            with st.expander(f"{i}. {pattern['name']} (신뢰도: {pattern['reliability']}/5.0)"):
                                st.write(f"**타입:** {pattern['type']}")
                                st.write(f"**확신도:** {pattern.get('confidence', 'N/A')}%")
                                st.write(f"**설명:** {pattern.get('desc', '')}")
                                if pattern.get('target'):
                                    st.write(f"**목표가:** ${pattern['target']:.2f}")
                    
                    # 특화 인사이트
                    if 'specialized_insights' in tf_data:
                        with st.expander("🔍 특화 분석"):
                            insights = tf_data['specialized_insights']
                            for key, value in insights.items():
                                st.write(f"**{key}:** {value}")
                    
                    # 추천
                    st.info(tf_data.get('recommendation', ''))
                else:
                    st.warning("이 시간 프레임의 데이터가 부족합니다.")
        
        # 전체 패턴 목록
        if result['all_patterns']:
            st.markdown("---")
            st.subheader("🎯 전체 감지된 패턴")
            
            st.write(f"총 {len(result['all_patterns'])}개 패턴 감지")
            
            # 패턴 테이블
            pattern_data = []
            for p in result['all_patterns'][:10]:
                pattern_data.append({
                    "패턴": p['name'],
                    "타입": p['type'],
                    "신뢰도": f"{p['reliability']}/5.0",
                    "확신도": f"{p.get('confidence', 'N/A')}%",
                    "시간프레임": p.get('timeframe', 'N/A')
                })
            
            st.table(pattern_data)
        
        # 차트 (간단한 가격 차트)
        st.markdown("---")
        st.subheader("📈 가격 차트")
        
        try:
            ticker_obj = yf.Ticker(result['ticker'])
            hist = ticker_obj.history(period="6mo")
            
            fig = go.Figure()
            
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name='가격'
            ))
            
            fig.update_layout(
                title=f"{result['ticker']} 6개월 차트",
                yaxis_title='가격 (USD)',
                xaxis_title='날짜',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.warning(f"차트 로딩 실패: {e}")
    
    else:
        st.info("""
        📊 **종목 분석 사용 방법:**
        
        1. 종목 심볼을 입력하세요 (예: AAPL, MSFT, GOOGL)
        2. '분석 시작' 버튼을 클릭하세요
        3. 단기/중기/장기 시간 프레임별 분석 결과를 확인하세요
        
        **제공 정보:**
        - 시간 프레임별 점수 및 신호
        - 매수/매도 타점 (피보나치, ATR 기반)
        - 30개 이상 차트 패턴 자동 감지
        - 리스크/보상 비율
        - 종합 컨센서스
        """)
