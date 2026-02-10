# 🚀 React 프론트엔드 업데이트 작업 계획

**작성일**: 2026-02-10
**목표**: FastAPI v2.0 신규 API를 React 프론트엔드에 통합

---

## 📋 현재 상황

### ✅ 완료된 작업
- FastAPI 백엔드에 8개 신규 API 엔드포인트 추가
- Streamlit 프로토타입에 모든 기능 구현
- API 문서 작성 (API_v2_REFERENCE.md)

### ❌ 미완료 작업
- React 프론트엔드에 신규 API 연동
- 멀티 페이지 구조로 변경

---

## 🎯 작업 목표

React 프론트엔드를 **5개 페이지 구조**로 변경:

1. **종목 분석 페이지** (기존) - TradingView 차트
2. **AI 채팅 페이지** (신규) - Gemini Flash
3. **경제 캘린더 페이지** (신규) - FOMC, CPI 등
4. **포트폴리오 분석 페이지** (신규) - AI 평가
5. **AI 추천 종목 페이지** (신규) - 스크리닝

---

## 📝 상세 작업 단계

### 1단계: 프로젝트 설정 (10분)

#### 1.1 패키지 설치
```bash
cd frontend
npm install react-router-dom
```

#### 1.2 폴더 구조 생성
```
frontend/src/
├── App.jsx (수정)
├── pages/
│   ├── AnalysisPage.jsx (기존 App.jsx 이동)
│   ├── ChatPage.jsx (신규)
│   ├── CalendarPage.jsx (신규)
│   ├── PortfolioPage.jsx (신규)
│   └── ScreenerPage.jsx (신규)
└── components/
    ├── StockChart.jsx (기존)
    ├── Navigation.jsx (신규)
    └── ChatMessage.jsx (신규)
```

---

### 2단계: 네비게이션 구현 (20분)

#### 2.1 App.jsx 수정
- React Router 설정
- 네비게이션 바 추가
- 페이지 라우팅

**파일**: `frontend/src/App.jsx`

**주요 코드**:
```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import AnalysisPage from './pages/AnalysisPage';
import ChatPage from './pages/ChatPage';
// ...

function App() {
  return (
    <BrowserRouter>
      <Navigation />
      <Routes>
        <Route path="/" element={<AnalysisPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/calendar" element={<CalendarPage />} />
        <Route path="/portfolio" element={<PortfolioPage />} />
        <Route path="/screener" element={<ScreenerPage />} />
      </Routes>
    </BrowserRouter>
  );
}
```

#### 2.2 Navigation.jsx 생성
- 상단 네비게이션 바
- 페이지 링크
- 테마 선택기

---

### 3단계: 종목 분석 페이지 (30분)

#### 3.1 AnalysisPage.jsx 생성
- 기존 App.jsx 코드 이동
- TradingView 차트 유지
- 모든 기존 기능 유지

**파일**: `frontend/src/pages/AnalysisPage.jsx`

---

### 4단계: AI 채팅 페이지 (40분)

#### 4.1 ChatPage.jsx 생성
**API**: `POST /api/chat`

**주요 기능**:
- 채팅 인터페이스
- 메시지 히스토리
- 추천 질문 버튼
- 종목 컨텍스트 연동

**UI 구성**:
```jsx
<div className="chat-container">
  <div className="messages">
    {messages.map(msg => (
      <ChatMessage key={msg.id} {...msg} />
    ))}
  </div>
  
  <div className="suggestions">
    {suggestions.map(q => (
      <button onClick={() => sendMessage(q)}>{q}</button>
    ))}
  </div>
  
  <div className="input">
    <input value={input} onChange={e => setInput(e.target.value)} />
    <button onClick={sendMessage}>Send</button>
  </div>
</div>
```

**API 호출**:
```javascript
const sendMessage = async (message) => {
  const response = await axios.post('http://localhost:8000/api/chat', {
    message,
    ticker: currentTicker,
    context: analysisData
  });
  setMessages([...messages, response.data]);
};
```

---

### 5단계: 경제 캘린더 페이지 (30분)

#### 5.1 CalendarPage.jsx 생성
**API**: `GET /api/calendar`

**주요 기능**:
- 이벤트 목록
- 날짜별 필터
- 중요도별 색상 구분
- D-Day 표시

**UI 구성**:
```jsx
<div className="calendar">
  <div className="filters">
    <DatePicker start={startDate} end={endDate} />
    <ImportanceFilter />
  </div>
  
  <div className="events">
    {events.map(event => (
      <EventCard key={event.id} {...event} />
    ))}
  </div>
</div>
```

**API 호출**:
```javascript
const fetchCalendar = async () => {
  const response = await axios.get('http://localhost:8000/api/calendar', {
    params: { start_date, end_date }
  });
  setEvents(response.data.events);
};
```

---

### 6단계: 포트폴리오 분석 페이지 (40분)

#### 6.1 PortfolioPage.jsx 생성
**API**: `POST /api/portfolio/analyze`

**주요 기능**:
- 보유 종목 입력
- AI 분석 결과
- 리밸런싱 제안
- 리스크 점수

**UI 구성**:
```jsx
<div className="portfolio">
  <div className="holdings-input">
    <HoldingForm onAdd={addHolding} />
    <HoldingsList holdings={holdings} onRemove={removeHolding} />
  </div>
  
  <button onClick={analyzePortfolio}>Analyze</button>
  
  {analysis && (
    <div className="analysis-results">
      <MetricCard label="Total Value" value={analysis.total_value} />
      <MetricCard label="Return" value={analysis.total_return} />
      <MetricCard label="Risk Score" value={analysis.risk_score} />
      <RecommendationsList items={analysis.recommendations} />
    </div>
  )}
</div>
```

---

### 7단계: AI 추천 종목 페이지 (30분)

#### 7.1 ScreenerPage.jsx 생성
**API**: `GET /api/screener/recommendations`

**주요 기능**:
- 투자 스타일 선택
- AI 추천 종목 목록
- 급등/급락 종목

**UI 구성**:
```jsx
<div className="screener">
  <div className="style-selector">
    <button onClick={() => setStyle('aggressive')}>Aggressive</button>
    <button onClick={() => setStyle('balanced')}>Balanced</button>
    <button onClick={() => setStyle('conservative')}>Conservative</button>
  </div>
  
  <div className="recommendations">
    {recommendations.map(stock => (
      <StockCard key={stock.ticker} {...stock} />
    ))}
  </div>
  
  <div className="top-movers">
    <h3>Top Gainers</h3>
    <MoversList items={gainers} />
    
    <h3>Top Losers</h3>
    <MoversList items={losers} />
  </div>
</div>
```

---

## 🎨 디자인 가이드

### 색상 테마
- **Primary**: Cyan (#22d3ee)
- **Background**: Dark (#020617)
- **Card**: Glass effect (backdrop-blur)
- **Text**: Slate-200

### 컴포넌트 스타일
- **Border Radius**: 2rem ~ 3.5rem (둥근 모서리)
- **Shadows**: 큰 그림자 (shadow-2xl)
- **Animations**: Framer Motion 사용
- **Hover Effects**: scale, color transitions

---

## 🔧 기술 스택

- **React 18**
- **React Router v6**
- **Axios** (API 호출)
- **Framer Motion** (애니메이션)
- **Lucide React** (아이콘)
- **TailwindCSS** (스타일링)

---

## ⏱️ 예상 소요 시간

| 단계 | 작업 | 시간 |
|------|------|------|
| 1 | 프로젝트 설정 | 10분 |
| 2 | 네비게이션 | 20분 |
| 3 | 종목 분석 페이지 | 30분 |
| 4 | AI 채팅 페이지 | 40분 |
| 5 | 경제 캘린더 페이지 | 30분 |
| 6 | 포트폴리오 페이지 | 40분 |
| 7 | AI 추천 종목 페이지 | 30분 |
| **총계** | | **3시간** |

---

## 📦 필요한 파일 목록

### 신규 생성
- [ ] `frontend/src/pages/AnalysisPage.jsx`
- [ ] `frontend/src/pages/ChatPage.jsx`
- [ ] `frontend/src/pages/CalendarPage.jsx`
- [ ] `frontend/src/pages/PortfolioPage.jsx`
- [ ] `frontend/src/pages/ScreenerPage.jsx`
- [ ] `frontend/src/components/Navigation.jsx`
- [ ] `frontend/src/components/ChatMessage.jsx`

### 수정
- [ ] `frontend/src/App.jsx` (라우팅 추가)
- [ ] `frontend/package.json` (react-router-dom 추가)

---

## 🧪 테스트 체크리스트

### 기능 테스트
- [ ] 페이지 간 네비게이션 작동
- [ ] AI 채팅 메시지 전송/수신
- [ ] 경제 캘린더 이벤트 로드
- [ ] 포트폴리오 분석 결과 표시
- [ ] AI 추천 종목 목록 표시

### UI/UX 테스트
- [ ] 모바일 반응형 확인
- [ ] 애니메이션 부드러움
- [ ] 로딩 상태 표시
- [ ] 에러 처리

---

## 🚀 배포 준비

### 프론트엔드
- **Vercel** 또는 **Netlify**
- 환경 변수: `VITE_API_BASE_URL`

### 백엔드
- **Railway** 또는 **Render**
- 환경 변수: `GEMINI_API_KEY`, `FRED_API_KEY`

---

## 📌 참고 자료

- **API 문서**: `API_v2_REFERENCE.md`
- **Streamlit 구현**: `src/ui/pages/` (참고용)
- **기존 차트**: `frontend/src/components/StockChart.jsx`

---

## 💡 다음 작업 시 시작 명령

```bash
# 1. 패키지 설치
cd frontend
npm install react-router-dom

# 2. 개발 서버 실행
npm run dev

# 3. 백엔드 서버 실행 (새 터미널)
cd ..
uvicorn src.api.server:app --reload
```

---

**작업 준비 완료!** 다음 세션에서 이 계획서를 따라 진행하시면 됩니다! 🎉
