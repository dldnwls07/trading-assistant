import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { StockChart } from '../components/StockChart';
import { Search, Clock, Eye, ChevronRight, Activity } from 'lucide-react';
import { useTranslation } from '../utils/translations';

// 서브 컴포넌트 임포트 (Javascript 컴포넌트들 - 추후 TS 전환 예정)
// @ts-ignore
import StrategyCard from '../components/analysis/StrategyCard';
// @ts-ignore
import TradingSetup from '../components/analysis/TradingSetup';
// @ts-ignore
import AnalysisInsights from '../components/analysis/AnalysisInsights';
// @ts-ignore
import { ThemeList } from '../components/themes/ThemeList';

import { OhlcvData, AnalysisResult } from '../types/api';

const API_BASE = 'http://127.0.0.1:8000';
const API_KEY = "trading-assistant-secret-2024";

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

const AnalysisPage: React.FC<AnalysisPageProps> = ({ settings }) => {
    const { tickerParam } = useParams<{ tickerParam: string }>();
    const [ticker, setTicker] = useState<string>(tickerParam || '');
    const [suggestions, setSuggestions] = useState<any[]>([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
    const [history, setHistory] = useState<OhlcvData[]>([]);
    const [loading, setLoading] = useState(false);
    const [selectedInterval, setSelectedInterval] = useState('1d');
    const [selectedView, setSelectedView] = useState('medium');
    const [chartType, setChartType] = useState('Candle');
    const [isReportOpen, setIsReportOpen] = useState(false);

    // New State for Phase 3
    const [activeTab, setActiveTab] = useState<'market' | 'themes'>('market');

    const isDark = settings?.darkMode;
    const t = useTranslation(settings);

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
        setLoading(true);
        setShowSuggestions(false);
        try {
            const encodedSym = encodeURIComponent(sym);
            const [analReq, histReq] = await Promise.allSettled([
                axios.get(`${API_BASE}/analyze/${encodedSym}?lang=${settings.language}`, AXIOS_CONFIG),
                axios.get(`${API_BASE}/history/${encodedSym}?interval=${selectedInterval}`, AXIOS_CONFIG)
            ]);

            if (analReq.status === 'fulfilled') {
                setAnalysis(analReq.value.data);
                setTicker(analReq.value.data.ticker);
            }
            if (histReq.status === 'fulfilled') {
                setHistory(histReq.value.data.data);
            }
        } catch (err) { console.error(err); } finally { setLoading(false); }
    };

    const handleUpdateHistory = async (interval: string) => {
        console.log(`[AnalysisPage] Requesting history for interval: ${interval}`);
        try {
            const url = `${API_BASE}/history/${encodeURIComponent(ticker)}?interval=${interval}`;
            console.log(`[AnalysisPage] Fetching URL: ${url}`);
            const res = await axios.get(url, AXIOS_CONFIG);
            setHistory(res.data.data);
            console.log(`[AnalysisPage] History data received: ${res.data.data.length} records`);
        } catch (err) { console.error(err); }
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

    // Animation Variants
    const containerVariants = {
        hidden: { opacity: 0 },
        visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
    };

    const itemVariants = {
        hidden: { y: 20, opacity: 0 },
        visible: { y: 0, opacity: 1 }
    };

    return (
        <div className={`min-h-screen p-6 transition-colors duration-300 font-sans ${isDark ? 'bg-[#0b1221] text-slate-200' : 'bg-slate-50 text-slate-800'}`}>

            {/* 1. Top Header & Search Bar */}
            <header className="max-w-[1600px] mx-auto mb-8 flex flex-col md:flex-row gap-6 items-center justify-between">
                <div className="flex items-center gap-4 w-full md:w-auto">
                    {/* Live Badge */}
                    <div className={`px-3 py-1.5 rounded-full text-xs font-bold flex items-center gap-2 animate-pulse ${isDark ? 'bg-blue-500/20 text-blue-400' : 'bg-blue-100 text-blue-600'}`}>
                        <Activity size={14} /> LIVE TERMINAL
                    </div>
                    {/* Time Display */}
                    <div className="text-xs text-slate-500 font-mono hidden md:block">
                        • {new Date().toLocaleTimeString()}
                    </div>
                </div>

                {/* Main Search */}
                <div className="relative w-full md:w-[600px] z-50">
                    <div className={`flex items-center gap-3 px-5 py-3.5 rounded-2xl shadow-xl transition-all duration-300 border ${isDark ? 'bg-[#1e293b] border-slate-700 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20' : 'bg-white border-slate-200 focus-within:border-blue-500'}`}>
                        <Search size={20} className={isDark ? "text-slate-400" : "text-slate-400"} />
                        <input
                            type="text"
                            value={ticker}
                            onChange={(e) => { setTicker(e.target.value.toUpperCase()); setShowSuggestions(true); }}
                            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                            placeholder="Enter symbol (e.g., AAPL, 005930, BTC)"
                            className="bg-transparent border-none outline-none flex-1 font-bold text-lg tracking-wide placeholder-slate-500"
                        />
                        {loading && <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />}
                    </div>

                    {/* Suggestions Dropdown */}
                    <AnimatePresence>
                        {showSuggestions && suggestions.length > 0 && (
                            <motion.ul
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className={`absolute top-full left-0 right-0 mt-2 rounded-xl shadow-2xl border overflow-hidden z-50 ${isDark ? 'bg-[#1e293b] border-slate-700' : 'bg-white border-slate-200'}`}
                            >
                                {suggestions.map((s, i) => (
                                    <li
                                        key={i}
                                        onClick={() => { setTicker(s.symbol); handleSearch(s.symbol); }}
                                        className={`px-5 py-3.5 cursor-pointer flex justify-between items-center transition-colors ${isDark ? 'hover:bg-slate-700 border-b border-slate-700 last:border-0' : 'hover:bg-slate-50 border-b border-slate-100 last:border-0'}`}
                                    >
                                        <div className="flex flex-col">
                                            <span className="font-bold text-sm tracking-wide">{s.symbol}</span>
                                            <span className="text-xs text-slate-500">{s.name}</span>
                                        </div>
                                        <span className={`text-xs px-2 py-1 rounded bg-slate-800 text-slate-400 uppercase`}>{s.typeDisp}</span>
                                    </li>
                                ))}
                            </motion.ul>
                        )}
                    </AnimatePresence>
                </div>

                {/* Tab Switcher (New Logic) */}
                <div className="flex bg-[#1e293b] p-1 rounded-lg border border-slate-700">
                    <button
                        onClick={() => setActiveTab('market')}
                        className={`px-4 py-2 rounded-md text-sm font-bold transition-all ${activeTab === 'market' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                    >
                        Market Analysis
                    </button>
                    <button
                        onClick={() => setActiveTab('themes')}
                        className={`px-4 py-2 rounded-md text-sm font-bold transition-all flex items-center gap-2 ${activeTab === 'themes' ? 'bg-purple-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                    >
                        Thematic Investing <span className="text-[10px] bg-white/20 px-1.5 rounded">BETA</span>
                    </button>
                </div>
            </header>

            {/* Content Area */}
            <main className="max-w-[1600px] mx-auto min-h-[600px]">
                {activeTab === 'themes' ? (
                    // @ts-ignore
                    <ThemeList onThemeSelect={handleThemeSelect} />
                ) : (
                    <motion.div
                        variants={containerVariants}
                        initial="hidden"
                        animate="visible"
                        className="grid grid-cols-12 gap-6"
                    >
                        {/* Left Column: Visual Analysis (Chart + AI Insights) */}
                        <div className="col-span-12 lg:col-span-8 space-y-6">

                            {/* 1. Chart Section */}
                            <motion.div variants={itemVariants} className={`rounded-3xl p-1 border shadow-2xl overflow-hidden relative group ${isDark ? 'bg-[#151e32] border-slate-700/50' : 'bg-white border-slate-200'}`}>
                                <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 opacity-50"></div>

                                {/* Chart Header */}
                                <div className="flex items-center justify-between p-4 pl-6 border-b border-slate-700/30 bg-[#0f172a]/50">
                                    <h2 className="font-black text-xl tracking-tight flex items-center gap-3">
                                        {analysis ? (
                                            <div className="flex flex-col">
                                                <span className="text-white">{analysis.ticker || ticker}</span>
                                                <span className="text-[10px] font-medium text-slate-400 uppercase tracking-widest">{selectedInterval} FRAME Analysis</span>
                                            </div>
                                        ) : (
                                            <span className="text-slate-500">Ready to Analyze</span>
                                        )}
                                    </h2>

                                    {/* Interval Selector */}
                                    <div className="flex bg-[#0f172a] p-1 rounded-lg border border-slate-700/50">
                                        {INTERVALS.map((int) => (
                                            <button
                                                key={int.label}
                                                onClick={() => setSelectedInterval(int.value)}
                                                className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${selectedInterval === int.value
                                                    ? 'bg-blue-600 text-white shadow-lg ring-1 ring-blue-400/50'
                                                    : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                                                    }`}
                                            >
                                                {int.label}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                {/* Chart Body */}
                                <div className="h-[500px] relative">
                                    <StockChart
                                        data={history}
                                        interval={selectedInterval}
                                        options={{ isDark, upColor: '#ef4444', downColor: '#3b82f6' }}
                                        analysis={analysis}
                                    />

                                    {/* Watermark / Empty State Overlay */}
                                    {!history.length && !loading && (
                                        <div className="absolute inset-0 flex items-center justify-center bg-[#0f172a]/80 backdrop-blur-sm z-10">
                                            <div className="text-center space-y-4">
                                                <Search size={48} className="mx-auto text-slate-600 mb-4" />
                                                <h3 className="text-xl font-bold text-slate-400">Search for a ticker to begin</h3>
                                                <p className="text-sm text-slate-500">Enter a symbol above (e.g., AAPL) for AI-powered analysis</p>
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

                        {/* Right Column: Strategic Setup & Signals */}
                        <div className="col-span-12 lg:col-span-4 space-y-6">

                            {/* 1. Trading Setup Card (Primary Signal) */}
                            <motion.div variants={itemVariants}>
                                <TradingSetup analysis={analysis} isDark={isDark} />
                            </motion.div>

                            {/* 2. Strategy Card (Detailed Metrics) */}
                            <motion.div variants={itemVariants}>
                                <StrategyCard analysis={analysis} isDark={isDark} />
                            </motion.div>

                            {/* 3. News / Macro (Placeholder for now) */}
                            {/*  <div className={`rounded-2xl p-6 border ${isDark ? 'bg-[#151e32] border-slate-700' : 'bg-white'}`}>
                                <h3 className="font-bold text-sm text-slate-400 uppercase mb-4">Market Context</h3>
                                <div className="space-y-3">
                                    {[1, 2, 3].map(i => (
                                        <div key={i} className="h-16 bg-slate-800/50 rounded-lg animate-pulse" />
                                    ))}
                                </div>
                            </div> */}

                        </div>
                    </motion.div>
                )}
            </main>
        </div>
    );
};

export default AnalysisPage;
