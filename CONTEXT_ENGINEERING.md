# Project Context: AI Trading Assistant

## 1. Vision & Goals
Establish a high-clase, AI-driven stock analysis platform that provides "Advisory Only" insights through a modern web UI. The goal is to replace CLI/Basic GUI with a professional dashboard (React + FastAPI).

## 2. Technical Commandments
- **Architecture**: Modular Backend (API, Collector, Storage, Agents) + Component-based Frontend.
- **Data Flow**: yfinance -> SQLite -> FastAPI -> React -> TradingView Charts.
- **AI Policy**: Utilize Hugging Face for financial sentiment and technical report generation.
- **UI Policy**: Premium Dark Mode, Glassmorphism, Zero-Crash rendering.

## 3. Critical Known Issues (Historical)
- **SQLite Date Type Mismatch**: Strings vs Python Date objects conflict during insertion.
- **Chart Sensitivity**: Lightweight Charts component crashes on duplicate or unsorted time-series data.
- **Ticker Resolving**: Korean stock names often fail to map to proper .KS/.KQ tickers via yfinance Search API.
- **Tailwind v4 Migration**: PostCSS configuration must use `@tailwindcss/postcss`.

## 4. Current Implementation Status
- [x] Modern Dashboard Layout (App.jsx)
- [x] Robust Chart Component (StockChart.jsx)
- [x] FastAPI Server with CORS and Ticker Mapping
- [x] SQLite persistence layer for Price & Financials
- [ ] Multi-timeframe sync (Daily + Hourly) visualization
- [ ] Advanced AI Report styling and formatting

## 5. Development Philosophy
"Never let the UI go blank. If a subsystem fails, degrade gracefully and inform the user in Korean."
