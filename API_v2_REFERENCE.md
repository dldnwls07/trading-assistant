# 🚀 Trading Assistant API v2.0

## 📋 목차
- [개요](#개요)
- [시작하기](#시작하기)
- [API 엔드포인트](#api-엔드포인트)
- [사용 예시](#사용-예시)

---

## 개요

**Trading Assistant API v2.0**은 AI 기반 주식 분석 서버입니다.

### 주요 기능
- ✅ **종목 분석** (다중 시간 프레임, 30+ 차트 패턴)
- ✅ **AI 채팅** (Gemini Flash)
- ✅ **경제 캘린더** (FOMC, CPI, 실적 발표)
- ✅ **포트폴리오 분석**
- ✅ **AI 추천 종목**
- ✅ **실시간 차트 데이터**

### 기술 스택
- **Backend**: FastAPI (Python)
- **Frontend**: React + Vite
- **AI**: Google Gemini Flash
- **Data**: yfinance, FRED API

---

## 시작하기

### 1. 서버 실행

#### 방법 1: 배치 파일 (추천)
```bash
start_web.bat
```

#### 방법 2: 수동 실행
```bash
# 백엔드
uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000

# 프론트엔드 (새 터미널)
cd frontend
npm run dev
```

### 2. 접속
- **API 서버**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **웹 앱**: http://localhost:5173

---

## API 엔드포인트

### 🏥 헬스 체크

#### `GET /api/health`
서버 상태 확인

**응답:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "features": {
    "ai_chat": true,
    "calendar": true,
    "portfolio": true,
    "screener": true,
    "multi_timeframe": true
  },
  "timestamp": "2026-02-10T19:00:00"
}
```

---

### 📊 종목 분석

#### `GET /analyze/{ticker}`
종목 종합 분석

**파라미터:**
- `ticker` (string): 종목 심볼 (예: AAPL, 005930.KS, 삼성전자)

**응답:**
```json
{
  "ticker": "AAPL",
  "final_score": 78,
  "signal": "매수 권고",
  "technical": {...},
  "fundamental": {...},
  "patterns": [...],
  "entry_points": {
    "buy": 175.50,
    "target": 195.00,
    "stop": 168.00
  }
}
```

#### `GET /history/{ticker}`
차트 데이터 (OHLCV + 지표)

**파라미터:**
- `ticker` (string): 종목 심볼
- `interval` (string): 시간 프레임 (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1wk, 1mo)

**응답:**
```json
{
  "ticker": "AAPL",
  "interval": "1d",
  "data": [
    {
      "time": "2026-02-10",
      "open": 175.00,
      "high": 178.50,
      "low": 174.00,
      "close": 177.25,
      "volume": 50000000,
      "sma20": 175.50,
      "sma50": 172.00,
      "rsi": 65.5,
      "macd": 1.25
    }
  ]
}
```

#### `GET /api/multi-timeframe/{ticker}`
다중 시간 프레임 분석

**응답:**
```json
{
  "ticker": "AAPL",
  "timeframes": {
    "1h": {"trend": "상승", "rsi": 68.5},
    "4h": {"trend": "상승", "rsi": 65.2},
    "1d": {"trend": "상승", "rsi": 62.1},
    "1wk": {"trend": "상승", "rsi": 58.7}
  }
}
```

---

### 💬 AI 채팅

#### `POST /api/chat`
AI와 대화

**요청:**
```json
{
  "message": "AAPL 지금 사도 될까요?",
  "ticker": "AAPL",
  "context": {
    "analysis": {
      "final_score": 78,
      "signal": "매수 권고"
    }
  }
}
```

**응답:**
```json
{
  "message": "AAPL 지금 사도 될까요?",
  "response": "AAPL의 현재 AI 분석 점수는 78점으로 매우 긍정적입니다...",
  "timestamp": "2026-02-10T19:00:00"
}
```

#### `GET /api/chat/suggestions`
추천 질문

**파라미터:**
- `ticker` (string, optional): 종목 심볼

**응답:**
```json
{
  "suggestions": [
    "AAPL 지금 사도 될까요?",
    "목표가는 얼마인가요?",
    "리스크는 무엇인가요?"
  ]
}
```

---

### 📅 경제 캘린더

#### `GET /api/calendar`
경제 이벤트 캘린더

**파라미터:**
- `start_date` (string, optional): 시작일 (YYYY-MM-DD)
- `end_date` (string, optional): 종료일 (YYYY-MM-DD)
- `tickers` (string, optional): 종목 리스트 (쉼표 구분)

**응답:**
```json
{
  "total_events": 45,
  "events": [
    {
      "date": "2026-02-15",
      "type": "FOMC",
      "title": "FOMC 회의",
      "importance": "critical",
      "impact": "금리 결정"
    }
  ],
  "summary": {
    "this_week": [...],
    "upcoming_critical": [...]
  }
}
```

---

### 💼 포트폴리오 분석

#### `POST /api/portfolio/analyze`
포트폴리오 AI 평가

**요청:**
```json
{
  "holdings": [
    {"ticker": "AAPL", "shares": 10, "avg_price": 150.00},
    {"ticker": "MSFT", "shares": 5, "avg_price": 300.00}
  ]
}
```

**응답:**
```json
{
  "total_value": 5250.00,
  "total_return": 12.5,
  "risk_score": 45,
  "diversification_score": 65,
  "recommendations": [
    "기술주 비중이 높습니다. 다른 섹터 추가를 고려하세요."
  ]
}
```

---

### 🔍 AI 추천 종목

#### `GET /api/screener/recommendations`
투자 스타일별 추천 종목

**파라미터:**
- `style` (string): 투자 스타일 (aggressive, growth, balanced, conservative)
- `market` (string): 시장 (US, KR)
- `limit` (int): 최대 종목 수

**응답:**
```json
{
  "style": "balanced",
  "recommendations": [
    {
      "ticker": "AAPL",
      "score": 85,
      "reason": "강한 펀더멘털과 기술적 모멘텀"
    }
  ]
}
```

#### `GET /api/screener/top-movers`
급등/급락 종목

**응답:**
```json
{
  "gainers": [
    {"ticker": "NVDA", "change": 8.5}
  ],
  "losers": [
    {"ticker": "TSLA", "change": -5.2}
  ]
}
```

---

### 🔎 종목 검색

#### `GET /search`
종목 자동완성

**파라미터:**
- `query` (string): 검색어

**응답:**
```json
{
  "query": "삼성",
  "candidates": [
    {
      "symbol": "005930.KS",
      "name": "삼성전자",
      "exchange": "KRX",
      "is_korean": true
    }
  ]
}
```

---

## 사용 예시

### JavaScript (Fetch)

```javascript
// 종목 분석
const response = await fetch('http://localhost:8000/analyze/AAPL');
const data = await response.json();
console.log(data.final_score); // 78

// AI 채팅
const chatResponse = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'AAPL 지금 사도 될까요?',
    ticker: 'AAPL'
  })
});
const chatData = await chatResponse.json();
console.log(chatData.response);

// 경제 캘린더
const calendarResponse = await fetch('http://localhost:8000/api/calendar');
const calendarData = await calendarResponse.json();
console.log(calendarData.events);
```

### Python (requests)

```python
import requests

# 종목 분석
response = requests.get('http://localhost:8000/analyze/AAPL')
data = response.json()
print(data['final_score'])  # 78

# AI 채팅
chat_response = requests.post('http://localhost:8000/api/chat', json={
    'message': 'AAPL 지금 사도 될까요?',
    'ticker': 'AAPL'
})
print(chat_response.json()['response'])

# 포트폴리오 분석
portfolio_response = requests.post('http://localhost:8000/api/portfolio/analyze', json={
    'holdings': [
        {'ticker': 'AAPL', 'shares': 10, 'avg_price': 150.00}
    ]
})
print(portfolio_response.json())
```

---

## 📱 플랫폼별 활용

### 웹 (React)
- 이미 구현된 React 프론트엔드 사용
- `frontend/` 폴더 참조

### 모바일 앱 (React Native)
```javascript
// React Native에서 동일한 API 사용
import axios from 'axios';

const API_BASE = 'http://your-server-ip:8000';

const analyzeStock = async (ticker) => {
  const response = await axios.get(`${API_BASE}/analyze/${ticker}`);
  return response.data;
};
```

### Chrome 확장프로그램
```javascript
// background.js 또는 content script
chrome.runtime.sendMessage({
  action: 'analyzeStock',
  ticker: 'AAPL'
}, (response) => {
  console.log(response.final_score);
});
```

---

## 🔒 보안

- **CORS**: 모든 출처 허용 (개발 환경)
- **프로덕션**: CORS 설정을 특정 도메인으로 제한 필요
- **API 키**: `.env` 파일로 관리 (Git에 커밋 금지)

---

## 📞 지원

- **API 문서**: http://localhost:8000/docs (Swagger UI)
- **GitHub**: 프로젝트 저장소
- **이슈**: GitHub Issues

---

**Made with ❤️ by Trading Assistant Team**
