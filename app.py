"""
AI 트레이딩 어시스턴트 - 메인 앱
Streamlit 기반 웹 서비스
"""
import streamlit as st
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 페이지 설정
st.set_page_config(
    page_title="AI 트레이딩 어시스턴트",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바
with st.sidebar:
    st.title("📈 AI 트레이딩 어시스턴트")
    st.markdown("---")
    
    # 네비게이션
    page = st.radio(
        "메뉴",
        [
            "🏠 대시보드",
            "📊 종목 분석",
            "🎯 AI 추천 종목",
            "💼 포트폴리오 평가",
            "📅 경제 캘린더",
            "💬 AI 채팅",
            "⚙️ 설정"
        ]
    )
    
    st.markdown("---")
    st.caption("v2.0 | Made with ❤️")

# 메인 컨텐츠
if page == "🏠 대시보드":
    from src.ui.pages import dashboard
    dashboard.show()

elif page == "📊 종목 분석":
    from src.ui.pages import stock_analysis
    stock_analysis.show()

elif page == "🎯 AI 추천 종목":
    from src.ui.pages import recommendations
    recommendations.show()

elif page == "💼 포트폴리오 평가":
    from src.ui.pages import portfolio
    portfolio.show()

elif page == "📅 경제 캘린더":
    from src.ui.pages import calendar_page
    calendar_page.show()

elif page == "💬 AI 채팅":
    from src.ui.pages import chat
    chat.show()

elif page == "⚙️ 설정":
    from src.ui.pages import settings
    settings.show()
