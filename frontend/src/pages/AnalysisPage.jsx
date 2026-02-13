import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { StockChart } from '../components/StockChart';
import {
    Search,
    Zap,
    Activity,
    Star,
    Clock,
    BarChart3,
    Eye,
    ChevronRight,
    MessageSquare
} from 'lucide-react';
import HelpTooltip from '../components/HelpTooltip';
import { useTranslation } from '../utils/translations';

const API_BASE = 'http://127.0.0.1:8000';

const INTERVALS = [
    { label: '1m', value: '1m' },
    { label: '5m', value: '5m' },
    { label: '15m', value: '15m' },
    { label: '1h', value: '60m' },
    { label: '1D', value: '1d' },
    { label: '1W', value: '1wk' },
];

const AnalysisPage = ({ settings }) => {
    const { tickerParam } = useParams();
    const [ticker, setTicker] = useState(tickerParam || '');
    const [suggestions, setSuggestions] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [analysis, setAnalysis] = useState(null);
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [selectedInterval, setSelectedInterval] = useState('1d');
    const [selectedView, setSelectedView] = useState('short'); // short, medium, long
    const [chartType, setChartType] = useState('Candle');
    const [isReportOpen, setIsReportOpen] = useState(false);

    const isDark = settings?.darkMode;
    const t = useTranslation(settings);

    // 검색어 추천 로직
    useEffect(() => {
        const fetchSuggestions = async () => {
            if (ticker.length < 1) {
                setSuggestions([]);
                return;
            }
            try {
                const res = await axios.get(`${API_BASE}/search?query=${encodeURIComponent(ticker)}`);
                setSuggestions(res.data.candidates || []);
            } catch (err) { console.error(err); }
        };
        const tid = setTimeout(fetchSuggestions, 300);
        return () => clearTimeout(tid);
    }, [ticker]);

    const handleSearch = async (s) => {
        const sym = s || ticker;
        if (!sym) return;
        setLoading(true);
        setShowSuggestions(false);

        try {
            const encodedSym = encodeURIComponent(sym);
            const [analReq, histReq] = await Promise.allSettled([
                axios.get(`${API_BASE}/analyze/${encodedSym}?lang=${settings.language}`),
                axios.get(`${API_BASE}/history/${encodedSym}?interval=${selectedInterval}`)
            ]);

            if (analReq.status === 'fulfilled') {
                setAnalysis(analReq.value.data);
                setTicker(analReq.value.data.ticker);
            }
            if (histReq.status === 'fulfilled') setHistory(histReq.value.data.data);
        } catch (err) { console.error(err); } finally { setLoading(false); }
    };

    // 초기 검색 및 파라미터 변경 시 대응
    useEffect(() => {
        if (tickerParam) {
            handleSearch(tickerParam);
        }
        // 자동 검색 제거: 사용자가 직접 검색하도록 변경
    }, [tickerParam]);

    return (
        <div className={`min-h-screen pb-12 transition-colors duration-300 ${isDark ? 'bg-slate-950 text-slate-100' : 'bg-gray-50 text-gray-900'}`}>

            {/* Full Report Modal */}
            <AnimatePresence>
                {isReportOpen && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 20 }}
                            className={`w-full max-w-4xl max-h-[90vh] overflow-hidden rounded-3xl shadow-2xl flex flex-col ${isDark ? 'bg-slate-900 text-slate-100 border border-slate-800' : 'bg-white text-gray-900'}`}
                        >
                            <div className={`p-6 border-b flex items-center justify-between ${isDark ? 'border-slate-800' : 'border-gray-100'}`}>
                                <div className="flex items-center gap-3">
                                    <div className="bg-blue-600 p-2 rounded-xl text-white">
                                        <Eye className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <h2 className="text-xl font-black">AI Detail Analysis Report</h2>
                                        <p className="text-xs opacity-50">{analysis?.display_name} ({analysis?.ticker})</p>
                                    </div>
                                </div>
                                <button onClick={() => setIsReportOpen(false)} className={`p-2 rounded-full hover:bg-opacity-10 transition-colors ${isDark ? 'hover:bg-white' : 'hover:bg-black'}`}>
                                    <span className="text-2xl leading-none">&times;</span>
                                </button>
                            </div>
                            <div className="p-8 overflow-y-auto custom-scrollbar">
                                <div className={`prose prose-sm max-w-none ${isDark ? 'prose-invert' : ''}`}>
                                    <div className="whitespace-pre-wrap leading-relaxed font-medium opacity-90 text-base">
                                        {analysis?.full_report || "리포트를 불러오는 중..."}
                                    </div>
                                </div>
                            </div>
                            <div className={`p-4 border-t text-center text-[11px] opacity-40 ${isDark ? 'border-slate-800' : 'border-gray-100'}`}>
                                This analysis is generated by QuantCore AI Engine and should be used for reference only.
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {/* Header / Search Area */}
            <div className={`border-b py-8 mb-8 shadow-sm transition-colors duration-300 ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-6">
                    <div className="flex items-center gap-5">
                        <div className="h-14 w-14 rounded-2xl bg-blue-600 flex items-center justify-center text-white font-black text-2xl shadow-xl shadow-blue-500/30">
                            {analysis?.ticker?.substring(0, 2) || "AN"}
                        </div>
                        <div>
                            <div className="flex items-center gap-2 mb-0.5">
                                <h1 className="text-3xl font-black tracking-tight">{analysis?.display_name || "Stock Assistant"}</h1>
                                {analysis?.ticker && <span className="text-xs font-black bg-blue-500/10 text-blue-500 px-2 py-0.5 rounded-full">{analysis?.ticker}</span>}
                            </div>
                            <div className="flex items-center gap-2 text-sm opacity-50 font-medium">
                                <Clock className="w-3.5 h-3.5" />
                                <span>KRW • {new Date().toLocaleTimeString()} • Live Analysis</span>
                            </div>
                        </div>
                    </div>

                    <div className="relative w-full md:w-[450px]">
                        <div className={`flex items-center px-4 py-3.5 rounded-2xl border transition-all duration-300 group ${isDark ? 'bg-slate-800 border-slate-700 focus-within:border-blue-500/50 focus-within:ring-4 focus-within:ring-blue-500/10' : 'bg-gray-50 border-gray-200 focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10'}`}>
                            <Search className={`h-5 w-5 mr-3 transition-colors ${isDark ? 'text-slate-500 group-focus-within:text-blue-400' : 'text-gray-400 group-focus-within:text-blue-500'}`} />
                            <input
                                type="text"
                                value={ticker}
                                onChange={(e) => { setTicker(e.target.value.toUpperCase()); setShowSuggestions(true); }}
                                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                                placeholder={t.ana_search_placeholder}
                                className="w-full bg-transparent border-none outline-none font-bold placeholder:text-gray-400"
                            />
                            {loading && <div className="ml-2 h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>}
                        </div>

                        {/* Search Suggestions */}
                        <AnimatePresence>
                            {showSuggestions && suggestions.length > 0 && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: 10 }}
                                    className={`absolute left-0 right-0 mt-2 rounded-2xl shadow-2xl z-50 border overflow-hidden ${isDark ? 'bg-slate-800 border-slate-700 text-slate-200' : 'bg-white border-gray-100'}`}
                                >
                                    {suggestions.map((s, i) => (
                                        <button
                                            key={i}
                                            onClick={() => { setTicker(s.symbol); handleSearch(s.symbol); }}
                                            className={`w-full px-5 py-3.5 text-left flex items-center justify-between hover:bg-blue-500 hover:text-white transition-colors border-b last:border-0 ${isDark ? 'border-slate-700' : 'border-gray-50'}`}
                                        >
                                            <div className="flex items-center gap-3">
                                                <span className="font-black text-sm">{s.symbol}</span>
                                                <span className="text-xs opacity-70 font-medium">{s.name}</span>
                                            </div>
                                            <ChevronRight className="w-4 h-4 opacity-30" />
                                        </button>
                                    ))}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            </div>

            <main className="max-w-7xl mx-auto px-4 space-y-8">
                {/* 1. Dashboard Row */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className={`p-8 rounded-3xl border shadow-xl flex flex-col items-center justify-center relative overflow-hidden transition-all duration-300 ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                        <div className="absolute top-0 left-0 w-full h-1 bg-blue-500"></div>
                        <span className="text-[10px] font-black text-blue-500 uppercase tracking-widest mb-2 px-3 py-1 bg-blue-500/5 rounded-full flex items-center gap-1">
                            {t.ana_ai_score}
                            <HelpTooltip indicatorId="Sharpe Ratio" title="AI 신뢰도 점수" isDark={isDark} />
                        </span>
                        <div className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-br from-blue-400 to-blue-600 drop-shadow-sm">{analysis?.final_score || '--'}</div>
                    </div>
                    <div className={`p-8 rounded-3xl border shadow-xl flex flex-col items-center justify-center transition-all duration-300 ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                        <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-1">
                            Engine Signal
                            <HelpTooltip indicatorId="RSI" title="매매 강도 지표" isDark={isDark} />
                        </span>
                        <div className={`text-xl font-black px-6 py-2 rounded-2xl border-2 italic shadow-sm ${analysis?.signal?.includes('매수') ? 'bg-green-500/10 text-green-500 border-green-500/20' : analysis?.signal?.includes('매도') ? 'bg-red-500/10 text-red-500 border-red-500/20' : 'bg-blue-500/5 text-blue-500 border-blue-500/10'}`}>
                            {analysis?.signal || 'Thinking...'}
                        </div>
                    </div>
                    <div className={`md:col-span-2 p-8 rounded-3xl border shadow-xl transition-all duration-300 ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                        <div className="flex justify-between items-center mb-6">
                            <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Target Trading Zones</span>
                            <div className="flex items-center gap-1.5 opacity-30">
                                <Star className="w-3.5 h-3.5 fill-current" />
                                <span className="text-[10px] font-black uppercase">Alpha Strategy</span>
                                <HelpTooltip indicatorId="Pivot Points" title="피벗 포인트 전략" isDark={isDark} />
                            </div>
                        </div>
                        <div className="flex justify-around items-center mb-8">
                            <div className="text-center group">
                                <p className="text-[10px] text-rose-500 font-black uppercase mb-1 tracking-tighter group-hover:scale-110 transition-transform flex items-center justify-center gap-1">
                                    {t.ana_stop_loss}
                                    <HelpTooltip indicatorId="Support & Resistance" title="손절 기준" isDark={isDark} />
                                </p>
                                <p className="text-xl font-black opacity-90">
                                    {analysis?.[`${selectedView}_term`]?.entry_points?.stop_loss?.toLocaleString() || '--'}
                                </p>
                            </div>
                            <div className={`h-12 w-px ${isDark ? 'bg-slate-800' : 'bg-gray-100'}`} />
                            <div className="text-center group">
                                <p className="text-[10px] text-blue-500 font-black uppercase mb-1 tracking-tighter group-hover:scale-110 transition-transform flex items-center justify-center gap-1">
                                    {t.ana_entry_zone}
                                    <HelpTooltip indicatorId="Bollinger Bands" title="추천 진입 구간" isDark={isDark} />
                                </p>
                                <p className="text-3xl font-black text-blue-600 shadow-blue-500/10 drop-shadow-sm">
                                    {analysis?.[`${selectedView}_term`]?.entry_points?.buy_zone?.[0]?.price?.toLocaleString() || '--'}
                                </p>
                            </div>
                            <div className={`h-12 w-px ${isDark ? 'bg-slate-800' : 'bg-gray-100'}`} />
                            <div className="text-center group">
                                <p className="text-[10px] text-emerald-500 font-black uppercase mb-1 tracking-tighter group-hover:scale-110 transition-transform flex items-center justify-center gap-1">
                                    {t.ana_take_profit}
                                    <HelpTooltip indicatorId="Support & Resistance" title="목표 수익 구간" isDark={isDark} />
                                </p>
                                <p className="text-xl font-black opacity-90">
                                    {analysis?.[`${selectedView}_term`]?.entry_points?.take_profit?.toLocaleString() || '--'}
                                </p>
                            </div>
                        </div>

                        {/* Price Scenarios */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 pt-6 border-t border-dashed border-gray-200 dark:border-slate-800">
                            <div className={`p-4 rounded-2xl ${isDark ? 'bg-red-500/5 border border-red-500/10' : 'bg-red-50 border border-red-100'}`}>
                                <p className="text-[10px] font-black text-red-500 uppercase flex items-center gap-2 mb-2">
                                    Bearish Scenario (Support Break)
                                    <HelpTooltip indicatorId="Support & Resistance" title="하락 시나리오" isDark={isDark} />
                                </p>
                                <p className="text-xs font-medium opacity-80 leading-relaxed">
                                    {analysis?.price_scenarios?.bearish || "Calculated based on volatility..."}
                                </p>
                            </div>
                            <div className={`p-4 rounded-2xl ${isDark ? 'bg-green-500/5 border border-green-500/10' : 'bg-green-50 border border-green-100'}`}>
                                <p className="text-[10px] font-black text-green-500 uppercase flex items-center gap-2 mb-2">
                                    Bullish Scenario (Resist Break)
                                    <HelpTooltip indicatorId="Support & Resistance" title="상승 시나리오" isDark={isDark} />
                                </p>
                                <p className="text-xs font-medium opacity-80 leading-relaxed">
                                    {analysis?.price_scenarios?.bullish || "Calculated based on momentum..."}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 2. Chart Section */}
                <div className={`rounded-3xl border shadow-2xl overflow-hidden transition-all duration-300 ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                    {/* Control Bar */}
                    <div className={`p-4 flex items-center justify-between gap-4 flex-wrap border-b ${isDark ? 'bg-slate-900/50 border-slate-800' : 'bg-gray-50/50 border-gray-100'}`}>
                        <div className={`flex bg-black/5 p-1 rounded-2xl ${isDark ? 'bg-white/5' : ''}`}>
                            {INTERVALS.map((int) => (
                                <button
                                    key={int.value}
                                    onClick={() => { setSelectedInterval(int.value); handleSearch(); }}
                                    className={`px-4 py-1.5 rounded-xl text-[11px] font-black transition-all ${selectedInterval === int.value ? (isDark ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'bg-slate-800 text-white shadow-lg') : 'text-gray-500 hover:text-gray-900'}`}
                                >
                                    {int.label}
                                </button>
                            ))}
                        </div>

                        {/* Chart Render Type Toggle */}
                        <div className="hidden lg:flex items-center gap-2">
                            <div className={`h-8 w-px mx-4 ${isDark ? 'bg-slate-800' : 'bg-gray-200'}`} />
                            <span className="text-[10px] font-black text-gray-400 uppercase mr-2">Chart Render</span>
                            <div className="flex gap-1">
                                {['Line', 'Candle', 'Area'].map(t => (
                                    <button
                                        key={t}
                                        onClick={() => setChartType(t)}
                                        className={`px-3 py-1 rounded-full text-[10px] font-black border transition-all ${chartType === t ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-200 opacity-50 hover:opacity-100'}`}
                                    >
                                        {t}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className={`h-[550px] w-full relative ${isDark ? 'bg-[#131722]' : 'bg-gray-50'}`}>
                        {loading && (
                            <div className="absolute inset-0 z-10 bg-black/20 backdrop-blur-[2px] flex items-center justify-center">
                                <Activity className="w-12 h-12 text-blue-500 animate-spin" />
                            </div>
                        )}
                        {history.length > 0 ? (
                            <StockChart data={history} interval={selectedInterval} chartType={chartType} options={settings} analysis={analysis} />
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-gray-500 gap-4">
                                <Activity className="w-12 h-12 animate-pulse text-blue-500" />
                                <p className="font-black text-sm uppercase tracking-widest opacity-40 italic">Decoding Market Frequency...</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* 3. Multi-View Analysis Report */}
                <div className={`rounded-3xl border shadow-2xl p-8 mb-12 transition-all duration-300 ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                    <div className="flex flex-col md:flex-row items-center justify-between mb-8 gap-4 text-center md:text-left">
                        <h3 className="text-2xl font-black flex items-center gap-3">
                            <BarChart3 className="w-7 h-7 text-blue-500" />
                            AI Insight Engine 4.0
                        </h3>
                        <div className={`flex p-1.5 rounded-2xl ${isDark ? 'bg-slate-800' : 'bg-gray-100'}`}>
                            {[
                                { id: 'short', label: t.ana_short_term, interval: '60m' },
                                { id: 'medium', label: t.ana_medium_term, interval: '1d' },
                                { id: 'long', label: t.ana_long_term, interval: '1wk' }
                            ].map((v) => (
                                <button
                                    key={v.id}
                                    onClick={() => {
                                        setSelectedView(v.id);
                                        setSelectedInterval(v.interval);
                                        // 인터벌 변경 후 즉시 검색 실행을 위해 핸들러 직접 호출
                                        const fetchUpdatedData = async () => {
                                            setLoading(true);
                                            try {
                                                const res = await axios.get(`${API_BASE}/history/${encodeURIComponent(ticker)}?interval=${v.interval}`);
                                                setHistory(res.data.data);
                                            } catch (err) { console.error(err); } finally { setLoading(false); }
                                        };
                                        fetchUpdatedData();
                                    }}
                                    className={`px-6 py-2 rounded-xl text-xs font-black transition-all ${selectedView === v.id ? (isDark ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/20' : 'bg-white text-blue-600 shadow-md') : 'text-gray-400 hover:text-gray-600'}`}
                                >
                                    {v.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                        <div className="lg:col-span-2 space-y-6">
                            <div className={`p-8 rounded-3xl border-l-[6px] border-blue-600 relative overflow-hidden ${isDark ? 'bg-slate-800/50' : 'bg-blue-50/30'}`}>
                                <div className="absolute top-4 right-6 opacity-5">
                                    <Zap className="w-24 h-24 fill-current" />
                                </div>
                                <p className="text-xl font-black mb-4 flex items-center gap-2">
                                    <MessageSquare className="w-5 h-5 text-blue-500" />
                                    Quantitative Summary
                                </p>
                                <div className="text-base leading-relaxed whitespace-pre-wrap opacity-90 font-medium tracking-tight mb-6">
                                    {analysis?.full_report || "Analyzing real-time harmonics and structural shifts..."}
                                </div>

                                <div className={`p-5 rounded-2xl border ${isDark ? 'bg-blue-500/5 border-blue-500/20' : 'bg-blue-50 border-blue-100'}`}>
                                    <p className="text-[10px] font-black text-blue-500 uppercase tracking-widest mb-2">Selected Timeframe Strategy</p>
                                    <p className="text-sm font-bold leading-relaxed whitespace-pre-wrap">
                                        {analysis?.[`${selectedView}_term`]?.recommendation || "Generating strategic alignment..."}
                                    </p>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 font-black">
                                <div className={`p-5 rounded-2xl border border-dashed transition-all hover:border-blue-500/50 ${isDark ? 'border-slate-700 bg-slate-800/20' : 'border-gray-200 bg-gray-50/50'}`}>
                                    <p className="text-[10px] text-gray-400 mb-2 uppercase tracking-widest flex items-center gap-2">
                                        <div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
                                        Technical Paradigm
                                        <HelpTooltip indicatorId="AI Score" title="기술적 분석 관점" isDark={isDark} />
                                    </p>
                                    <p className="text-sm opacity-80">{analysis?.[`${selectedView}_term`]?.focus_areas || "Calculating structural bias..."}</p>
                                </div>
                                <div className={`p-5 rounded-2xl border border-dashed transition-all hover:border-emerald-500/50 ${isDark ? 'border-slate-700 bg-slate-800/20' : 'border-gray-200 bg-gray-50/50'}`}>
                                    <p className="text-[10px] text-gray-400 mb-2 uppercase tracking-widest flex items-center gap-2">
                                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
                                        Optimized Horizon
                                        <HelpTooltip indicatorId="SMA" title="최적 보유 기간" isDark={isDark} />
                                    </p>
                                    <p className="text-sm opacity-80">{analysis?.[`${selectedView}_term`]?.holding_period || "Estimating time decay..."}</p>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <div className={`p-6 rounded-3xl shadow-2xl relative overflow-hidden transition-all duration-500 group ${isDark ? 'bg-slate-900 border border-slate-800' : 'bg-gray-900 text-white'}`}>
                                <div className="absolute -bottom-10 -right-10 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl group-hover:bg-blue-500/20 transition-all"></div>
                                <div className="flex items-center gap-2 mb-6 text-blue-400">
                                    <Zap className="w-5 h-5 fill-current" />
                                    <span className="text-xs font-black uppercase tracking-widest">Active Pattern Hub</span>
                                </div>
                                <div className="space-y-4 relative z-10">
                                    {analysis?.all_patterns?.slice(0, 3).map((p, i) => (
                                        <div key={i} className={`pb-4 last:pb-0 border-b last:border-0 ${isDark ? 'border-slate-800' : 'border-white/10'}`}>
                                            <div className="flex justify-between items-center mb-1.5">
                                                <p className="text-sm font-black group-hover:text-blue-400 transition-colors uppercase">{p.name}</p>
                                                <span className="text-[9px] font-black bg-blue-600/20 text-blue-500 px-2 py-0.5 rounded-lg border border-blue-500/20">{p.timeframe}</span>
                                            </div>
                                            <p className={`text-[11px] font-medium leading-relaxed ${isDark ? 'text-slate-400' : 'text-gray-300 opacity-70'}`}>{p.desc}</p>
                                        </div>
                                    ))}
                                    {(!analysis?.all_patterns || analysis.all_patterns.length === 0) && (
                                        <p className="text-[11px] text-gray-500 italic py-4">No structural patterns detected in the current window.</p>
                                    )}
                                </div>
                            </div>

                            <button
                                onClick={() => setIsReportOpen(true)}
                                className={`w-full py-5 rounded-2xl font-black flex items-center justify-center gap-3 transition-all transform hover:scale-[1.02] active:scale-[0.98] shadow-2xl ${isDark ? 'bg-blue-600 text-white shadow-blue-900/40 hover:bg-blue-500' : 'bg-blue-600 text-white shadow-blue-200 hover:bg-blue-700'}`}
                            >
                                <Eye className="w-6 h-6" />
                                READ FULL REPORT
                                <ChevronRight className="w-4 h-4 ml-1" />
                            </button>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default AnalysisPage;
