import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Search,
    ArrowUpRight,
    ArrowDownRight,
    Zap,
    TrendingUp,
    BarChart2,
    Globe,
    ChevronRight,
    Activity,
    Filter,
    Rocket,
    Briefcase,
    Scale
} from 'lucide-react';
import { useTranslation } from '../utils/translations';
import api from '../utils/api';

const ScreenerPage = ({ settings }) => {
    const navigate = useNavigate();
    const [style, setStyle] = useState('balanced');
    const [market, setMarket] = useState('US');
    const [recommendations, setRecommendations] = useState([]);
    const [topMovers, setTopMovers] = useState({ gainers: [], losers: [] });
    const [loading, setLoading] = useState(false);

    const isDark = settings?.darkMode;
    const t = useTranslation(settings);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const backendStyle = settings.tradingStyle || 'balanced';
                const [recRes, topRes] = await Promise.all([
                    api.get(`/api/screener/recommendations?style=${backendStyle}&market=${market}`),
                    api.get(`/api/screener/top-movers?market=${market}`)
                ]);
                setRecommendations(recRes.data.recommendations || []);
                setTopMovers(topRes.data || { gainers: [], losers: [] });
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [market, settings.tradingStyle, style]);

    const styles = [
        { id: 'aggressive', label: t.scr_aggressive, icon: Rocket, color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/20' },
        { id: 'balanced', label: t.scr_balanced, icon: Scale, color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20' },
        { id: 'conservative', label: t.scr_conservative, icon: Briefcase, color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' },
    ];

    const markets = [
        { id: 'US', label: t.scr_market_us || 'US' },
        { id: 'KR', label: t.scr_market_kr || 'KR' }
    ];

    const handleAnalyze = (ticker) => {
        navigate(`/analysis/${encodeURIComponent(ticker)}`);
    };

    return (
        <div className={`min-h-screen py-10 transition-colors duration-300 ${isDark ? 'bg-slate-950 text-slate-100' : 'bg-gray-50 text-gray-900'}`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-3xl font-black flex items-center gap-3">
                            <div className="bg-blue-600 p-2 rounded-xl text-white shadow-lg shadow-blue-500/20">
                                <TrendingUp className="w-7 h-7" />
                            </div>
                            {t.scr_title}
                        </h1>
                        <p className={`text-sm font-medium mt-2 opacity-50 ${isDark ? 'text-slate-400' : 'text-gray-500'}`}>
                            {t.scr_desc}
                        </p>
                    </div>

                    <div className={`p-1 rounded-2xl border flex gap-1 ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-200'}`}>
                        {markets.map(m => (
                            <button
                                key={m.id}
                                onClick={() => setMarket(m.id)}
                                className={`px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${market === m.id ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'text-gray-400 hover:text-gray-600'}`}
                            >
                                {m.label}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className={`shadow-xl rounded-3xl border overflow-hidden ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                        <div className={`px-6 py-4 border-b flex justify-between items-center ${isDark ? 'bg-emerald-500/5 border-slate-800' : 'bg-emerald-50 border-gray-100'}`}>
                            <h3 className={`text-[10px] font-black uppercase tracking-widest flex items-center gap-2 ${isDark ? 'text-emerald-400' : 'text-emerald-800'}`}>
                                <ArrowUpRight className="w-4 h-4" /> {t.scr_gainers} ({market})
                            </h3>
                        </div>
                        <ul className={`divide-y ${isDark ? 'divide-slate-800' : 'divide-gray-50'}`}>
                            {topMovers.gainers?.slice(0, 5).map((stock, idx) => (
                                <li key={idx} onClick={() => handleAnalyze(stock.ticker)} className={`px-8 py-4 flex justify-between items-center cursor-pointer transition-colors ${isDark ? 'hover:bg-slate-800/50' : 'hover:bg-gray-50'}`}>
                                    <span className="font-black text-sm">{stock.ticker}</span>
                                    <span className="font-black text-emerald-500 text-sm">+{stock.change}%</span>
                                </li>
                            ))}
                            {(!topMovers.gainers || topMovers.gainers.length === 0) && <li className="px-8 py-10 text-center opacity-30 text-xs font-bold italic">Awaiting Market Pulse...</li>}
                        </ul>
                    </div>

                    <div className={`shadow-xl rounded-3xl border overflow-hidden ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                        <div className={`px-6 py-4 border-b flex justify-between items-center ${isDark ? 'bg-rose-500/5 border-slate-800' : 'bg-rose-50 border-gray-100'}`}>
                            <h3 className={`text-[10px] font-black uppercase tracking-widest flex items-center gap-2 ${isDark ? 'text-rose-400' : 'text-rose-800'}`}>
                                <ArrowDownRight className="w-4 h-4" /> {t.scr_losers} ({market})
                            </h3>
                        </div>
                        <ul className={`divide-y ${isDark ? 'divide-slate-800' : 'divide-gray-50'}`}>
                            {topMovers.losers?.slice(0, 5).map((stock, idx) => (
                                <li key={idx} onClick={() => handleAnalyze(stock.ticker)} className={`px-8 py-4 flex justify-between items-center cursor-pointer transition-colors ${isDark ? 'hover:bg-slate-800/50' : 'hover:bg-gray-50'}`}>
                                    <span className="font-black text-sm">{stock.ticker}</span>
                                    <span className="font-black text-rose-500 text-sm">{stock.change}%</span>
                                </li>
                            ))}
                            {(!topMovers.losers || topMovers.losers.length === 0) && <li className="px-8 py-10 text-center opacity-30 text-xs font-bold italic">Awaiting Market Pulse...</li>}
                        </ul>
                    </div>
                </div>

                <div className="space-y-6">
                    <h2 className="text-xl font-black flex items-center gap-3">
                        <Filter className="w-5 h-5 text-blue-500" />
                        {t.scr_strategies}
                    </h2>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                        {styles.map((s) => {
                            const Icon = s.icon;
                            const isSelected = style === s.id;
                            return (
                                <button key={s.id} onClick={() => setStyle(s.id)} className={`flex items-center gap-5 p-6 rounded-3xl border-2 transition-all transform hover:translate-y-[-4px] active:scale-[0.98] ${isSelected ? (isDark ? 'border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-900/40' : 'border-blue-600 bg-blue-50 shadow-xl shadow-blue-500/10 scale-[1.02]') : (isDark ? 'border-slate-800 bg-slate-900/50 hover:border-slate-700' : 'border-gray-100 bg-white hover:border-gray-200 hover:shadow-lg')}`}>
                                    <div className={`p-4 rounded-xl shadow-inner ${s.bg} ${s.color}`}>
                                        <Icon className="w-7 h-7" />
                                    </div>
                                    <div className="text-left">
                                        <p className={`font-black text-sm uppercase tracking-tight ${isSelected ? (isDark ? 'text-blue-400' : 'text-blue-900') : (isDark ? 'text-slate-300' : 'text-gray-900')}`}>{s.label}</p>
                                        <p className="text-[10px] font-bold opacity-40 uppercase tracking-widest mt-1">High-Alpha Vectors</p>
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                </div>

                <div className={`shadow-2xl rounded-[2.5rem] border overflow-hidden ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                    <div className={`px-10 py-6 border-b flex items-center justify-between ${isDark ? 'border-slate-800' : 'border-gray-50'}`}>
                        <h3 className="text-lg font-black italic">Neural Pick Stream ({market})</h3>
                        <div className={`h-2 w-2 rounded-full bg-blue-500 animate-ping`}></div>
                    </div>
                    <div className="overflow-x-auto custom-scrollbar">
                        <table className="min-w-full divide-y divide-transparent">
                            <thead>
                                <tr className={isDark ? 'bg-slate-950/30 text-slate-500' : 'bg-gray-50/50 text-gray-400'}>
                                    <th scope="col" className="px-10 py-4 text-left text-[10px] font-black uppercase tracking-widest">Ticker Hub</th>
                                    <th scope="col" className="px-10 py-4 text-left text-[10px] font-black uppercase tracking-widest">AI Confidence</th>
                                    <th scope="col" className="px-10 py-4 text-left text-[10px] font-black uppercase tracking-widest">Heuristic Intent</th>
                                    <th scope="col" className="px-10 py-4 text-center text-[10px] font-black uppercase tracking-widest">Execution</th>
                                </tr>
                            </thead>
                            <tbody className={`divide-y ${isDark ? 'divide-slate-800/50' : 'divide-gray-50'}`}>
                                {recommendations.length > 0 ? (
                                    recommendations.map((rec, idx) => (
                                        <tr key={idx} className={`transition-all duration-200 group ${isDark ? 'hover:bg-blue-500/5' : 'hover:bg-blue-50/30'}`}>
                                            <td className="px-10 py-6 whitespace-nowrap">
                                                <div className="flex items-center gap-4">
                                                    <div className={`h-12 w-12 rounded-2xl flex items-center justify-center font-black text-sm shadow-sm transition-transform group-hover:scale-110 ${isDark ? 'bg-slate-800 text-blue-400' : 'bg-gray-100 text-gray-600'}`}>
                                                        {rec.ticker.substring(0, 2)}
                                                    </div>
                                                    <div className="text-base font-black text-blue-500">{rec.ticker}</div>
                                                </div>
                                            </td>
                                            <td className="px-10 py-6 whitespace-nowrap">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden flex">
                                                        <div className={`h-full ${rec.score >= 80 ? 'bg-blue-500' : 'bg-yellow-500'}`} style={{ width: `${rec.score}%` }}></div>
                                                    </div>
                                                    <span className={`text-[11px] font-black px-3 py-1 rounded-full ${rec.score >= 80 ? 'bg-blue-500/10 text-blue-500' : 'bg-yellow-500/10 text-yellow-500'}`}>
                                                        {rec.score}%
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="px-10 py-6 whitespace-normal">
                                                <div className="flex flex-col gap-2">
                                                    {/* Multi-Timeframe Signals */}
                                                    {rec.signals && (
                                                        <div className="flex gap-2 mb-1">
                                                            {['short', 'medium', 'long'].map((tf) => {
                                                                const sig = rec.signals[tf];
                                                                if (!sig) return null;

                                                                let color = 'bg-gray-100 text-gray-600';
                                                                if (sig.signal === 'BUY' || sig.signal === 'STRONG_BUY') color = 'bg-red-100 text-red-600';
                                                                else if (sig.signal === 'SELL' || sig.signal === 'STRONG_SELL') color = 'bg-blue-100 text-blue-600';

                                                                const labelMap = { short: '단기', medium: '중기', long: '장기' };

                                                                return (
                                                                    <span key={tf} className={`px-2 py-1 rounded text-[10px] font-bold ${color}`}>
                                                                        {labelMap[tf]} {sig.signal}
                                                                    </span>
                                                                );
                                                            })}
                                                        </div>
                                                    )}
                                                    <div className={`text-sm font-medium leading-relaxed opacity-80 whitespace-pre-wrap`}>
                                                        {rec.reason.split('\n').filter(line => !line.includes('시계열 분석:')).join('\n')}
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-10 py-6 whitespace-nowrap text-center">
                                                <button onClick={() => handleAnalyze(rec.ticker)} className={`px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${isDark ? 'bg-blue-600 text-white hover:bg-blue-500 shadow-lg shadow-blue-500/20' : 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg shadow-blue-200'}`}>
                                                    {t.scr_analyze}
                                                </button>
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan="4" className="px-10 py-24 text-center">
                                            <div className="flex flex-col items-center gap-4 opacity-50">
                                                {loading ? (
                                                    <>
                                                        <Activity className="w-16 h-16 text-blue-500 animate-spin" />
                                                        <p className="text-sm font-black uppercase tracking-[0.2em] text-blue-400">Synchronizing Neural Fabric...</p>
                                                        <p className="text-[10px] text-slate-500 font-bold">Fetching Multi-Timeframe Vectors & Market Pulsar</p>
                                                    </>
                                                ) : (
                                                    <>
                                                        <Rocket className="w-16 h-16 text-slate-700" />
                                                        <p className="text-sm font-black uppercase tracking-[0.2em]">No Vectors Identified</p>
                                                    </>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ScreenerPage;
