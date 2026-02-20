import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { StockChart } from '../components/StockChart';
import { Search, Clock, Eye, ChevronRight, Activity, BarChart3 } from 'lucide-react';
import { useTranslation } from '../utils/translations';

// 서브 컴포넌트 임포트 (Javascript 컴포넌트들 - 추후 TS 전환 예정)
// @ts-ignore
import StrategyCard from '../components/analysis/StrategyCard';
// @ts-ignore
import TradingSetup from '../components/analysis/TradingSetup';
import AnalysisInsights from '../components/analysis/AnalysisInsights';
import StrategicSignals from '../components/analysis/StrategicSignals';
import CalendarWidget from '../components/analysis/CalendarWidget';
import { ThemeList } from '../components/themes/ThemeList';

import { OhlcvData, AnalysisResult } from '../types/api';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const API_KEY = import.meta.env.VITE_API_KEY || "trading-assistant-secret-2024";

const AXIOS_CONFIG = {
    headers: { 'X-API-Key': API_KEY }
};

const INTERVALS = [
    { label: '1m', value: '1m' },
    { label: '5m', value: '5m' },
    { label: '15m', value: '15m' },
    { label: '30m', value: '30m' },
    { label: '1h', value: '1h' },
    { label: '1D', value: '1d' },
    { label: '1W', value: '1wk' },
    { label: '1M', value: '1mo' },
    { label: '1Y', value: '1y' },
];

interface AnalysisPageProps {
    settings: any; // Settings type not yet defined
}

// Animation Variants (Outside component to prevent recreation)
const containerVariants: any = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1, delayChildren: 0.1 } }
};

const itemVariants: any = {
    hidden: { y: 40, opacity: 0, scale: 0.98 },
    visible: {
        y: 0,
        opacity: 1,
        scale: 1,
        transition: { type: 'spring', stiffness: 300, damping: 24 }
    }
};

const AnalysisPage: React.FC<AnalysisPageProps> = ({ settings }) => {
    const { tickerParam } = useParams<{ tickerParam: string }>();
    const [ticker, setTicker] = useState<string>(tickerParam || '');
    const [suggestions, setSuggestions] = useState<any[]>([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
    const [history, setHistory] = useState<OhlcvData[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<{ message: string; suggestion: string } | null>(null);
    const [selectedInterval, setSelectedInterval] = useState('1d');
    const [selectedView, setSelectedView] = useState('medium');
    const [chartType, setChartType] = useState('Candle');
    const [isReportOpen, setIsReportOpen] = useState(false);

    // New State for Phase 3
    const [activeTab, setActiveTab] = useState<'market' | 'themes'>('market');

    const isDark = settings?.darkMode;
    const t = useTranslation(settings);

    // Initial Search Effect
    useEffect(() => {
        if (tickerParam) {
            console.log(`[AnalysisPage] Initial search for: ${tickerParam}`);
            handleSearch(tickerParam);
        }
    }, []); // Only on mount

    useEffect(() => {
        const fetchSuggestions = async () => {
            if (ticker.length < 1) { setSuggestions([]); return; }
            try {
                const res = await axios.get(`${API_BASE}/search?query=${encodeURIComponent(ticker)}`, AXIOS_CONFIG);
                setSuggestions(res.data.candidates || []);
            } catch (err) { console.error(err); }
        };
        const tid = setTimeout(fetchSuggestions, 300);
        return () => clearTimeout(tid);
    }, [ticker]);

    // Interval 변경 시 자동으로 데이터 갱신
    useEffect(() => {
        if (ticker && selectedInterval) {
            handleUpdateHistory(selectedInterval);
        }
    }, [selectedInterval]);

    const handleSearch = async (s?: string) => {
        const sym = s || ticker;
        if (!sym) return;

        // 검색 시작 전 이전 상태 초기화 (Context Integrity 보장)
        setLoading(true);
        setShowSuggestions(false);
        setError(null);
        setAnalysis(null);
        setHistory([]);

        try {
            const encodedSym = encodeURIComponent(sym);
            const [analReq, histReq] = await Promise.allSettled([
                axios.get(`${API_BASE}/analyze/${encodedSym}?lang=${settings.language}`, AXIOS_CONFIG),
                axios.get(`${API_BASE}/history/${encodedSym}?interval=${selectedInterval}`, AXIOS_CONFIG)
            ]);

            let hasError = false;
            let errorMessage = '';
            let suggestion = '';

            // 1. 분석 API 결과 처리
            if (analReq.status === 'fulfilled') {
                setAnalysis(analReq.value.data);
                setTicker(analReq.value.data.ticker);
            } else {
                hasError = true;
                errorMessage = `분석 데이터를 가져오지 못했습니다 (${sym})`;
                suggestion = analReq.reason?.response?.data?.detail || "올바르지 않은 티커이거나 지원하지 않는 자산일 수 있습니다. (예: AAPL, 005930.KS)";
            }

            // 2. 차트(History) API 결과 처리
            if (histReq.status === 'fulfilled') {
                setHistory(histReq.value.data.data);
            } else {
                hasError = true;
                if (!errorMessage) {
                    errorMessage = `차트 데이터를 가져오지 못했습니다 (${sym})`;
                    suggestion = histReq.reason?.response?.data?.detail || "해당 심볼의 시장 데이터를 수집할 수 없습니다.";
                }
                // 만약 History만 실패할 경우, 잘못된 분석 데이터와 매칭되는 것을 막기 위해 analysis도 초기화
                setAnalysis(null);
            }

            // 에러가 있다면 UI 상태 업데이트
            if (hasError) {
                setError({ message: errorMessage, suggestion });
            }

        } catch (err: any) {
            console.error(err);
            setError({
                message: "서버 통신 중 치명적인 오류가 발생했습니다.",
                suggestion: "네트워크 연결이나 API 서버 상태를 확인하고 다시 시도하세요."
            });
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateHistory = async (interval: string) => {
        if (!ticker) return;
        console.log(`[AnalysisPage] Requesting history for interval: ${interval}`);
        try {
            const url = `${API_BASE}/history/${encodeURIComponent(ticker)}?interval=${interval}`;
            console.log(`[AnalysisPage] Fetching URL: ${url}`);
            const res = await axios.get(url, AXIOS_CONFIG);
            setHistory(res.data.data);
            setError(null);
            console.log(`[AnalysisPage] History data received: ${res.data.data.length} records`);
        } catch (err: any) {
            console.error(err);
            setError({
                message: `${interval} 간격의 차트 데이터 갱신에 실패했습니다.`,
                suggestion: "네트워크 문제나 서버 응답 지연일 수 있습니다. 잠시 후 재시도하세요."
            });
            // 데이터가 일치하지 않게 되는 것을 방지하기 위해 컨텍스트(History, Analysis) 클리어
            setHistory([]);
            setAnalysis(null);
        }
    };

    const handleThemeSelect = (theme: any) => {
        // theme.relatedStocks[0] or similar logic
        // Assuming theme has relatedStocks array
        if (theme.relatedStocks && theme.relatedStocks.length > 0) {
            const stock = theme.relatedStocks[0];
            setTicker(stock);
            setActiveTab('market');
            handleSearch(stock);
        }
    };

    // Memoized Chart Options to prevent unnecessary re-renders of the chart
    const memoizedChartOptions = React.useMemo(() => ({
        isDark, upColor: '#ef4444', downColor: '#3b82f6'
    }), [isDark]);

    // Memoize the heavy StockChart component
    const renderedChart = React.useMemo(() => {
        if (!history || history.length === 0) return null;
        return (
            <StockChart
                data={history}
                interval={selectedInterval}
                options={memoizedChartOptions}
                analysis={analysis}
            />
        );
    }, [history, selectedInterval, memoizedChartOptions, analysis]);


    return (
        <div className="min-h-screen p-4 md:p-8 font-sans bg-zinc-950 text-zinc-50 relative overflow-x-hidden selection:bg-yellow-400/30">
            {/* Subtle Gradient Background Layers */}
            <div className="fixed inset-0 pointer-events-none overflow-hidden">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-yellow-400/5 blur-[120px] rounded-full"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] bg-zinc-800/10 blur-[100px] rounded-full"></div>
            </div>

            {/* 1. Top Header & Search Bar - Optimized Hierarchy */}
            <header className="max-w-[1600px] mx-auto mb-8 flex flex-col lg:flex-row gap-6 items-center justify-between relative z-[100]">
                <div className="flex items-center gap-6 w-full md:w-auto">
                    {/* Live Badge */}
                    <div className="px-4 py-2 rounded-full text-[10px] font-black flex items-center gap-2 animate-glow bg-secondary/10 text-secondary border border-secondary/30 tracking-[0.2em]">
                        <Activity size={12} className="text-secondary" /> LIVE TERMINAL
                    </div>
                    {/* Time Display */}
                    <div className="text-[10px] text-muted-foreground font-mono hidden lg:block tracking-widest opacity-60">
                        EST. {new Date().toLocaleTimeString('en-US', { hour12: false })} UTC-5
                    </div>
                </div>

                {/* Main Search - Stitch Style Glass */}
                <div className="relative w-full lg:max-w-[600px] z-50">
                    <div className="flex items-center gap-4 px-5 py-4 rounded-xl shadow-2xl transition-colors duration-200 border bg-white/5 backdrop-blur-md border-white/10 group focus-within:border-yellow-400/50 focus-within:ring-1 focus-within:ring-yellow-400/20">
                        <Search size={18} className="text-zinc-500 group-focus-within:text-yellow-400 transition-colors duration-200" aria-hidden="true" />
                        <input
                            type="text"
                            value={ticker}
                            onChange={(e) => { setTicker(e.target.value.toUpperCase()); setShowSuggestions(true); }}
                            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                            placeholder="SEARCH MARKET..."
                            className="bg-transparent border-none outline-none focus:ring-0 px-2 py-0.5 flex-1 font-mono font-bold text-lg tracking-tight placeholder:text-zinc-700 text-zinc-100 min-w-0"
                            autoComplete="off"
                            spellCheck={false}
                            aria-label="Search ticker symbol"
                        />
                        {loading && (
                            <div className="relative flex items-center justify-center w-5 h-5">
                                <div className="absolute inset-0 border-2 border-yellow-400/20 rounded-full"></div>
                                <div className="absolute inset-0 border-2 border-yellow-400 border-t-transparent rounded-full animate-spin"></div>
                            </div>
                        )}
                    </div>

                    {/* Suggestions Dropdown - High Fidelity Glass */}
                    <AnimatePresence>
                        {showSuggestions && suggestions.length > 0 && (
                            <motion.ul
                                initial={{ opacity: 0, y: -10, scale: 0.98 }}
                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                exit={{ opacity: 0, y: -10, scale: 0.98 }}
                                className="absolute top-full left-0 right-0 mt-3 rounded-2xl shadow-3xl border overflow-hidden z-50 glass backdrop-blur-xl border-white/10"
                            >
                                {suggestions.map((s, i) => (
                                    <li
                                        key={i}
                                        role="button"
                                        tabIndex={0}
                                        onClick={() => { setTicker(s.symbol); handleSearch(s.symbol); }}
                                        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setTicker(s.symbol); handleSearch(s.symbol); } }}
                                        aria-label={`Select ${s.symbol}, ${s.name}`}
                                        className="px-6 py-4 cursor-pointer flex justify-between items-center transition-colors duration-200 hover:bg-white/5 border-b border-white/5 focus-visible:outline-none focus-visible:bg-white/10 last:border-0"
                                    >
                                        <div className="flex flex-col">
                                            <span className="font-mono font-bold text-sm tracking-tight text-zinc-100 uppercase">{s.symbol}</span>
                                            <span className="text-[10px] text-zinc-500 font-medium tracking-wider uppercase">{s.name}</span>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <span className="text-[9px] px-2.5 py-1 rounded bg-secondary/10 border border-secondary/20 text-secondary uppercase font-black tracking-[0.15em]">{s.typeDisp}</span>
                                            <ChevronRight size={14} className="text-muted-foreground/30" />
                                        </div>
                                    </li>
                                ))}
                            </motion.ul>
                        )}
                    </AnimatePresence>
                </div>

                {/* Tab Switcher - Stitch Minimalist Pill */}
                <div className="flex bg-white/5 backdrop-blur-md p-1 rounded-xl border border-white/10 shadow-lg">
                    <button
                        onClick={() => setActiveTab('market')}
                        className={`px-5 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition-colors duration-200 ${activeTab === 'market' ? 'bg-yellow-400 text-black shadow-md shadow-yellow-400/20' : 'text-zinc-400 hover:text-zinc-100 hover:bg-white/5'}`}
                    >
                        Markets
                    </button>
                    <button
                        onClick={() => setActiveTab('themes')}
                        className={`px-5 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition-colors duration-200 flex items-center gap-2 ${activeTab === 'themes' ? 'bg-yellow-400 text-black shadow-md shadow-yellow-400/20' : 'text-zinc-400 hover:text-zinc-100 hover:bg-white/5'}`}
                    >
                        Themes <span className="text-[9px] bg-white/10 px-1.5 py-0.5 rounded text-zinc-400 font-mono">NEW</span>
                    </button>
                </div>
            </header>

            {/* Content Area */}
            <main className="max-w-[1700px] mx-auto min-h-[700px]">
                {activeTab === 'themes' ? (
                    // @ts-ignore
                    <ThemeList onThemeSelect={handleThemeSelect} />
                ) : (
                    <motion.div
                        variants={containerVariants}
                        initial="hidden"
                        animate="visible"
                        className="grid grid-cols-1 md:grid-cols-12 gap-6 relative z-10"
                    >
                        {/* Left Column: Visual Analysis (Chart + AI Insights) */}
                        <div className="col-span-1 md:col-span-8 space-y-6">

                            {/* 1. Chart Section - Crisp Stitch Glass */}
                            <motion.div variants={itemVariants} className="rounded-2xl border bg-white/5 backdrop-blur-md border-white/10 shadow-2xl overflow-hidden">

                                <div className="absolute inset-x-0 top-0 h-[2px] bg-gradient-to-r from-transparent via-secondary/40 to-transparent"></div>

                                {/* Chart Header - Minimalist */}
                                <div className="flex items-center justify-between px-6 py-5 border-b border-white/10">
                                    <h2 className="font-bold flex items-center gap-3">
                                        {analysis ? (
                                            <div className="flex items-baseline gap-2">
                                                <span className="text-zinc-100 font-mono text-xl tracking-tight uppercase leading-none">{analysis.ticker || ticker}</span>
                                                <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest font-mono">TERMINAL CORE</span>
                                            </div>
                                        ) : (
                                            <span className="text-zinc-700 font-mono text-xs tracking-widest">OFFLINE</span>
                                        )}
                                    </h2>

                                    {/* Interval Selector - Refined Micro-Pill */}
                                    <div className="flex bg-white/5 p-1 rounded-lg border border-white/5">
                                        {INTERVALS.map((int) => (
                                            <button
                                                key={int.label}
                                                onClick={() => setSelectedInterval(int.value)}
                                                className={`px-3 py-1 rounded-md text-[10px] font-bold tracking-tight transition-colors duration-200 ${selectedInterval === int.value
                                                    ? 'bg-yellow-400 text-black shadow-sm'
                                                    : 'text-zinc-500 hover:text-zinc-100 hover:bg-white/5'
                                                    }`}
                                            >
                                                {int.label}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                {/* Chart Body */}
                                <div className="relative" style={{ height: '480px' }}>
                                    {error ? (
                                        <div className="absolute inset-0 flex flex-col items-center justify-center text-center space-y-4 p-8 bg-red-500/5 m-4">
                                            <div className="bg-red-500/10 p-4 rounded-full flex items-center justify-center">
                                                <Activity size={32} className="text-red-500" />
                                            </div>
                                            <div className="px-4">
                                                <h3 className="text-lg font-black text-red-500 tracking-tight font-mono">{error.message}</h3>
                                                <p className="text-xs font-semibold text-red-500/80 mt-2 max-w-sm mx-auto font-mono tracking-tighter">{error.suggestion}</p>
                                            </div>
                                        </div>
                                    ) : history.length > 0 ? (
                                        renderedChart
                                    ) : (
                                        <div className="absolute inset-0 flex flex-col items-center justify-center text-center space-y-4">
                                            <div className="bg-white/5 p-6 rounded-3xl border border-white/10 animate-pulse">
                                                <Search size={32} className="text-muted-foreground opacity-30" />
                                            </div>
                                            <div>
                                                <h3 className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.4em]">AWAITING_QUANT_SIGNAL</h3>
                                                <p className="text-[9px] text-muted-foreground/30 mt-2 font-mono">ENTER TICKER TO INITIALIZE TERMINAL</p>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </motion.div>

                            {/* 2. Analysis Insights (Bottom Panel) */}
                            <motion.div variants={itemVariants}>
                                <AnalysisInsights
                                    analysis={analysis}
                                    selectedView={selectedView}
                                    setSelectedView={setSelectedView}
                                    setSelectedInterval={setSelectedInterval}
                                    isDark={isDark}
                                    t={t}
                                    onOpenReport={() => setIsReportOpen(true)}
                                    onUpdateHistory={handleUpdateHistory}
                                />
                            </motion.div>

                        </div>

                        {/* Right Column: Strategic Setup & Signals (Optimized Density) */}
                        <div className="col-span-1 md:col-span-4 space-y-6">

                            {/* 1. Trading Setup Card */}
                            <motion.div variants={itemVariants}>
                                <TradingSetup analysis={analysis} isDark={true} />
                            </motion.div>

                            {/* 2. Strategic Signals */}
                            <motion.div variants={itemVariants}>
                                <StrategicSignals analysis={analysis} isDark={true} />
                            </motion.div>

                            {/* 3. Strategy Card */}
                            <motion.div variants={itemVariants}>
                                <StrategyCard analysis={analysis} isDark={true} />
                            </motion.div>

                            {/* 4. Calendar Timeline */}
                            <motion.div variants={itemVariants}>
                                <CalendarWidget analysis={analysis} isDark={true} />
                            </motion.div>

                        </div>
                    </motion.div >
                )}
            </main >
        </div >
    );
};

export default AnalysisPage;
