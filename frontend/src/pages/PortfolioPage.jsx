import React, { useState, useEffect, useRef } from 'react';
import { PieChart, Plus, Trash2, ArrowUpRight, TrendingUp, ShieldAlert, BarChart, DollarSign, TrendingDown, Wallet, Target, Activity, Cpu, History, RefreshCcw } from 'lucide-react';
import { useTranslation } from '../utils/translations';
import api from '../utils/api';

const PortfolioPage = ({ settings }) => {
    const t = useTranslation(settings);
    const [activeTab, setActiveTab] = useState('manual');
    const [displayCurrency, setDisplayCurrency] = useState('KRW');

    const [holdings, setHoldings] = useState([
        { ticker: 'AAPL', shares: 10, avg_price: 150 },
        { ticker: 'TSLA', shares: 5, avg_price: 200 }
    ]);
    const [newHolding, setNewHolding] = useState({ ticker: '', shares: '', avg_price: '' });
    const [account, setAccount] = useState(null);
    const [positions, setPositions] = useState([]);
    const [exchangeRate, setExchangeRate] = useState(1350);
    const [loading, setLoading] = useState(false);

    const isDark = settings?.darkMode;

    const fetchData = async () => {
        setLoading(true);
        try {
            const [accRes, posRes, rateRes] = await Promise.all([
                api.get('/api/virtual/account'),
                api.get('/api/virtual/positions'),
                api.get('/api/exchange-rate')
            ]);
            setAccount(accRes.data);
            setPositions(posRes.data.positions || []);
            setExchangeRate(rateRes.data.rate);
        } catch (err) {
            console.error("Data fetch error:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (activeTab === 'virtual') {
            fetchData();
        }
    }, [activeTab]);

    const formatNumber = (num, decimals = 0) => {
        if (!num && num !== 0) return '0';
        return num.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
    };

    const getSymbol = () => displayCurrency === 'KRW' ? '₩' : '$';

    const totalValue = activeTab === 'manual'
        ? 0 // 수동 계산 로직 생략
        : (positions.reduce((acc, p) => acc + p.total_value_krw, 0) + (account?.balance || 0));

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
                        <div className={`flex p-1 rounded-xl border ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-200'}`}>
                            <button onClick={() => setDisplayCurrency('KRW')} className={`px-4 py-1.5 rounded-lg text-[10px] font-black transition-all ${displayCurrency === 'KRW' ? 'bg-blue-600 text-white' : 'text-gray-400'}`}>KRW (₩)</button>
                            <button onClick={() => setDisplayCurrency('USD')} className={`px-4 py-1.5 rounded-lg text-[10px] font-black transition-all ${displayCurrency === 'USD' ? 'bg-blue-600 text-white' : 'text-gray-400'}`}>USD ($)</button>
                        </div>
                        <div className={`flex p-1 rounded-xl border ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-200'}`}>
                            <button onClick={() => setActiveTab('manual')} className={`px-4 py-1.5 rounded-lg text-[10px] font-black transition-all ${activeTab === 'manual' ? 'bg-slate-800 text-blue-400' : 'text-gray-400'}`}>MANUAL</button>
                            <button onClick={() => setActiveTab('virtual')} className={`px-4 py-1.5 rounded-lg text-[10px] font-black flex items-center gap-2 transition-all ${activeTab === 'virtual' ? 'bg-slate-800 text-emerald-400' : 'text-gray-400'}`}><Cpu className="w-3 h-3" />AI VIRTUAL</button>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className={`p-6 rounded-3xl shadow-xl border ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                        <div className="flex items-center gap-3 mb-2 opacity-50"><Wallet className="w-4 h-4" /><span className="text-[10px] font-black uppercase tracking-widest">Total Asset</span></div>
                        <p className="text-2xl font-black"><span className="text-sm mr-1 opacity-50">{getSymbol()}</span>{formatNumber(displayCurrency === 'KRW' ? totalValue : totalValue / exchangeRate, displayCurrency === 'USD' ? 2 : 0)}</p>
                    </div>
                    {/* 기타 메트릭 생략 또는 간소화 */}
                </div>

                {activeTab === 'virtual' && (
                    <div className={`p-8 rounded-[2.5rem] shadow-xl border ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                        <div className="flex items-center justify-between mb-8">
                            <h3 className="text-xl font-black flex items-center gap-3"><Activity className="w-6 h-6 text-emerald-500" />AI Active Positions</h3>
                            <button onClick={fetchData} className="p-2 hover:bg-gray-100 rounded-xl transition-all"><RefreshCcw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} /></button>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {positions.map((p, idx) => {
                                const symbol = p.is_usd ? '$' : '₩';
                                return (
                                    <div key={idx} className={`p-6 rounded-3xl border transition-all hover:scale-[1.02] ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-gray-50 border-gray-200 shadow-sm'}`}>
                                        <div className="flex justify-between items-start mb-6">
                                            <div><h4 className="text-xl font-black">{p.ticker}</h4><p className="text-[9px] font-black text-blue-500 uppercase tracking-widest">{p.quantity} SHARES</p></div>
                                            <div className="text-right"><span className={`px-2 py-1 rounded-lg text-[10px] font-black ${p.profit_rate >= 0 ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>{p.profit_rate >= 0 ? '+' : ''}{p.profit_rate.toFixed(2)}%</span></div>
                                        </div>
                                        {/* 상세 정보 */}
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
