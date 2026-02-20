// Basic types for the application

export interface StockTicker {
    symbol: string;
    name: string;
    price: number;
    change: number;
    changePercent: number;
}

export interface RecommendedEtf {
    ticker: string;
    name: string;
    description: string;
}

export interface InvestmentTheme {
    id: string;
    name: string;
    description: string;
    icon: string; // Lucide icon name or emoji
    tickers: string[]; // List of symbols
    avgPerformance: number; // Average daily change of constituents
    momentumScore: number; // 0-100 score
    tags: string[];
    recommendedEtfs?: RecommendedEtf[]; // ETF 추천 (각 테마 관련 대표 ETF)
}
