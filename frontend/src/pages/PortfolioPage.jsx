import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { PieChart, Plus, Trash2, ArrowUpRight, TrendingUp, ShieldAlert, BarChart, DollarSign, TrendingDown, Wallet, Target, Activity, Cpu, History, RefreshCcw } from 'lucide-react';
import { useTranslation } from '../utils/translations';

const API_BASE = 'http://127.0.0.1:8000';

// 한국 종목 코드 자동 감지 및 변환
const normalizeTickerForAPI = (ticker) => {
    if (ticker.endsWith('.KS') || ticker.endsWith('.KQ')) return ticker;
    if (/^\d{6}$/.test(ticker)) return `${ticker}.KS`;
    return ticker;
};

// 숫자 포맷팅
const formatNumber = (num, decimals = 0) => {
    if (!num && num !== 0) return '0';
    return num.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
};

const PortfolioPage = ({ settings }) => {
    const t = useTranslation(settings);
    const [activeTab, setActiveTab] = useState('manual');
    const [displayCurrency, setDisplayCurrency] = useState('KRW'); // 'KRW' or 'USD'

    // 수동 포트폴리오 상태
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

    // 가상 포트폴리오 및 환율 상태
    const [virtualAccount, setVirtualAccount] = useState(null);
    const [virtualPositions, setVirtualPositions] = useState([]);
    const [exchangeRate, setExchangeRate] = useState(1350);
    const [virtualLoading, setVirtualLoading] = useState(false);

    const isDark = settings?.darkMode;

    // 데이터 로드
    const fetchData = async () => {
        setVirtualLoading(true);
        try {
            const [accRes, posRes, rateRes] = await Promise.all([
                axios.get(`${API_BASE}/api/virtual/account`),
                axios.get(`${API_BASE}/api/virtual/positions`),
                axios.get(`${API_BASE}/api/exchange-rate`)
            ]);
            setVirtualAccount(accRes.data);
            setVirtualPositions(posRes.data);
            setExchangeRate(rateRes.data.rate);
        } catch (err) {
            console.error("Data fetch error:", err);
        } finally {
            setVirtualLoading(false);
        }
    };

    useEffect(() => {
        if (activeTab === 'virtual') {
            fetchData();
        }
    }, [activeTab]);

    const addHolding = () => {
        if (!newHolding.ticker || !newHolding.shares || !newHolding.avg_price) return;
        setHoldings([...holdings, { ...newHolding }]);
        setNewHolding({ ticker: '', shares: '', avg_price: '' });
    };

    const removeHolding = (idx) => {
        const newHoldings = [...holdings];
        newHoldings.splice(idx, 1);
        setHoldings(newHoldings);
    };

    // 금액 변환 함수
    const convert = (value, targetCurrency) => {
        if (displayCurrency === 'KRW') {
            return targetCurrency === 'USD' ? value / exchangeRate : value;
        } else {
            return targetCurrency === 'KRW' ? value * exchangeRate : value;
        }
    };

    const getSymbol = () => displayCurrency === 'KRW' ? '₩' : '$';

    // 요약 메트릭 계산
    const totalValue = activeTab === 'manual'
        ? (analysis?.total_value || 0)
        : (virtualPositions.reduce((acc, p) => acc + p.total_value_krw, 0) + (virtualAccount?.balance || 0));

    const initialCapital = 10000000;
    const currentProfit = totalValue - initialCapital;
    const currentProfitRate = (currentProfit / initialCapital) * 100;

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

                    <div className="flex items-center gap-4">
                        {/* Currency Toggle */}
                        <div className={`flex p-1 rounded-xl border ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-200'}`}>
                            <button
                                onClick={() => setDisplayCurrency('KRW')}
                                className={`px-4 py-1.5 rounded-lg text-[10px] font-black transition-all ${displayCurrency === 'KRW' ? 'bg-blue-600 text-white' : 'text-gray-400'}`}
                            >
                                KRW (₩)
                            </button>
                            <button
                                onClick={() => setDisplayCurrency('USD')}
                                className={`px-4 py-1.5 rounded-lg text-[10px] font-black transition-all ${displayCurrency === 'USD' ? 'bg-blue-600 text-white' : 'text-gray-400'}`}
                            >
                                USD ($)
                            </button>
                        </div>

                        {/* Tab Switcher */}
                        <div className={`flex p-1 rounded-xl border ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-200'}`}>
                            <button
                                onClick={() => setActiveTab('manual')}
                                className={`px-4 py-1.5 rounded-lg text-[10px] font-black transition-all ${activeTab === 'manual' ? (isDark ? 'bg-slate-800 text-blue-400' : 'bg-gray-100 text-blue-600') : 'text-gray-400'}`}
                            >
                                {t.manual || 'MANUAL'}
                            </button>
                            <button
                                onClick={() => setActiveTab('virtual')}
                                className={`px-4 py-1.5 rounded-lg text-[10px] font-black flex items-center gap-2 transition-all ${activeTab === 'virtual' ? (isDark ? 'bg-slate-800 text-emerald-400' : 'bg-gray-100 text-emerald-600') : 'text-gray-400'}`}
                            >
                                <Cpu className="w-3 h-3" />
                                {t.virtualTrade || 'AI VIRTUAL'}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Exchange Rate Info */}
                <div className="flex justify-end text-[10px] font-bold opacity-40 gap-4">
                    <span>LIVE RATE: 1 USD = {exchangeRate.toFixed(2)} KRW (via Int'l Markets)</span>
                </div>

                {/* Dashboard Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className={`p-6 rounded-3xl shadow-xl border ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                        <div className="flex items-center gap-3 mb-2 opacity-50">
                            <Wallet className="w-4 h-4" />
                            <span className="text-[10px] font-black uppercase tracking-widest">Total Asset</span>
                        </div>
                        <p className="text-2xl font-black">
                            <span className="text-sm mr-1 opacity-50">{getSymbol()}</span>
                            {formatNumber(displayCurrency === 'KRW' ? totalValue : totalValue / exchangeRate, displayCurrency === 'USD' ? 2 : 0)}
                        </p>
                    </div>
                    <div className={`p-6 rounded-3xl shadow-xl border ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                        <div className="flex items-center gap-3 mb-2 opacity-50">
                            <DollarSign className="w-4 h-4" />
                            <span className="text-[10px] font-black uppercase tracking-widest">Available Cash</span>
                        </div>
                        <p className="text-2xl font-black text-blue-500">
                            <span className="text-sm mr-1 opacity-50">{getSymbol()}</span>
                            {formatNumber(displayCurrency === 'KRW' ? (virtualAccount?.balance || 0) : (virtualAccount?.balance || 0) / exchangeRate, displayCurrency === 'USD' ? 2 : 0)}
                        </p>
                    </div>
                    <div className={`p-6 rounded-3xl shadow-xl border ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                        <div className="flex items-center gap-3 mb-2 opacity-50">
                            <TrendingUp className="w-4 h-4" />
                            <span className="text-[10px] font-black uppercase tracking-widest">Profit/Loss</span>
                        </div>
                        <p className={`text-2xl font-black ${currentProfit >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                            <span className="text-sm mr-1 opacity-50">{getSymbol()}</span>
                            {currentProfit > 0 ? '+' : ''}{formatNumber(displayCurrency === 'KRW' ? currentProfit : currentProfit / exchangeRate, displayCurrency === 'USD' ? 2 : 0)}
                        </p>
                    </div>
                    <div className={`p-6 rounded-3xl shadow-xl border ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                        <div className="flex items-center gap-3 mb-2 opacity-50">
                            <Target className="w-4 h-4" />
                            <span className="text-[10px] font-black uppercase tracking-widest">ROI %</span>
                        </div>
                        <p className={`text-2xl font-black ${currentProfitRate >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                            {currentProfitRate > 0 ? '+' : ''}{currentProfitRate.toFixed(2)}%
                        </p>
                    </div>
                </div>

                {activeTab === 'virtual' && (
                    <div className={`p-8 rounded-[2.5rem] shadow-xl border ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                        <div className="flex items-center justify-between mb-8">
                            <h3 className="text-xl font-black flex items-center gap-3">
                                <Activity className="w-6 h-6 text-emerald-500" />
                                AI Active Positions
                            </h3>
                            <button onClick={fetchData} className="p-2 hover:bg-gray-100 rounded-xl transition-all">
                                <RefreshCcw className={`w-5 h-5 ${virtualLoading ? 'animate-spin' : ''}`} />
                            </button>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {virtualPositions.map((p, idx) => {
                                const symbol = p.is_usd ? '$' : '₩';
                                return (
                                    <div key={idx} className={`p-6 rounded-3xl border transition-all hover:scale-[1.02] ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-gray-50 border-gray-200 shadow-sm'}`}>
                                        <div className="flex justify-between items-start mb-6">
                                            <div>
                                                <h4 className="text-xl font-black">{p.ticker}</h4>
                                                <p className="text-[9px] font-black text-blue-500 uppercase tracking-widest">{p.quantity} SHARES</p>
                                            </div>
                                            <div className="text-right">
                                                <span className={`px-2 py-1 rounded-lg text-[10px] font-black ${p.profit_rate >= 0 ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>
                                                    {p.profit_rate >= 0 ? '+' : ''}{p.profit_rate.toFixed(2)}%
                                                </span>
                                            </div>
                                        </div>

                                        <div className="space-y-3">
                                            <div className="flex justify-between items-center">
                                                <span className="text-[10px] font-bold opacity-40 uppercase">Avg Cost</span>
                                                <span className="text-xs font-black">{symbol}{formatNumber(p.avg_price, p.is_usd ? 2 : 0)}</span>
                                            </div>
                                            <div className="flex justify-between items-center">
                                                <span className="text-[10px] font-bold opacity-40 uppercase">Current</span>
                                                <span className="text-xs font-black">{symbol}{formatNumber(p.current_price, p.is_usd ? 2 : 0)}</span>
                                            </div>
                                            <div className="pt-3 border-t border-dashed border-gray-700/50 flex justify-between items-end">
                                                <div>
                                                    <p className="text-[8px] font-black opacity-30 uppercase mb-1">Position Value</p>
                                                    <p className="text-lg font-black text-blue-500 leading-none">
                                                        {getSymbol()} {formatNumber(displayCurrency === 'KRW' ? p.total_value_krw : p.total_value_native, displayCurrency === 'USD' ? 2 : 0)}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PortfolioPage;
