"""
경제 캘린더 페이지 (개선된 UI)
FOMC, CPI, 실적 발표 등 주요 일정
"""
import streamlit as st
from src.agents.event_calendar import EventCalendar
from datetime import datetime, timedelta
import pandas as pd

def show():
    st.title("📅 경제 이벤트 캘린더")
    st.markdown("### FOMC, CPI, 실적 발표 등 주요 일정")
    
    # 필터 옵션
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input(
            "시작일",
            value=datetime.now(),
            key="cal_start"
        )
    
    with col2:
        end_date = st.date_input(
            "종료일",
            value=datetime.now() + timedelta(days=90),
            key="cal_end"
        )
    
    with col3:
        ticker_input = st.text_input(
            "종목 심볼 (선택사항, 쉼표로 구분)",
            placeholder="AAPL, MSFT, GOOGL",
            key="cal_tickers"
        )
    
    # 캘린더 생성
    if st.button("📅 캘린더 생성", type="primary", use_container_width=True):
        with st.spinner("이벤트 수집 중..."):
            try:
                calendar = EventCalendar()
                
                # 종목 리스트 파싱
                tickers = None
                if ticker_input:
                    tickers = [t.strip().upper() for t in ticker_input.split(",")]
                
                cal_data = calendar.get_calendar(
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d"),
                    tickers=tickers
                )
                
                st.session_state.calendar_data = cal_data
                st.success(f"✅ {cal_data['total_events']}개 이벤트 로드 완료!")
                
            except Exception as e:
                st.error(f"캘린더 생성 실패: {e}")
    
    # 캘린더 데이터 표시
    if 'calendar_data' in st.session_state:
        cal_data = st.session_state.calendar_data
        
        # 요약 통계 (카드 스타일)
        st.markdown("---")
        st.subheader("📊 요약 통계")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📌 총 이벤트", cal_data['total_events'])
        
        with col2:
            critical_count = cal_data['summary']['by_importance'].get('critical', 0)
            st.metric("🚨 중요 이벤트", critical_count)
        
        with col3:
            this_week_count = len(cal_data['summary']['this_week'])
            st.metric("📆 이번 주", this_week_count)
        
        with col4:
            macro_count = cal_data['summary']['by_category'].get('macro', 0)
            st.metric("🌍 거시 경제", macro_count)
        
        # 이번 주 주요 일정 (카드 스타일)
        if cal_data['summary']['this_week']:
            st.markdown("---")
            st.subheader("🔔 이번 주 주요 일정")
            
            for event in cal_data['summary']['this_week']:
                importance = event.get('importance', 'low')
                
                # 중요도에 따른 스타일
                if importance == 'critical':
                    icon = "🚨"
                    bg_color = "#ffe6e6"
                    border_color = "#ff4d4d"
                elif importance == 'high':
                    icon = "⚠️"
                    bg_color = "#fff4e6"
                    border_color = "#ff9933"
                else:
                    icon = "📌"
                    bg_color = "#e6f3ff"
                    border_color = "#4da6ff"
                
                # 카드 스타일로 표시
                st.markdown(f"""
                <div style="
                    background-color: {bg_color};
                    border-left: 4px solid {border_color};
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                ">
                    <strong>{icon} {event['date']}</strong><br>
                    <span style="font-size: 1.1em;">{event['title']}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # 다가오는 중요 이벤트 (타임라인 스타일)
        if cal_data['summary']['upcoming_critical']:
            st.markdown("---")
            st.subheader("⚠️ 다가오는 중요 이벤트")
            
            for event in cal_data['summary']['upcoming_critical'][:10]:
                days_until = event['days_until']
                
                if days_until == 0:
                    day_text = "오늘"
                    badge_color = "#ff4d4d"
                elif days_until == 1:
                    day_text = "내일"
                    badge_color = "#ff9933"
                elif days_until <= 7:
                    day_text = f"D-{days_until}"
                    badge_color = "#ffcc00"
                else:
                    day_text = f"D-{days_until}"
                    badge_color = "#4da6ff"
                
                st.markdown(f"""
                <div style="
                    display: flex;
                    align-items: center;
                    padding: 10px;
                    margin: 5px 0;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                ">
                    <span style="
                        background-color: {badge_color};
                        color: white;
                        padding: 5px 10px;
                        border-radius: 15px;
                        font-weight: bold;
                        margin-right: 15px;
                        min-width: 60px;
                        text-align: center;
                    ">{day_text}</span>
                    <span><strong>{event['date']}</strong>: {event['title']}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # 전체 이벤트 목록 (개선된 테이블)
        st.markdown("---")
        st.subheader("📋 전체 이벤트 목록")
        
        # 필터
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            category_filter = st.multiselect(
                "카테고리 필터",
                options=list(cal_data['summary']['by_category'].keys()),
                default=list(cal_data['summary']['by_category'].keys()),
                help="표시할 이벤트 카테고리를 선택하세요"
            )
        
        with filter_col2:
            importance_filter = st.multiselect(
                "중요도 필터",
                options=['critical', 'high', 'medium', 'low'],
                default=['critical', 'high', 'medium', 'low'],
                format_func=lambda x: {
                    'critical': '🚨 매우 중요',
                    'high': '⚠️ 중요',
                    'medium': '📌 보통',
                    'low': '📎 낮음'
                }[x]
            )
        
        # 필터링된 이벤트
        filtered_events = [
            e for e in cal_data['events']
            if e.get('category', 'other') in category_filter
            and e.get('importance', 'low') in importance_filter
        ]
        
        # 개선된 이벤트 카드 표시
        if filtered_events:
            st.write(f"**총 {len(filtered_events)}개 이벤트**")
            
            # 날짜별로 그룹화
            events_by_date = {}
            for event in filtered_events:
                date = event['date']
                if date not in events_by_date:
                    events_by_date[date] = []
                events_by_date[date].append(event)
            
            # 날짜순 정렬
            sorted_dates = sorted(events_by_date.keys())
            
            # 날짜별로 표시
            for date in sorted_dates[:20]:  # 최대 20일치만 표시
                st.markdown(f"### 📅 {date}")
                
                for event in events_by_date[date]:
                    importance = event.get('importance', 'low')
                    
                    # 중요도 아이콘
                    if importance == 'critical':
                        icon = "🚨"
                        badge = "매우 중요"
                        badge_color = "#ff4d4d"
                    elif importance == 'high':
                        icon = "⚠️"
                        badge = "중요"
                        badge_color = "#ff9933"
                    elif importance == 'medium':
                        icon = "📌"
                        badge = "보통"
                        badge_color = "#4da6ff"
                    else:
                        icon = "📎"
                        badge = "낮음"
                        badge_color = "#999999"
                    
                    # 이벤트 카드
                    with st.expander(f"{icon} {event['title']} ({event['type']})"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**설명:** {event.get('description', '')}")
                            st.markdown(f"**영향:** {event.get('impact', '')}")
                        
                        with col2:
                            st.markdown(f"""
                            <div style="
                                background-color: {badge_color};
                                color: white;
                                padding: 5px 10px;
                                border-radius: 5px;
                                text-align: center;
                                font-weight: bold;
                            ">{badge}</div>
                            """, unsafe_allow_html=True)
                
                st.markdown("---")
            
            # CSV 다운로드
            st.markdown("### 📥 데이터 다운로드")
            
            df_data = []
            for event in filtered_events:
                df_data.append({
                    "날짜": event['date'],
                    "종류": event['type'],
                    "제목": event['title'],
                    "중요도": event.get('importance', 'low'),
                    "카테고리": event.get('category', 'other'),
                    "설명": event.get('description', ''),
                    "영향": event.get('impact', '')
                })
            
            df = pd.DataFrame(df_data)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            
            st.download_button(
                label="📥 CSV 파일 다운로드",
                data=csv,
                file_name=f"economic_calendar_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("필터 조건에 맞는 이벤트가 없습니다.")
    
    else:
        # 초기 안내 (개선된 스타일)
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin: 20px 0;
        ">
            <h3 style="color: white;">📅 경제 이벤트 캘린더 사용 방법</h3>
            <ol style="font-size: 1.1em; line-height: 1.8;">
                <li>시작일과 종료일을 선택하세요</li>
                <li>(선택사항) 추적할 종목 심볼을 입력하세요</li>
                <li>'캘린더 생성' 버튼을 클릭하세요</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📊 포함 이벤트")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **거시 경제 지표:**
            - 🏦 FOMC 회의 (연 8회)
            - 📊 CPI 발표 (매월)
            - 💼 고용지표 NFP (매월)
            - 📈 GDP 발표 (분기별)
            """)
        
        with col2:
            st.markdown("""
            **기업 이벤트:**
            - 💰 실적 발표
            - 💵 배당락일
            - 📢 주요 공시
            """)
    
    # 푸터
    st.markdown("---")
    st.caption("⚠️ 이벤트 일정은 예상 날짜이며 변경될 수 있습니다.")
