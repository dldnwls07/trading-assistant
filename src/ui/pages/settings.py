"""
설정 페이지
"""
import streamlit as st
import os
from pathlib import Path

def show():
    st.title("⚙️ 설정")
    st.markdown("### API 키 및 환경 설정")
    
    # API 키 설정
    st.subheader("🔑 API 키 설정")
    
    env_path = Path(".env")
    
    # HF Token
    st.markdown("#### Hugging Face API Token")
    st.caption("AI 리포트 생성 및 채팅 기능에 필요합니다.")
    
    hf_token = st.text_input(
        "HF_TOKEN",
        value=os.getenv("HF_TOKEN", ""),
        type="password",
        help="https://huggingface.co/settings/tokens 에서 발급"
    )
    
    if st.button("HF Token 저장"):
        try:
            # .env 파일 업데이트
            if env_path.exists():
                with open(env_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                updated = False
                for i, line in enumerate(lines):
                    if line.startswith('HF_TOKEN='):
                        lines[i] = f'HF_TOKEN="{hf_token}"\n'
                        updated = True
                        break
                
                if not updated:
                    lines.append(f'HF_TOKEN="{hf_token}"\n')
                
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                st.success("✅ HF Token이 저장되었습니다. 앱을 재시작하세요.")
            else:
                st.error(".env 파일을 찾을 수 없습니다.")
        except Exception as e:
            st.error(f"저장 실패: {e}")
    
    st.markdown("---")
    
    # FRED API Key
    st.markdown("#### FRED API Key")
    st.caption("거시 경제 지표 수집에 필요합니다 (선택사항).")
    
    fred_key = st.text_input(
        "FRED_API_KEY",
        value=os.getenv("FRED_API_KEY", ""),
        type="password",
        help="https://fred.stlouisfed.org/docs/api/api_key.html 에서 발급"
    )
    
    if st.button("FRED Key 저장"):
        try:
            if env_path.exists():
                with open(env_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                updated = False
                for i, line in enumerate(lines):
                    if line.startswith('FRED_API_KEY='):
                        lines[i] = f'FRED_API_KEY="{fred_key}"\n'
                        updated = True
                        break
                
                if not updated:
                    lines.append(f'FRED_API_KEY="{fred_key}"\n')
                
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                st.success("✅ FRED API Key가 저장되었습니다. 앱을 재시작하세요.")
            else:
                st.error(".env 파일을 찾을 수 없습니다.")
        except Exception as e:
            st.error(f"저장 실패: {e}")
    
    st.markdown("---")
    
    # Gemini API Key (추천!)
    st.markdown("#### 🌟 Google Gemini API Key (추천!)")
    st.caption("AI 채팅 기능에 사용됩니다. 무료이며 매우 똑똑합니다!")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        gemini_key = st.text_input(
            "GEMINI_API_KEY",
            value=os.getenv("GEMINI_API_KEY", ""),
            type="password",
            help="https://aistudio.google.com/app/apikey 에서 무료 발급"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("Gemini Key 저장", type="primary"):
            try:
                if env_path.exists():
                    with open(env_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    updated = False
                    for i, line in enumerate(lines):
                        if line.startswith('GEMINI_API_KEY='):
                            lines[i] = f'GEMINI_API_KEY="{gemini_key}"\n'
                            updated = True
                            break
                    
                    if not updated:
                        lines.append(f'GEMINI_API_KEY="{gemini_key}"\n')
                    
                    with open(env_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    
                    st.success("✅ Gemini API Key가 저장되었습니다. 앱을 재시작하세요.")
                else:
                    st.error(".env 파일을 찾을 수 없습니다.")
            except Exception as e:
                st.error(f"저장 실패: {e}")
    
    st.info("""
    💡 **Gemini API 추천 이유:**
    - 완전 무료 (월 1,500회 요청)
    - 매우 똑똑하고 자연스러운 대화
    - 발급 즉시 사용 가능
    - Hugging Face보다 훨씬 빠름
    """)
    
    # 투자 스타일 설정
    st.markdown("---")
    st.subheader("👤 투자 스타일 설정")
    
    from src.agents.profiler import InvestorProfiler
    
    profiler = InvestorProfiler()
    
    current_style = profiler.get_style()
    
    if current_style:
        style_info = profiler.get_style_info(current_style)
        st.success(f"현재 스타일: **{style_info['name']}**")
        st.write(style_info['description'])
    else:
        st.info("아직 투자 스타일이 설정되지 않았습니다.")
    
    if st.button("투자 스타일 설문 시작"):
        st.session_state.show_survey = True
    
    if st.session_state.get('show_survey', False):
        st.markdown("#### 📋 투자 성향 설문")
        
        with st.form("investment_survey"):
            q1 = st.slider(
                "1. 투자 위험 감수 정도 (1=매우 보수적, 5=매우 공격적)",
                1, 5, 3
            )
            
            q2 = st.selectbox(
                "2. 투자 기간",
                ["short", "medium", "long"],
                format_func=lambda x: {"short": "단기 (1년 이하)", "medium": "중기 (1~3년)", "long": "장기 (3년 이상)"}[x]
            )
            
            q3 = st.slider(
                "3. 손실 감내 정도 (1=10% 손실도 힘듦, 5=30% 손실도 견딤)",
                1, 5, 3
            )
            
            q4 = st.selectbox(
                "4. 투자 목표",
                ["growth", "income", "preservation", "balanced"],
                format_func=lambda x: {"growth": "자본 성장", "income": "배당 수익", "preservation": "원금 보존", "balanced": "균형"}[x]
            )
            
            q5 = st.selectbox(
                "5. 거래 빈도",
                ["daily", "weekly", "monthly", "rarely"],
                format_func=lambda x: {"daily": "매일", "weekly": "주 1회", "monthly": "월 1회", "rarely": "거의 안 함"}[x]
            )
            
            submit = st.form_submit_button("설문 제출", type="primary")
            
            if submit:
                survey_answers = {
                    "risk_tolerance": q1,
                    "time_horizon": q2,
                    "loss_tolerance": q3,
                    "investment_goal": q4,
                    "trading_frequency": q5
                }
                
                style = profiler.create_profile_from_survey(survey_answers)
                style_info = profiler.get_style_info(style)
                
                st.success(f"✅ 당신의 투자 스타일: **{style_info['name']}**")
                st.write(style_info['description'])
                
                st.session_state.show_survey = False
                st.rerun()
    
    # 시스템 정보
    st.markdown("---")
    st.subheader("ℹ️ 시스템 정보")
    
    st.write(f"**버전:** v2.0")
    st.write(f"**Python:** {os.sys.version.split()[0]}")
    
    # 캐시 초기화
    if st.button("🗑️ 캐시 초기화"):
        st.cache_data.clear()
        st.success("✅ 캐시가 초기화되었습니다.")
    
    # 도움말
    st.markdown("---")
    st.subheader("📚 도움말")
    
    st.markdown("""
    **API 키 발급 방법:**
    
    1. **Google Gemini API Key (추천!) 🌟**
       - https://aistudio.google.com/app/apikey 접속
       - Google 계정으로 로그인
       - "Create API Key" 클릭
       - 생성된 키 복사
       - **완전 무료! (월 1,500회)**
    
    2. **Hugging Face Token**
       - https://huggingface.co/settings/tokens 접속
       - "New token" 클릭
       - Read 권한 선택
       - 생성된 토큰 복사
    
    3. **FRED API Key**
       - https://fred.stlouisfed.org/ 회원가입
       - https://fred.stlouisfed.org/docs/api/api_key.html 에서 API 키 발급
       - 생성된 키 복사
    
    **문제 해결:**
    - API 키 저장 후 반드시 앱을 재시작하세요
    - 오류 발생 시 캐시를 초기화해 보세요
    - 자세한 내용은 USER_GUIDE.md를 참조하세요
    """)
