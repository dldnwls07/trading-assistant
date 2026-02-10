import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { StockChart } from '../components/StockChart';
import {
    Search,
    Zap,
    Activity,
    Maximize2,
    Minimize2,
    Settings,
    Star
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

const INTERVALS = [
    { label: '1m', value: '1m' },
    { label: '5m', value: '5m' },
    { label: '15m', value: '15m' },
    { label: '30m', value: '30m' },
    { label: '1h', value: '60m' },
    { label: '4h', value: '4h' },
    { label: '1D', value: '1d' },
    { label: '1W', value: '1wk' },
    { label: '1M', value: '1mo' },
];

const AnalysisPage = () => {
    const [ticker, setTicker] = useState(''); // Default Ticker removed
    const [suggestions, setSuggestions] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [analysis, setAnalysis] = useState(null);
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedInterval, setSelectedInterval] = useState('1d');
    const [isFullscreen, setIsFullscreen] = useState(false);

    // 차트 옵션 (기본값)
    const [chartOptions, setChartOptions] = useState({
        showVolume: true,
        showGrid: true,
        showSMA: true,
        showBB: true,
        showRSI: true,
        showMACD: true,
        showAIQuotes: true,
        themeColor: '#2563eb' // Blue-600
    });

    const searchRef = useRef(null);

    // 검색어 추천
    useEffect(() => {
        const fetchSuggestions = async () => {
            if (ticker.length < 1) {
                setSuggestions([]);
                return;
            }
            try {
                const res = await axios.get(`${API_BASE}/search?query=${encodeURIComponent(ticker)}`);
                setSuggestions(res.data.candidates || []);
            } catch (err) {
                console.error("Suggestion fetch failed", err);
            }
        };
        const timeoutId = setTimeout(fetchSuggestions, 300);
        return () => clearTimeout(timeoutId);
    }, [ticker]);

    // 히스토리 업데이트
    useEffect(() => {
        if (analysis?.ticker) {
            updateHistory(analysis.ticker, selectedInterval);
        }
    }, [selectedInterval]);

    // 초기 로드 시 분석 실행
    useEffect(() => {
        if (ticker) handleSearch(ticker);
    }, []);

    const updateHistory = async (symbol, interval) => {
        try {
            const res = await axios.get(`${API_BASE}/history/${encodeURIComponent(symbol)}?interval=${interval}`);
            if (res.data && Array.isArray(res.data.data)) {
                setHistory(res.data.data);
            }
        } catch (err) {
            console.error("History fetch failed", err);
        }
    };

    const handleSearch = async (s) => {
        const sym = s || ticker;
        if (!sym) return;

        setLoading(true);
        setError(null);
        // setAnalysis(null); // 기존 데이터 유지하면서 로딩 표시
        setShowSuggestions(false);

        try {
            // 병렬 처리로 속도 개선
            const [analReq, histReq] = await Promise.allSettled([
                axios.get(`${API_BASE}/analyze/${sym}`), // GET 방식으로 변경 (캐싱 등 이점)
                axios.get(`${API_BASE}/history/${encodeURIComponent(sym)}?interval=${selectedInterval}`)
            ]);

            if (analReq.status === 'fulfilled') {
                setAnalysis(analReq.value.data);
                // 검색창 티커도 업데이트 (심볼 대문자화 등)
                setTicker(analReq.value.data.ticker);
            } else {
                throw new Error(analReq.reason?.response?.data?.detail || "Analysis failed");
            }

            if (histReq.status === 'fulfilled' && histReq.value.data && Array.isArray(histReq.value.data.data)) {
                setHistory(histReq.value.data.data);
            }

        } catch (err) {
            setError(err.message || "An error occurred");
        } finally {
            setLoading(false);
        }
    };

    // UI Helpers
    const getSignalColor = (signal) => {
        if (!signal) return 'bg-gray-100 text-gray-800';
        if (signal.includes('BUY')) return 'bg-green-100 text-green-800 border-green-200';
        if (signal.includes('SELL')) return 'bg-red-100 text-red-800 border-red-200';
        return 'bg-gray-100 text-gray-800 border-gray-200';
    };

    return (
        <div className="min-h-screen bg-gray-50 pb-12 font-sans text-gray-900">
            {/* Header / Search Area */}
            <div className="bg-white border-b border-gray-200 py-6 mb-8 shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">

                        {/* Ticker Info */}
                        <div className="flex items-center gap-4">
                            <div className="h-12 w-12 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-xl shadow-md">
                                {analysis?.ticker ? analysis.ticker.substring(0, 2) : "QC"}
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">
                                    {analysis?.display_name || "Enter a Symbol"}
                                </h1>
                                <div className="flex items-center gap-2 text-sm text-gray-500">
                                    <span className="font-medium bg-gray-100 px-2 py-0.5 rounded text-xs text-gray-600">
                                        {analysis?.ticker}
                                    </span>
                                    <span>•</span>
                                    <span className="flex items-center gap-1">
                                        Scan Time: {new Date().toLocaleTimeString()}
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* Search Bar */}
                        <div className="relative w-full md:w-96" ref={searchRef}>
                            <div className="relative">
                                <input
                                    type="text"
                                    value={ticker}
                                    onChange={(e) => { setTicker(e.target.value.toUpperCase()); setShowSuggestions(true); }}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                                    placeholder="Search Ticker (e.g. TSLA)"
                                    className="block w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 sm:text-sm shadow-sm transition-all"
                                />
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Search className="h-5 w-5 text-gray-400" />
                                </div>
                                <button
                                    onClick={() => handleSearch()}
                                    className="absolute inset-y-0 right-0 px-4 flex items-center bg-blue-600 hover:bg-blue-700 text-white rounded-r-lg font-medium text-sm transition-colors"
                                >
                                    {loading ? <Activity className="w-4 h-4 animate-spin" /> : "GO"}
                                </button>
                            </div>

                            {/* Suggestions Dropdown */}
                            <AnimatePresence>
                                {showSuggestions && suggestions.length > 0 && (
                                    <motion.ul
                                        initial={{ opacity: 0, y: -10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: -10 }}
                                        className="absolute z-50 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm"
                                    >
                                        {suggestions.map((s, idx) => (
                                            <li
                                                key={idx}
                                                onClick={() => { setTicker(s.symbol); handleSearch(s.symbol); }}
                                                className="cursor-pointer select-none relative py-2 pl-3 pr-9 hover:bg-gray-100 transition-colors"
                                            >
                                                <div className="flex items-center justify-between">
                                                    <span className="font-bold text-gray-900">{s.symbol}</span>
                                                    <span className="text-gray-500 text-xs truncate ml-2">{s.shortname}</span>
                                                </div>
                                            </li>
                                        ))}
                                    </motion.ul>
                                )}
                            </AnimatePresence>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">

                {/* 1. Score & Signal Cards (Top Row) */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    {/* Score Card */}
                    <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200 p-5 flex flex-col items-center justify-center text-center">
                        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">AI Confidence Score</h3>
                        <div className="relative flex items-center justify-center">
                            <svg className="w-24 h-24 transform -rotate-90">
                                <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-gray-200" />
                                <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" strokeDasharray={251.2} strokeDashoffset={251.2 - (251.2 * (analysis?.final_score || 0)) / 100} className={`transition-all duration-1000 ease-out ${analysis?.final_score >= 70 ? 'text-green-500' : analysis?.final_score >= 40 ? 'text-yellow-500' : 'text-red-500'}`} />
                            </svg>
                            <span className="absolute text-3xl font-bold text-gray-800">{analysis?.final_score ?? '--'}</span>
                        </div>
                    </div>

                    {/* Signal Card */}
                    <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200 p-5 flex flex-col items-center justify-center">
                        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-4">Trading Signal</h3>
                        <span className={`px-6 py-2 rounded-full text-lg font-bold border ${getSignalColor(analysis?.signal)} shadow-sm`}>
                            {analysis?.signal || 'WAITING...'}
                        </span>
                        <p className="mt-3 text-xs text-gray-400">Based on multi-factor analysis</p>
                    </div>

                    {/* Target Price Card */}
                    <div className="md:col-span-2 bg-white overflow-hidden shadow rounded-lg border border-gray-200 p-5">
                        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-4">Tactical Price Targets</h3>
                        <div className="grid grid-cols-3 gap-4 text-center h-full items-center">
                            <div>
                                <p className="text-xs text-gray-400 mb-1">Defense (Stop)</p>
                                <p className="text-xl font-bold text-red-600">{analysis?.entry_points?.stop || '--'}</p>
                            </div>
                            <div className="border-x border-gray-100 px-2">
                                <p className="text-xs text-blue-500 font-bold mb-1">Entry Zone</p>
                                <p className="text-2xl font-black text-gray-900">{analysis?.entry_points?.buy || '--'}</p>
                            </div>
                            <div>
                                <p className="text-xs text-gray-400 mb-1">Target (Exit)</p>
                                <p className="text-xl font-bold text-green-600">{analysis?.entry_points?.target || '--'}</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 2. Chart Section */}
                <div className="bg-white shadow rounded-lg border border-gray-200 overflow-hidden">
                    {/* Toolbar */}
                    <div className="border-b border-gray-200 bg-gray-50 px-4 py-3 sm:px-6 flex flex-wrap items-center justify-between gap-2">
                        <div className="flex space-x-1">
                            {INTERVALS.map((int) => (
                                <button
                                    key={int.value}
                                    onClick={() => setSelectedInterval(int.value)}
                                    className={`px-3 py-1.5 rounded text-xs font-semibold transition-colors ${selectedInterval === int.value ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-600 hover:bg-gray-200'}`}
                                >
                                    {int.label}
                                </button>
                            ))}
                        </div>
                        <div className="flex items-center space-x-2">
                            <button className="p-1.5 rounded hover:bg-gray-200 text-gray-500" title="Chart Settings" onClick={() => { /* Toggle Settings */ }}>
                                <Settings className="w-4 h-4" />
                            </button>
                            <div className="h-4 w-px bg-gray-300 mx-2"></div>
                            <span className="text-xs font-medium text-blue-600 flex items-center gap-1">
                                <Zap className="w-3 h-3 fill-current" /> AI Patterns On
                            </span>
                        </div>
                    </div>

                    {/* Chart Container */}
                    <div className="relative h-[600px] w-full bg-[#131722]">
                        {history.length > 0 ? (
                            <StockChart
                                data={history}
                                interval={selectedInterval}
                                options={chartOptions}
                                analysis={analysis}
                            />
                        ) : (
                            <div className="flex items-center justify-center h-full text-gray-500">
                                {loading ? "Loading Market Data..." : "No Data Available"}
                            </div>
                        )}
                    </div>
                </div>

                {/* 3. Detailed Report */}
                <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-blue-600" />
                        Strategic Analysis Report
                    </h3>
                    <div className="prose prose-blue max-w-none text-gray-700 text-sm leading-relaxed whitespace-pre-wrap">
                        {analysis?.full_report || "Select a stock to generate a comprehensive AI report."}
                    </div>
                </div>

                {/* 4. Pattern Recognition List */}
                {analysis?.daily_analysis?.patterns?.length > 0 && (
                    <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
                        <h3 className="text-lg font-bold text-gray-900 mb-4">Detected Chart Patterns</h3>
                        <div className="overflow-hidden">
                            <ul className="divide-y divide-gray-200">
                                {analysis.daily_analysis.patterns.map((p, idx) => (
                                    <li key={idx} className="py-4 flex items-start space-x-4">
                                        <div className="flex-shrink-0">
                                            <span className={`inline-flex items-center justify-center h-8 w-8 rounded-full ${p.reliability >= 4 ? 'bg-green-100' : 'bg-yellow-100'}`}>
                                                <Star className={`h-5 w-5 ${p.reliability >= 4 ? 'text-green-600' : 'text-yellow-600'}`} />
                                            </span>
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium text-gray-900 truncate">{p.name}</p>
                                            <p className="text-xs text-gray-500 mt-1">{p.desc}</p>
                                        </div>
                                        <div className="inline-flex items-center shadow-sm px-2.5 py-0.5 border border-gray-300 text-xs font-medium rounded-full text-gray-700 bg-white">
                                            Reliability: {p.reliability}/5
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
};

export default AnalysisPage;
