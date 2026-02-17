export interface OhlcvData {
    time: string | number; // String from backend, converted to number in frontend
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
    // Technical Indicators (Optional)
    sma_5?: number;
    sma_20?: number;
    sma_60?: number;
    sma_120?: number;
    bb_upper?: number;
    bb_lower?: number;
    bb_middle?: number;
    rsi?: number;
    // ... add more as needed based on server.py
}

export interface HistoryResponse {
    ticker: string;
    interval: string;
    data: OhlcvData[];
}

export interface TechnicalAnalysis {
    signal: string; // e.g., "buy", "sell", "hold"
    score: number;
    // ... detail fields from analyst.py
}

export interface FundamentalAnalysis {
    overall_status: string;
    // ... detail fields
}

export interface EntryPoints {
    entry_price: number;
    stop_loss: number;
    take_profit: number;
}

export interface KeyLevels {
    levels: number[];
    current_price: number;
}

export interface Trendline {
    type: 'uptrend' | 'downtrend';
    start_time: string;
    start_price: number;
    end_time: string;
    end_price: number;
}

export interface Pattern {
    name: string;
    timeframe: string;
    desc: string;
}

export interface MLForecast {
    success: boolean;
    direction: string;
    predicted_return: number;
    message: string;
}

export interface BacktestResult {
    success: boolean;
    win_rate: number;
    profit_factor: number;
    mdd_pct: number;
}

export interface FullAnalysis {
    ml_forecast?: MLForecast;
    backtest?: BacktestResult;
    [key: string]: any;
}

export interface TimeframeStrategy {
    recommendation: string;
    focus_areas: string;
    holding_period: string;
    full_analysis?: FullAnalysis;
}

export interface GlobalEnsemble {
    grade: string;
    confidence: number;
    risk_impact: number;
    recommendation: string;
    confluence_details: string[];
}

export interface Consensus {
    global_ensemble?: GlobalEnsemble;
}

export interface MarketRegime {
    regime: string;
    label: string;
    color: string;
    desc: string;
}

export interface StrategyChecklistItem {
    id: string;
    text: string;
    status: boolean;
    importance: string;
}

export interface AnalysisResult {
    ticker: string;
    interval: string;
    signal: string;
    final_score: number;
    technical: TechnicalAnalysis;
    fundamental: FundamentalAnalysis;
    entry_points: EntryPoints;
    key_levels?: KeyLevels;
    trendlines?: Trendline[];
    events?: Record<string, any>;
    full_report?: string;

    // AnalysisInsights additions
    all_patterns?: Pattern[];
    short_term?: TimeframeStrategy;
    medium_term?: TimeframeStrategy;
    long_term?: TimeframeStrategy;

    // StrategyCard additions
    market_regime?: MarketRegime;
    strategy_checklist?: StrategyChecklistItem[];

    // TradingSetup additions
    consensus?: Consensus;

    // Allow dynamic access for timeframe strategies
    [key: string]: any;
}
