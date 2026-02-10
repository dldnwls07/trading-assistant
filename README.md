# 🚀 AI Trading Assistant v2.0

**AI 기반 주식 분석 플랫폼 - 웹, 모바일, 확장프로그램 지원**

[![FastAPI](https://img.shields.io/badge/FastAPI-2.0-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react)](https://react.dev/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ 주요 기능

### 📊 종목 분석
- **다중 시간 프레임 분석** (1m ~ 1y)
- **30+ 차트 패턴 자동 감지** (헤드앤숄더, 더블바텀 등)
- **AI 점수 시스템** (0~100점)
- **매수/매도 타점 제시**
- **실시간 차트** (TradingView Lightweight Charts)

### 💬 AI 채팅
- **Google Gemini Flash** 통합 (무료!)
- **자연스러운 대화형 투자 상담**
- **컨텍스트 인식** (분석 결과 기반 답변)
- **API 키 없이도 작동** (고급 룰 기반 시스템)

### 📅 경제 캘린더
- **FOMC, CPI, 고용지표** 등 주요 일정
- **기업 실적 발표일**
- **중요도별 필터링**
- **D-Day 알림**

### 💼 포트폴리오 분석
- **AI 기반 포트폴리오 평가**
- **리스크 분석**
- **리밸런싱 제안**
- **섹터 분산도 분석**

### 🔍 AI 추천 종목
- **투자 스타일별 맞춤 추천** (공격적/성장/균형/보수적)
- **급등/급락 종목 모니터링**
- **실시간 스크리닝**

---

## 🎯 플랫폼 지원

### ✅ 현재 지원
- **웹 앱** (React + FastAPI)
- **Streamlit 프로토타입** (내부 테스트용)

### 🚧 개발 예정
- **모바일 앱** (React Native)
- **Chrome 확장프로그램**
- **데스크톱 앱** (Electron)

---

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/trading-assistant.git
cd trading-assistant

# Python 패키지 설치
pip install -r requirements.txt

# 프론트엔드 패키지 설치
cd frontend
npm install
cd ..
```

### 2. 환경 변수 설정

`.env` 파일 생성:

```bash
# Google Gemini API Key (무료, 추천!)
GEMINI_API_KEY="your-gemini-api-key"

# FRED API Key (거시 경제 지표)
FRED_API_KEY="your-fred-api-key"

# Hugging Face Token (선택사항)
HF_TOKEN="your-hf-token"
```

**API 키 발급:**
- **Gemini**: https://aistudio.google.com/app/apikey (1분, 무료)
- **FRED**: https://fred.stlouisfed.org/docs/api/api_key.html (무료)

### 3. 서버 실행

#### 방법 1: 배치 파일 (추천)

**웹 앱 (FastAPI + React):**
```bash
start_web.bat
```

**Streamlit 프로토타입:**
```bash
start.bat
```

#### 방법 2: 수동 실행

**웹 앱:**
```bash
# 백엔드
uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000

# 프론트엔드 (새 터미널)
cd frontend
npm run dev
```

**Streamlit:**
```bash
streamlit run app.py
```

### 4. 접속

- **웹 앱**: http://localhost:5173
- **API 문서**: http://localhost:8000/docs
- **Streamlit**: http://localhost:8501

---

## 📚 문서

- **[API Reference v2.0](API_v2_REFERENCE.md)** - 전체 API 엔드포인트
- **[User Guide](USER_GUIDE.md)** - 사용자 가이드
- **[API Reference v1.0](API_REFERENCE.md)** - 레거시 API

---

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────┐
│         프론트엔드 (Frontend)            │
├─────────────────────────────────────────┤
│  • React Web App                        │
│  • React Native (예정)                  │
│  • Chrome Extension (예정)              │
│  • Streamlit (테스트용)                 │
└─────────────────────────────────────────┘
                    ↓ REST API
┌─────────────────────────────────────────┐
│         백엔드 (Backend)                 │
├─────────────────────────────────────────┤
│  • FastAPI Server                       │
│  • WebSocket (실시간)                   │
│  • CORS 지원                            │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         분석 엔진 (Analysis)             │
├─────────────────────────────────────────┤
│  • Multi-timeframe Analyzer            │
│  • Pattern Detector (30+ patterns)     │
│  • AI Chat (Gemini Flash)              │
│  • Portfolio Analyzer                  │
│  • Event Calendar                      │
│  • Stock Screener                      │
└─────────────────────────────────────────┘
```

---

## 🛠️ 기술 스택

### Backend
- **FastAPI** - 고성능 Python 웹 프레임워크
- **yfinance** - 주식 데이터 수집
- **pandas** - 데이터 분석
- **Google Gemini** - AI 채팅

### Frontend
- **React 18** - UI 라이브러리
- **Vite** - 빌드 도구
- **Lightweight Charts** - TradingView 차트
- **Lucide React** - 아이콘

### AI/ML
- **Google Gemini Flash** - 대화형 AI
- **Bulkowski 패턴 통계** - 차트 패턴 신뢰도

---

## 📊 API 엔드포인트

### 종목 분석
- `GET /analyze/{ticker}` - 종합 분석
- `GET /history/{ticker}` - 차트 데이터
- `GET /api/multi-timeframe/{ticker}` - 다중 시간 프레임

### AI 채팅
- `POST /api/chat` - AI와 대화
- `GET /api/chat/suggestions` - 추천 질문

### 경제 캘린더
- `GET /api/calendar` - 이벤트 캘린더

### 포트폴리오
- `POST /api/portfolio/analyze` - 포트폴리오 분석

### 추천 종목
- `GET /api/screener/recommendations` - AI 추천
- `GET /api/screener/top-movers` - 급등/급락

**전체 API 문서**: http://localhost:8000/docs

---

## 🎨 스크린샷

### 웹 앱 (React)
- 실시간 차트 + AI 패턴 시각화
- 수동 그리기 도구 (추세선, 수평선)
- 다중 시간 프레임 전환
- 전체화면 모드

### Streamlit 프로토타입
- 빠른 프로토타이핑
- AI 채팅 인터페이스
- 경제 캘린더
- 포트폴리오 분석

---

## 🤝 기여

기여를 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일 참조

---

## 🙏 감사의 말

- **TradingView** - Lightweight Charts 라이브러리
- **Google** - Gemini AI
- **Thomas Bulkowski** - 차트 패턴 통계
- **yfinance** - 주식 데이터 API

---

## 📞 문의

- **Issues**: GitHub Issues
- **Email**: your-email@example.com

---

**Made with ❤️ by Trading Assistant Team**
