import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { PieChart, Plus, Trash2, ArrowUpRight, TrendingUp, ShieldAlert, BarChart, DollarSign, TrendingDown, Wallet, Target, Activity } from 'lucide-react';
import { useTranslation } from '../utils/translations';

const API_BASE = 'http://127.0.0.1:8000';

// 한국 종목 코드 자동 감지 및 변환
const normalizeTickerForAPI = (ticker) => {
    if (ticker.endsWith('.KS') || ticker.endsWith('.KQ')) return ticker;
    if (/^\d{6}$/.test(ticker)) return `${ticker}.KS`;
    return ticker;
};

// 통화 감지 (한국 종목이면 원화, 아니면 달러)
const getCurrency = (ticker) => {
    if (ticker.endsWith('.KS') || ticker.endsWith('.KQ') || /^\d{6}$/.test(ticker)) {
        return { symbol: '₩', name: 'KRW' };
    }
    return { symbol: '$', name: 'USD' };
};

// 숫자 포맷팅
const formatNumber = (num, decimals = 0) => {
    if (!num && num !== 0) return 'N/A';
    return num.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
};

const PortfolioPage = ({ settings }) => {
    const t = useTranslation(settings);
    const [holdings, setHoldings] = useState([
        { ticker: 'AAPL', shares: 10, avg_price: 150 },
        { ticker: 'TSLA', shares: 5, avg_price: 200 }
    ]);
    const [newHolding, setNewHolding] = useState({ ticker: '', shares: '', avg_price: '' });
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [suggestions, setSuggestions] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const searchRef = useRef(null);

    const isDark = settings?.darkMode;

    const addHolding = () => {
        if (!newHolding.ticker || !newHolding.shares || !newHolding.avg_price) return;
        if (newHolding.shares <= 0 || newHolding.avg_price < 0) {
            alert(t.invalidInput || "수량과 가격은 양수여야 합니다.");
            return;
        }
        setHoldings([...holdings, { ...newHolding }]);
        setNewHolding({ ticker: '', shares: '', avg_price: '' });
        setSuggestions([]);
        setShowSuggestions(false);
    };

    // 실시간 종목 검색 및 외부 클릭 핸들링
    useEffect(() => {
        const fetchSuggestions = async () => {
            if (!newHolding.ticker || newHolding.ticker.length < 1) {
                setSuggestions([]);
                return;
            }
            try {
                const res = await axios.get(`${API_BASE}/search?query=${encodeURIComponent(newHolding.ticker)}`);
                setSuggestions(res.data.candidates || []);
            } catch (err) {
                console.error("Search error:", err);
            }
        };

        const timeoutId = setTimeout(fetchSuggestions, 300);
        return () => clearTimeout(timeoutId);
    }, [newHolding.ticker]);

    // 외부 클릭 시 닫기
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (searchRef.current && !searchRef.current.contains(e.target)) {
                setShowSuggestions(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const removeHolding = (idx) => {
        const newHoldings = [...holdings];
        newHoldings.splice(idx, 1);
        setHoldings(newHoldings);
    };

    const analyzePortfolio = async () => {
        if (holdings.length === 0) return;
        setLoading(true);
        try {
            const normalizedHoldings = holdings.map(h => ({
                ...h,
                ticker: normalizeTickerForAPI(h.ticker)
            }));

            const res = await axios.post(`${API_BASE}/api/portfolio/analyze`, { holdings: normalizedHoldings });
            setAnalysis(res.data);
        } catch (err) {
            console.error(err);
            alert(t.noData || '오류 발생');
        } finally {
            setLoading(false);
        }
    };

    // 포트폴리오 실시간/입력 요약 계산
    const portfolioSummary = holdings.reduce((acc, h) => {
        const cost = h.shares * h.avg_price;
        acc.totalShares += h.shares;
        acc.totalPrinciple += cost;
        return acc;
    }, { totalShares: 0, totalPrinciple: 0 });

    // 분석 데이터가 있을 때의 상세 메트릭
    const currentTotalValue = analysis?.total_value || 0;
    const totalProfit = analysis?.total_profit_loss || 0;
    const profitRate = analysis?.total_profit_loss_pct || 0;

    return (
        <div className={`min-h-screen py-10 transition-colors duration-300 ${isDark ? 'bg-slate-950 text-slate-100' : 'bg-gray-50 text-gray-900'}`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
                <div className="flex items-center justify-between">
                    <h1 className="text-3xl font-black flex items-center gap-3">
                        <div className="bg-blue-600 p-2 rounded-xl text-white shadow-lg shadow-blue-500/20">
                            <PieChart className="w-7 h-7" />
                        </div>
                        {t.portfolio}
                    </h1>
                    <div className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border ${isDark ? 'bg-slate-900 border-slate-800 text-slate-500' : 'bg-white border-gray-200 text-gray-400'}`}>
                        Real-time Exposure Engine
                    </div>
                </div>

                {/* Detailed Performance Dashboard (Top Bar) */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className={`p-6 rounded-3xl shadow-xl border ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                        <div className="flex items-center gap-3 mb-2 opacity-50">
                            <Wallet className="w-4 h-4" />
                            <span className="text-[10px] font-black uppercase tracking-widest">{t.totalPrinciple}</span>
                        </div>
                        <p className="text-2xl font-black">
                            <span className="text-sm mr-1 opacity-50">$</span>
                            {formatNumber(portfolioSummary.totalPrinciple, 0)}
                        </p>
                    </div>
                    <div className={`p-6 rounded-3xl shadow-xl border ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                        <div className="flex items-center gap-3 mb-2 opacity-50">
                            <Activity className="w-4 h-4" />
                            <span className="text-[10px] font-black uppercase tracking-widest">{t.totalValue}</span>
                        </div>
                        <p className="text-2xl font-black text-blue-500">
                            {analysis ? (
                                <>
                                    <span className="text-sm mr-1 opacity-50">$</span>
                                    {formatNumber(currentTotalValue, 0)}
                                </>
                            ) : "---"}
                        </p>
                    </div>
                    <div className={`p-6 rounded-3xl shadow-xl border ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                        <div className="flex items-center gap-3 mb-2 opacity-50">
                            <TrendingUp className="w-4 h-4" />
                            <span className="text-[10px] font-black uppercase tracking-widest">{t.profit}</span>
                        </div>
                        <p className={`text-2xl font-black ${totalProfit >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                            {analysis ? (
                                <>
                                    <span className="text-sm mr-1 opacity-50">$</span>
                                    {totalProfit > 0 ? '+' : ''}{formatNumber(totalProfit, 0)}
                                </>
                            ) : "---"}
                        </p>
                    </div>
                    <div className={`p-6 rounded-3xl shadow-xl border ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                        <div className="flex items-center gap-3 mb-2 opacity-50">
                            <Target className="w-4 h-4" />
                            <span className="text-[10px] font-black uppercase tracking-widest">{t.return}</span>
                        </div>
                        <p className={`text-2xl font-black ${profitRate >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                            {analysis ? `${profitRate > 0 ? '+' : ''}${profitRate.toFixed(2)}%` : "---"}
                        </p>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Asset Hub / Input */}
                    <div className={`shadow-xl rounded-3xl border p-8 h-fit sticky top-24 transition-colors ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                        <h2 className="text-xl font-black mb-6 flex items-center justify-between">
                            {t.assetHub}
                            <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${isDark ? 'bg-slate-800 text-blue-400' : 'bg-blue-50 text-blue-600'}`}>{holdings.length} Assets</span>
                        </h2>

                        <ul className={`divide-y mb-8 ${isDark ? 'divide-slate-800' : 'divide-gray-100'}`}>
                            {holdings.map((h, idx) => {
                                const currency = getCurrency(h.ticker);
                                return (
                                    <li key={idx} className="py-4 flex justify-between items-center group">
                                        <div className="flex items-center gap-4">
                                            <div className={`h-11 w-11 rounded-2xl flex items-center justify-center font-black text-xs shadow-inner ${isDark ? 'bg-slate-800 text-blue-400' : 'bg-gray-50 text-gray-500'}`}>
                                                {h.ticker.substring(0, 2)}
                                            </div>
                                            <div>
                                                <p className="font-black text-sm">{h.ticker}</p>
                                                <p className={`text-[11px] font-bold ${isDark ? 'text-slate-500' : 'text-gray-400'}`}>
                                                    {h.shares}{t.shares} @ {currency.symbol}{formatNumber(h.avg_price, 0)}
                                                </p>
                                            </div>
                                        </div>
                                        <button onClick={() => removeHolding(idx)} className={`p-2 rounded-lg opacity-0 group-hover:opacity-100 transition-all ${isDark ? 'hover:bg-rose-500/10 text-slate-500 hover:text-rose-500' : 'hover:bg-rose-50 text-gray-400 hover:text-rose-500'}`}>
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </li>
                                );
                            })}
                        </ul>

                        <div className="space-y-4 mb-6">
                            <div className="grid grid-cols-1 gap-4">
                                <div className="relative" ref={searchRef}>
                                    <div className={`flex items-center px-4 py-3 rounded-2xl border transition-all ${isDark ? 'bg-slate-800 border-slate-700 focus-within:border-blue-500/50' : 'bg-gray-50 border-gray-200 focus-within:border-blue-500'}`}>
                                        <span className="text-[10px] font-black text-gray-400 w-20 uppercase italic">{t.ticker}</span>
                                        <input
                                            placeholder="삼성전자 or AAPL"
                                            value={newHolding.ticker}
                                            onFocus={() => setShowSuggestions(true)}
                                            onChange={e => {
                                                setNewHolding({ ...newHolding, ticker: e.target.value.toUpperCase() });
                                                setShowSuggestions(true);
                                            }}
                                            className="w-full bg-transparent border-none outline-none font-black text-sm placeholder:text-gray-300"
                                        />
                                    </div>

                                    {/* Autocomplete Dropdown */}
                                    {showSuggestions && suggestions.length > 0 && (
                                        <div className={`absolute z-50 left-0 right-0 mt-2 rounded-2xl shadow-2xl border overflow-hidden max-h-60 overflow-y-auto ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-100'}`}>
                                            {suggestions.map((s, idx) => (
                                                <div
                                                    key={idx}
                                                    onClick={() => {
                                                        setNewHolding({ ...newHolding, ticker: s.symbol });
                                                        setShowSuggestions(false);
                                                    }}
                                                    className={`p-4 cursor-pointer flex justify-between items-center transition-colors ${isDark ? 'hover:bg-slate-700' : 'hover:bg-gray-50'}`}
                                                >
                                                    <div>
                                                        <p className="font-black text-xs">{s.name}</p>
                                                        <p className="text-[10px] opacity-50">{s.symbol} • {s.exchange}</p>
                                                    </div>
                                                    {s.is_korean && <span className="text-[10px] bg-blue-500/10 text-blue-500 px-2 py-0.5 rounded-full font-bold">KR</span>}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className={`flex items-center px-4 py-3 rounded-2xl border transition-all ${isDark ? 'bg-slate-800 border-slate-700 focus-within:border-blue-500/50' : 'bg-gray-50 border-gray-200 focus-within:border-blue-500'}`}>
                                        <span className="text-[10px] font-black text-gray-400 w-12 uppercase italic">{t.shares}</span>
                                        <input
                                            type="number"
                                            min="0"
                                            value={newHolding.shares}
                                            onChange={e => setNewHolding({ ...newHolding, shares: Math.max(0, Number(e.target.value)) })}
                                            className="w-full bg-transparent border-none outline-none font-black text-sm"
                                        />
                                    </div>
                                    <div className={`flex items-center px-4 py-3 rounded-2xl border transition-all ${isDark ? 'bg-slate-800 border-slate-700 focus-within:border-blue-500/50' : 'bg-gray-50 border-gray-200 focus-within:border-blue-500'}`}>
                                        <span className="text-[10px] font-black text-gray-400 w-12 uppercase italic">{t.avgPrice}</span>
                                        <input
                                            type="number"
                                            min="0"
                                            value={newHolding.avg_price}
                                            onChange={e => setNewHolding({ ...newHolding, avg_price: Math.max(0, Number(e.target.value)) })}
                                            className="w-full bg-transparent border-none outline-none font-black text-sm"
                                        />
                                    </div>
                                </div>
                            </div>
                            <button onClick={addHolding} className={`w-full py-4 rounded-2xl font-black text-xs flex items-center justify-center gap-2 transition-all ${isDark ? 'bg-slate-800 hover:bg-slate-700 text-slate-300' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}>
                                <Plus className="w-4 h-4" /> {t.addPortfolio}
                            </button>
                        </div>

                        <button
                            onClick={analyzePortfolio}
                            disabled={loading || holdings.length === 0}
                            className={`w-full py-4 rounded-2xl font-black text-sm shadow-2xl transition-all transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 flex items-center justify-center gap-3 ${isDark ? 'bg-blue-600 text-white shadow-blue-900/40' : 'bg-blue-600 text-white shadow-blue-200 hover:bg-blue-700'}`}
                        >
                            {loading ? (
                                <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            ) : (
                                <>{t.runAnalysis} <ArrowUpRight className="w-5 h-5" /></>
                            )}
                        </button>
                    </div>

                    {/* Results Section */}
                    <div className="lg:col-span-2 space-y-8">
                        {analysis ? (
                            <>
                                {/* Matrix Grid */}
                                <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                                    {[
                                        { label: t.diversification, value: analysis.diversification?.grade, color: analysis.diversification?.score > 70 ? 'text-emerald-500' : 'text-rose-500' },
                                        { label: t.correlation, value: analysis.correlations?.avg_correlation?.toFixed(3), color: 'text-blue-500' },
                                        { label: t.riskScore, value: `${analysis.portfolio_score}/100`, color: 'text-purple-500' }
                                    ].map((m, i) => (
                                        <div key={i} className={`p-6 rounded-3xl shadow-xl border text-center transition-all ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                                            <p className="text-[10px] text-gray-400 uppercase font-black mb-2 tracking-widest">{m.label}</p>
                                            <p className={`text-2xl font-black ${m.color}`}>{m.value}</p>
                                        </div>
                                    ))}
                                </div>

                                {/* Rebalancing & Correlation Row */}
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                    <div className={`rounded-[2.5rem] shadow-xl border p-8 transition-colors ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                                        <h3 className="text-xs font-black text-blue-500 uppercase tracking-widest mb-6 flex items-center gap-2">
                                            <TrendingUp className="w-4 h-4" />
                                            {t.rebalancing}
                                        </h3>
                                        <div className={`p-6 rounded-3xl mb-6 border-l-4 border-blue-500 ${isDark ? 'bg-slate-800/50' : 'bg-blue-50/30'}`}>
                                            <p className="text-sm font-medium leading-relaxed opacity-90 whitespace-pre-wrap">{analysis.summary}</p>
                                        </div>
                                        <div className="space-y-4">
                                            <h4 className="text-[10px] font-black text-gray-400 uppercase tracking-widest">{t.signals}</h4>
                                            {((analysis.rebalancing?.sell || []).concat(analysis.rebalancing?.adjust || [])).map((rec, idx) => (
                                                <div key={idx} className={`flex items-center justify-between p-5 rounded-3xl border transition-all ${isDark ? 'bg-rose-500/5 border-rose-500/20' : 'bg-rose-50 border-rose-100'}`}>
                                                    <div>
                                                        <span className={`font-black text-sm ${isDark ? 'text-rose-400' : 'text-rose-700'}`}>{rec.ticker}</span>
                                                        <p className={`text-[11px] font-bold opacity-60 ${isDark ? 'text-rose-300' : 'text-rose-600'}`}>{rec.reason}</p>
                                                    </div>
                                                    <span className={`text-[9px] font-black uppercase px-3 py-1.5 rounded-full border ${isDark ? 'bg-slate-900 text-rose-400 border-rose-500/30' : 'bg-white text-rose-700 border-rose-200'}`}>{rec.action}</span>
                                                </div>
                                            ))}
                                            {(analysis.rebalancing?.sell?.length === 0 && (!analysis.rebalancing?.adjust || analysis.rebalancing.adjust.length === 0)) && (
                                                <div className={`text-center py-10 rounded-3xl border-2 border-dashed ${isDark ? 'border-slate-800 text-slate-600' : 'border-gray-100 text-gray-400'}`}>
                                                    <ShieldAlert className="w-10 h-10 mx-auto mb-3 opacity-20" />
                                                    <p className="text-xs font-black italic">{t.optimal}</p>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    <div className={`rounded-[2.5rem] shadow-xl border p-8 transition-colors ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                                        <h3 className="text-xs font-black text-gray-400 uppercase tracking-widest mb-6 flex items-center gap-2">
                                            <BarChart className="w-4 h-4" />
                                            {t.matrix}
                                        </h3>
                                        <div className="overflow-x-auto custom-scrollbar pb-4 text-center">
                                            <table className="inline-block text-[10px]">
                                                <thead>
                                                    <tr>
                                                        <th className="p-3"></th>
                                                        {Object.keys(analysis.correlations?.matrix || {}).map(t => (
                                                            <th key={t} className="p-3 font-black text-gray-400 uppercase tracking-tight">{t}</th>
                                                        ))}
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {Object.entries(analysis.correlations?.matrix || {}).map(([t1, row]) => (
                                                        <tr key={t1} className={`border-t ${isDark ? 'border-slate-800' : 'border-gray-50'}`}>
                                                            <td className="p-3 font-black text-gray-400 uppercase">{t1}</td>
                                                            {Object.values(row).map((v, i) => (
                                                                <td key={i} className={`p-3 text-center font-black rounded-xl transition-all ${v > 0.7 ? (isDark ? 'bg-rose-500/20 text-rose-400' : 'bg-rose-100 text-rose-700') : v < 0.3 ? (isDark ? 'bg-emerald-500/20 text-emerald-400' : 'bg-emerald-100 text-emerald-700') : 'opacity-60'}`}>
                                                                    {v.toFixed(2)}
                                                                </td>
                                                            ))}
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                        <div className={`mt-8 p-6 rounded-3xl border flex items-start gap-4 ${isDark ? 'bg-slate-800/30 border-slate-800' : 'bg-gray-50 border-gray-100'}`}>
                                            <div className="p-2 bg-blue-500/10 rounded-xl text-blue-500">
                                                <ShieldAlert className="w-5 h-5" />
                                            </div>
                                            <p className="text-[11px] font-medium leading-relaxed opacity-60">
                                                <strong>{t.tip}:</strong> Assets with correlation below 0.3 significantly reduce overall volatility. Current average is <strong>{analysis.correlations?.avg_correlation?.toFixed(3)}</strong>.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div className={`h-[600px] flex flex-col items-center justify-center rounded-[2.5rem] border-2 border-dashed transition-all ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-gray-50 border-gray-200'}`}>
                                <div className={`w-24 h-24 rounded-full flex items-center justify-center mb-6 opacity-20 ${isDark ? 'bg-slate-800' : 'bg-white shadow-xl'}`}>
                                    <PieChart className="w-12 h-12" />
                                </div>
                                <p className="text-xl font-black opacity-30 tracking-tight uppercase italic mb-2">Neural Analysis Pending</p>
                                <p className="text-xs font-bold opacity-20 uppercase tracking-[0.3em]">Configure assets to start computation</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PortfolioPage;
