import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { StockChart } from '../components/StockChart';
import { Search, Clock, Eye, ChevronRight, Activity } from 'lucide-react';
import { useTranslation } from '../utils/translations';

// 서브 컴포넌트 임포트
import StrategyCard from '../components/analysis/StrategyCard';
import TradingSetup from '../components/analysis/TradingSetup';
import AnalysisInsights from '../components/analysis/AnalysisInsights';

const API_BASE = 'http://127.0.0.1:8000';
// 브라우저 환경이므로 .env 접근이 어려울 수 있으나, 여기서는 백엔드와 맞춘 기본값 사용
const API_KEY = "trading-assistant-secret-2024";

const AXIOS_CONFIG = {
    headers: { 'X-API-Key': API_KEY }
};

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
    const [selectedView, setSelectedView] = useState('medium');
    const [chartType, setChartType] = useState('Candle');
    const [isReportOpen, setIsReportOpen] = useState(false);

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

    const handleSearch = async (s) => {
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
            if (histReq.status === 'fulfilled') setHistory(histReq.value.data.data);
        } catch (err) { console.error(err); } finally { setLoading(false); }
    };

    const handleUpdateHistory = async (interval) => {
        setLoading(true);
        try {
            const res = await axios.get(`${API_BASE}/history/${encodeURIComponent(ticker)}?interval=${interval}`, AXIOS_CONFIG);
            setHistory(res.data.data);
        } catch (err) { console.error(err); } finally { setLoading(false); }
    };

    useEffect(() => { if (tickerParam) handleSearch(tickerParam); }, [tickerParam]);

    return (
        <div className={`min-h-screen pb-12 transition-colors duration-300 ${isDark ? 'bg-slate-950 text-slate-100' : 'bg-gray-50 text-gray-900'}`}>
            {/* Full Report Modal */}
            <AnimatePresence>
                {isReportOpen && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                        <motion.div initial={{ opacity: 0, scale: 0.95, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.95, y: 20 }}
                            className={`w-full max-w-4xl max-h-[90vh] overflow-hidden rounded-3xl shadow-2xl flex flex-col ${isDark ? 'bg-slate-900 text-slate-100 border border-slate-800' : 'bg-white text-gray-900'}`}>
                            <div className={`p-6 border-b flex items-center justify-between ${isDark ? 'border-slate-800' : 'border-gray-100'}`}>
                                <div className="flex items-center gap-3">
                                    <div className="bg-blue-600 p-2 rounded-xl text-white"><Eye className="w-5 h-5" /></div>
                                    <div><h2 className="text-xl font-black">AI Detail Analysis Report</h2><p className="text-xs opacity-50">{analysis?.display_name} ({analysis?.ticker})</p></div>
                                </div>
                                <button onClick={() => setIsReportOpen(false)} className="p-2 rounded-full hover:bg-opacity-10 transition-colors"><span className="text-2xl leading-none">&times;</span></button>
                            </div>
                            <div className="p-8 overflow-y-auto custom-scrollbar">
                                <div className={`prose prose-sm max-w-none ${isDark ? 'prose-invert' : ''}`}>
                                    <div className="whitespace-pre-wrap leading-relaxed font-medium opacity-90 text-base">{analysis?.full_report || "리포트를 불러오는 중..."}</div>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {/* Header / Search Area (간소화) */}
            <div className={`border-b py-8 mb-8 shadow-sm ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-6">
                    <div className="flex items-center gap-5">
                        <div className="h-14 w-14 rounded-2xl bg-blue-600 flex items-center justify-center text-white font-black text-2xl shadow-xl shadow-blue-500/30">{analysis?.ticker?.substring(0, 2) || "AN"}</div>
                        <div>
                            <div className="flex items-center gap-2 mb-0.5"><h1 className="text-3xl font-black tracking-tight">{analysis?.display_name || "Stock Assistant"}</h1></div>
                            <div className="flex items-center gap-2 text-sm opacity-50 font-medium"><Clock className="w-3.5 h-3.5" /><span>{new Date().toLocaleTimeString()} • Live Analysis</span></div>
                        </div>
                    </div>
                    <div className="relative w-full md:w-[450px]">
                        <div className={`flex items-center px-4 py-3.5 rounded-2xl border transition-all duration-300 group ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-gray-50 border-gray-200'}`}>
                            <Search className="h-5 w-5 mr-3 text-gray-400" />
                            <input type="text" value={ticker} onChange={(e) => { setTicker(e.target.value.toUpperCase()); setShowSuggestions(true); }} onKeyDown={(e) => e.key === 'Enter' && handleSearch()} placeholder={t.ana_search_placeholder} className="w-full bg-transparent border-none outline-none font-bold" />
                            {loading && <div className="ml-2 h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>}
                        </div>
                        {showSuggestions && suggestions.length > 0 && (
                            <div className={`absolute left-0 right-0 mt-2 rounded-2xl shadow-2xl z-50 border overflow-hidden ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-100'}`}>
                                {suggestions.map((s, i) => (
                                    <button key={i} onClick={() => { setTicker(s.symbol); handleSearch(s.symbol); }} className={`w-full px-5 py-3.5 text-left flex items-center justify-between hover:bg-blue-500 hover:text-white transition-colors border-b last:border-0 ${isDark ? 'border-slate-700' : 'border-gray-50'}`}>
                                        <div className="flex items-center gap-3"><span className="font-black text-sm">{s.symbol}</span><span className="text-xs opacity-70 font-medium">{s.name}</span></div>
                                        <ChevronRight className="w-4 h-4 opacity-30" />
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <main className="max-w-7xl mx-auto px-4 space-y-8">
                {/* 1. Alpha Strategy Dashboard */}
                <StrategyCard analysis={analysis} isDark={isDark} />

                {/* 1.5 Strategic Trading Setup */}
                <TradingSetup analysis={analysis} isDark={isDark} />

                {/* 2. Chart Section */}
                <div className={`rounded-3xl border shadow-2xl overflow-hidden ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                    <div className={`p-4 flex items-center justify-between gap-4 flex-wrap border-b ${isDark ? 'bg-slate-900/50 border-slate-800' : 'bg-gray-50/50 border-gray-100'}`}>
                        <div className={`flex bg-black/5 p-1 rounded-2xl ${isDark ? 'bg-white/5' : ''}`}>
                            {INTERVALS.map((int) => (
                                <button key={int.value} onClick={() => { setSelectedInterval(int.value); handleSearch(); }} className={`px-4 py-1.5 rounded-xl text-[11px] font-black transition-all ${selectedInterval === int.value ? 'bg-blue-600 text-white' : 'text-gray-500 hover:text-gray-900'}`}>{int.label}</button>
                            ))}
                        </div>
                    </div>
                    <div className={`h-[550px] w-full relative ${isDark ? 'bg-[#131722]' : 'bg-gray-50'}`}>
                        {loading && <div className="absolute inset-0 z-10 bg-black/20 backdrop-blur-[2px] flex items-center justify-center"><Activity className="w-12 h-12 text-blue-500 animate-spin" /></div>}
                        {history.length > 0 ? (
                            <StockChart data={history} interval={selectedInterval} chartType={chartType} options={settings} analysis={analysis} />
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-gray-500 gap-4"><Activity className="w-12 h-12 animate-pulse text-blue-500" /><p className="font-black text-sm uppercase tracking-widest opacity-40 italic">Decoding Market Frequency...</p></div>
                        )}
                    </div>
                </div>

                {/* 3. Multi-View Analysis Report (인사이트 엔진) */}
                <AnalysisInsights
                    analysis={analysis}
                    selectedView={selectedView} setSelectedView={setSelectedView}
                    setSelectedInterval={setSelectedInterval}
                    isDark={isDark} t={t}
                    onOpenReport={() => setIsReportOpen(true)}
                    onUpdateHistory={handleUpdateHistory}
                />
            </main>
        </div>
    );
};

export default AnalysisPage;
