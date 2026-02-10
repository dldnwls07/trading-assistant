"""
대시보드 페이지
시장 개요 및 주요 지표
"""
import streamlit as st
import yfinance as yf
from datetime import datetime
from src.data.fred_provider import FREDDataProvider
from src.agents.event_calendar import EventCalendar

def show():
    st.title("🏠 대시보드")
    st.markdown("### 시장 개요 및 주요 지표")
    
    # 거시 경제 지표
    st.markdown("---")
    st.subheader("📈 거시 경제 지표")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        try:
            fred = FREDDataProvider()
            macro_analysis = fred.analyze_macro_conditions()
            
            # 점수 표시
            score = macro_analysis['score']
            grade = macro_analysis['grade']
            
            # 점수에 따른 색상
            if score >= 70:
                color = "green"
            elif score >= 50:
                color = "orange"
            else:
                color = "red"
            
            st.markdown(f"### 거시 경제 점수: <span style='color:{color}; font-size:2em'>{score}/100</span> ({grade})", unsafe_allow_html=True)
            
            # 상세 정보
            with st.expander("📊 상세 분석"):
                for detail in macro_analysis['details']:
                    st.write(detail)
                
                st.markdown("**주요 리스크:**")
                for risk in macro_analysis['risks']:
                    st.write(f"• {risk}")
            
            st.info(macro_analysis['recommendation'])
            
        except Exception as e:
            st.warning("⚠️ FRED API 키가 설정되지 않았습니다. 설정 페이지에서 API 키를 입력하세요.")
            st.caption(f"오류: {str(e)}")
    
    with col2:
        # 주요 지수
        st.markdown("**주요 지수**")
        
        indices = {
            "S&P 500": "^GSPC",
            "NASDAQ": "^IXIC",
            "다우존스": "^DJI"
        }
        
        for name, ticker in indices.items():
            try:
                data = yf.Ticker(ticker)
                hist = data.history(period="2d")
                if len(hist) >= 2:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2]
                    change = ((current - prev) / prev) * 100
                    
                    color = "green" if change > 0 else "red"
                    arrow = "▲" if change > 0 else "▼"
                    
                    st.markdown(f"**{name}**: ${current:,.2f} <span style='color:{color}'>{arrow} {abs(change):.2f}%</span>", unsafe_allow_html=True)
            except:
                st.write(f"**{name}**: 데이터 로딩 실패")
    
    # 이번 주 주요 이벤트
    st.markdown("---")
    st.subheader("📅 이번 주 주요 일정")
    
    try:
        calendar = EventCalendar()
        cal_data = calendar.get_calendar()
        
        this_week = cal_data['summary']['this_week']
        
        if this_week:
            for event in this_week[:5]:
                importance = event.get('importance', 'low')
                
                if importance == 'critical':
                    icon = "🚨"
                elif importance == 'high':
                    icon = "⚠️"
                else:
                    icon = "📌"
                
                st.write(f"{icon} **{event['date']}**: {event['title']}")
        else:
            st.info("이번 주 주요 일정이 없습니다.")
            
    except Exception as e:
        st.error(f"캘린더 로딩 실패: {e}")
    
    # 빠른 분석
    st.markdown("---")
    st.subheader("🔍 빠른 종목 분석")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker_input = st.text_input("종목 심볼 입력 (예: AAPL, MSFT)", "AAPL")
    
    with col2:
        st.write("")
        st.write("")
        analyze_btn = st.button("분석하기", type="primary")
    
    if analyze_btn and ticker_input:
        with st.spinner(f"{ticker_input} 분석 중..."):
            try:
                from src.agents.multi_timeframe import MultiTimeframeAnalyzer
                
                analyzer = MultiTimeframeAnalyzer()
                result = analyzer.analyze_all_timeframes(ticker_input.upper())
                
                # 결과 표시
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "단기 점수",
                        f"{result['short_term']['score']}/100" if result['short_term'] else "N/A",
                        result['short_term']['signal'] if result['short_term'] else ""
                    )
                
                with col2:
                    st.metric(
                        "중기 점수",
                        f"{result['medium_term']['score']}/100" if result['medium_term'] else "N/A",
                        result['medium_term']['signal'] if result['medium_term'] else ""
                    )
                
                with col3:
                    st.metric(
                        "장기 점수",
                        f"{result['long_term']['score']}/100" if result['long_term'] else "N/A",
                        result['long_term']['signal'] if result['long_term'] else ""
                    )
                
                # 컨센서스
                st.success(f"**컨센서스:** {result['consensus']['consensus']}")
                
                # 상세 분석 링크
                st.info("💡 더 상세한 분석을 원하시면 '종목 분석' 페이지를 이용하세요.")
                
            except Exception as e:
                st.error(f"분석 실패: {e}")
    
    # 푸터
    st.markdown("---")
    st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
