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
    const [error, setError] = useState(null);

    const fetchData = async () => {
        setLoading(true);
        setError(null);
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
            setError("Failed to load portfolio data. Please try again.");
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

    // 로딩 중 표시
    if (loading && !account && activeTab === 'virtual') {
        return (
            <div className="min-h-screen py-20 flex flex-col items-center justify-center bg-background text-foreground animate-pulse">
                <Activity className="w-12 h-12 text-primary mb-4" />
                <p className="text-lg font-bold">Synchronizing Assets...</p>
            </div>
        );
    }

    return (
        <div className="min-h-screen py-10 transition-colors duration-300 bg-background text-foreground">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
                <div className="flex items-center justify-between">
                    <h1 className="text-3xl font-black flex items-center gap-3">
                        <div className="bg-primary p-2 rounded-xl text-primary-foreground shadow-lg">
                            <PieChart className="w-7 h-7" />
                        </div>
                        {t.portfolio}
                    </h1>

                    <div className="flex items-center gap-4">
                        <div className="flex p-1 rounded-xl border bg-card border-border">
                            <button onClick={() => setDisplayCurrency('KRW')} className={`px-4 py-1.5 rounded-lg text-[10px] font-black transition-all ${displayCurrency === 'KRW' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'}`}>KRW (₩)</button>
                            <button onClick={() => setDisplayCurrency('USD')} className={`px-4 py-1.5 rounded-lg text-[10px] font-black transition-all ${displayCurrency === 'USD' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'}`}>USD ($)</button>
                        </div>
                        <div className="flex p-1 rounded-xl border bg-card border-border">
                            <button onClick={() => setActiveTab('manual')} className={`px-4 py-1.5 rounded-lg text-[10px] font-black transition-all ${activeTab === 'manual' ? 'bg-secondary text-secondary-foreground' : 'text-muted-foreground'}`}>MANUAL</button>
                            <button onClick={() => setActiveTab('virtual')} className={`px-4 py-1.5 rounded-lg text-[10px] font-black flex items-center gap-2 transition-all ${activeTab === 'virtual' ? 'bg-secondary text-emerald-500' : 'text-muted-foreground'}`}><Cpu className="w-3 h-3" />AI VIRTUAL</button>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="p-6 rounded-3xl shadow-xl border bg-card border-border">
                        <div className="flex items-center gap-3 mb-2 opacity-50"><Wallet className="w-4 h-4" /><span className="text-[10px] font-black uppercase tracking-widest">Total Asset</span></div>
                        <p className="text-2xl font-black"><span className="text-sm mr-1 opacity-50">{getSymbol()}</span>{formatNumber(displayCurrency === 'KRW' ? totalValue : totalValue / exchangeRate, displayCurrency === 'USD' ? 2 : 0)}</p>
                    </div>
                    {/* 기타 메트릭 생략 또는 간소화 */}
                </div>

                {error && activeTab === 'virtual' && (
                    <div className="p-8 rounded-3xl border border-destructive/50 bg-destructive/10 text-center">
                        <ShieldAlert className="w-10 h-10 text-destructive mx-auto mb-4" />
                        <h3 className="text-xl font-bold text-destructive mb-2">Connection Error</h3>
                        <p className="text-muted-foreground mb-6">{error}</p>
                        <button onClick={fetchData} className="px-6 py-2 bg-destructive text-destructive-foreground rounded-lg font-bold hover:bg-destructive/90 transition-colors">
                            Retry Connection
                        </button>
                    </div>
                )}

                {activeTab === 'virtual' && !error && (
                    <div className="p-8 rounded-[2.5rem] shadow-xl border bg-card border-border">
                        <div className="flex items-center justify-between mb-8">
                            <h3 className="text-xl font-black flex items-center gap-3"><Activity className="w-6 h-6 text-emerald-500" />AI Active Positions</h3>
                            <button onClick={fetchData} className="p-2 hover:bg-muted rounded-xl transition-all"><RefreshCcw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} /></button>
                        </div>

                        {positions.length === 0 ? (
                            <div className="text-center py-20 text-muted-foreground">
                                <Wallet className="w-16 h-16 mx-auto mb-4 opacity-20" />
                                <p className="font-medium">No active positions found.</p>
                                <p className="text-sm opacity-70 mt-2">The AI auto-trader has not executed any trades yet.</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {positions.map((p, idx) => {
                                    return (
                                        <div key={idx} className="p-6 rounded-3xl border transition-all hover:scale-[1.02] bg-card border-border hover:shadow-lg hover:border-primary/30 group">
                                            <div className="flex justify-between items-start mb-6">
                                                <div><h4 className="text-xl font-black group-hover:text-primary transition-colors">{p.ticker}</h4><p className="text-[9px] font-black text-blue-500 uppercase tracking-widest">{p.quantity} SHARES</p></div>
                                                <div className="text-right"><span className={`px-2 py-1 rounded-lg text-[10px] font-black ${p.profit_rate >= 0 ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>{p.profit_rate >= 0 ? '+' : ''}{p.profit_rate.toFixed(2)}%</span></div>
                                            </div>
                                            {/* 상세 정보 */}
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default PortfolioPage;
