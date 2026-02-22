/* eslint-disable unused-imports/no-unused-imports, unused-imports/no-unused-vars, no-unused-vars */
import { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
    Rocket,
    Briefcase,
    Scale,
    TrendingUp,
    ArrowUpRight,
    ArrowDownRight,
    Filter,
    Activity
} from 'lucide-react';
import { useTranslation } from '../utils/translations';
import { useScreener } from '../features/screener/hooks/useScreener';

// Moved outside to prevent recreation & leverage hardware acceleration (willChange)
const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1, delayChildren: 0.1 }, willChange: "transform, opacity" }
};

const itemVariants = {
    hidden: { opacity: 0, y: 30, scale: 0.98 },
    visible: { opacity: 1, y: 0, scale: 1, transition: { type: 'spring', stiffness: 300, damping: 24 }, willChange: "transform, opacity" }
};

const ScreenerPage = ({ settings }) => {
    const t = useTranslation(settings);
    const {
        style, setStyle,
        market, setMarket,
        recommendations,
        loading,
        topGainers, topLosers,
        handleAnalyze
    } = useScreener(settings.tradingStyle || 'balanced', 'US');

    const memoizedStyles = useMemo(() => [
        { id: 'aggressive', label: t.scr_aggressive, icon: Rocket, color: 'text-yellow-400', bg: 'bg-yellow-400/20', border: 'border-yellow-400/40' },
        { id: 'balanced', label: t.scr_balanced, icon: Scale, color: 'text-yellow-400 opacity-90', bg: 'bg-yellow-400/10', border: 'border-yellow-400/20' },
        { id: 'conservative', label: t.scr_conservative, icon: Briefcase, color: 'text-yellow-400 opacity-70', bg: 'bg-yellow-400/5', border: 'border-yellow-400/10' },
    ], [t.scr_aggressive, t.scr_balanced, t.scr_conservative]);

    const memoizedMarkets = useMemo(() => [
        { id: 'US', label: t.scr_market_us || 'US' },
        { id: 'KR', label: t.scr_market_kr || 'KR' }
    ], [t.scr_market_us, t.scr_market_kr]);

    return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="min-h-screen py-10 transition-all duration-300 bg-[#09090b] text-foreground">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
                        <h1 className="text-3xl font-black tracking-tighter flex items-center gap-3 text-zinc-100 uppercase">
                            <div className="bg-yellow-400 p-2 rounded-xl text-black shadow-lg shadow-yellow-400/20">
                                <TrendingUp className="w-7 h-7" />
                            </div>
                            {t.scr_title}
                        </h1>
                        <p className="text-sm font-medium mt-2 opacity-80 text-zinc-500 uppercase tracking-widest font-mono">
                            {t.scr_desc}
                        </p>
                    </motion.div>

                    <div className="p-1.5 rounded-2xl border flex gap-1.5 bg-white/5 border-white/10">
                        {memoizedMarkets.map(m => (
                            <button
                                key={m.id}
                                onClick={() => setMarket(m.id)}
                                className={`px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${market === m.id ? 'bg-yellow-400 text-black shadow-lg shadow-yellow-400/20' : 'text-zinc-500 hover:text-zinc-300'}`}
                            >
                                {m.label}
                            </button>
                        ))}
                    </div>
                </div>

                <motion.div
                    initial="hidden" animate="visible"
                    variants={containerVariants}
                    className="grid grid-cols-1 md:grid-cols-2 gap-8"
                >
                    <motion.div variants={itemVariants} className="shadow-xl rounded-3xl border overflow-hidden bg-white/5 backdrop-blur-md border-white/10 hover:shadow-2xl hover:scale-[1.02] transition-all">
                        <div className="px-6 py-4 border-b flex justify-between items-center bg-emerald-500/10 border-white/5">
                            <h3 className="text-[10px] font-black uppercase tracking-widest flex items-center gap-2 text-emerald-500 font-mono">
                                <ArrowUpRight className="w-4 h-4" /> {t.scr_gainers} ({market})
                            </h3>
                        </div>
                        <ul className="divide-y divide-white/5">
                            {topGainers.map((stock, idx) => (
                                <li key={idx} onClick={() => handleAnalyze(stock.ticker)} className="px-8 py-5 flex justify-between items-center cursor-pointer transition-colors hover:bg-white/5">
                                    <span className="font-black text-sm text-zinc-100 font-mono">{stock.ticker}</span>
                                    <span className="font-black text-emerald-500 text-sm font-mono">+{stock.change}%</span>
                                </li>
                            ))}
                            {topGainers.length === 0 && <li className="px-8 py-12 text-center opacity-30 text-xs font-bold italic text-zinc-500 font-mono uppercase tracking-widest">Awaiting_Market_Pulse...</li>}
                        </ul>
                    </motion.div>

                    <motion.div variants={itemVariants} className="shadow-xl rounded-3xl border overflow-hidden bg-white/5 backdrop-blur-md border-white/10 hover:shadow-2xl hover:scale-[1.02] transition-all">
                        <div className="px-6 py-4 border-b flex justify-between items-center bg-rose-500/10 border-white/5">
                            <h3 className="text-[10px] font-black uppercase tracking-widest flex items-center gap-2 text-rose-500 font-mono">
                                <ArrowDownRight className="w-4 h-4" /> {t.scr_losers} ({market})
                            </h3>
                        </div>
                        <ul className="divide-y divide-white/5">
                            {topLosers.map((stock, idx) => (
                                <li key={idx} onClick={() => handleAnalyze(stock.ticker)} className="px-8 py-5 flex justify-between items-center cursor-pointer transition-colors hover:bg-white/5">
                                    <span className="font-black text-sm text-zinc-100 font-mono">{stock.ticker}</span>
                                    <span className="font-black text-rose-500 text-sm font-mono">{stock.change}%</span>
                                </li>
                            ))}
                            {topLosers.length === 0 && <li className="px-8 py-12 text-center opacity-30 text-xs font-bold italic text-zinc-500 font-mono uppercase tracking-widest">Awaiting_Market_Pulse...</li>}
                        </ul>
                    </motion.div>
                </motion.div>

                <motion.div initial="hidden" animate="visible" variants={containerVariants} className="space-y-6">
                    <motion.h2 variants={itemVariants} className="text-xl font-black flex items-center gap-3 text-zinc-100 uppercase tracking-tighter">
                        <Filter className="w-5 h-5 text-yellow-400" />
                        {t.scr_strategies}
                    </motion.h2>
                    <motion.div variants={containerVariants} className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                        {memoizedStyles.map((s) => {
                            const Icon = s.icon;
                            const isSelected = style === s.id;
                            return (
                                <motion.button variants={itemVariants} key={s.id} onClick={() => setStyle(s.id)} className={`flex items-center gap-5 p-6 rounded-3xl border transition-all transform hover:scale-[1.02] active:scale-[0.98] ${isSelected ? 'border-yellow-400 bg-yellow-400/10 shadow-lg shadow-yellow-400/20' : 'border-white/10 bg-white/5 backdrop-blur-md hover:border-yellow-400/50 hover:bg-white/10'}`}>
                                    <div className={`p-4 rounded-xl shadow-inner ${s.bg} ${s.color}`}>
                                        <Icon className="w-7 h-7" />
                                    </div>
                                    <div className="text-left">
                                        <p className={`font-black text-sm uppercase tracking-tight ${isSelected ? 'text-yellow-400' : 'text-zinc-100'}`}>{s.label}</p>
                                        <p className="text-[10px] font-bold opacity-40 uppercase tracking-widest mt-1 text-zinc-500 font-mono">High-Alpha Vectors</p>
                                    </div>
                                </motion.button>
                            );
                        })}
                    </motion.div>
                </motion.div>

                <motion.div initial="hidden" animate="visible" variants={itemVariants} className="shadow-2xl rounded-[2.5rem] border overflow-hidden bg-white/5 backdrop-blur-md border-white/10">
                    <div className="px-10 py-6 border-b flex items-center justify-between border-white/5">
                        <h3 className="text-lg font-black italic tracking-tighter text-zinc-100 uppercase font-mono">Neural_Pick_Stream ({market})</h3>
                        <div className="h-2 w-2 rounded-full bg-yellow-400 animate-pulse"></div>
                    </div>
                    <div className="overflow-x-auto custom-scrollbar">
                        <table className="min-w-full divide-y divide-transparent">
                            <thead>
                                <tr className="bg-white/5 text-zinc-500">
                                    <th scope="col" className="px-10 py-4 text-left text-[10px] font-black uppercase tracking-widest font-mono">Ticker_Hub</th>
                                    <th scope="col" className="px-10 py-4 text-left text-[10px] font-black uppercase tracking-widest font-mono">AI_Confidence</th>
                                    <th scope="col" className="px-10 py-4 text-left text-[10px] font-black uppercase tracking-widest font-mono">Heuristic_Intent</th>
                                    <th scope="col" className="px-10 py-4 text-center text-[10px] font-black uppercase tracking-widest font-mono">Execution</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {recommendations.length > 0 ? (
                                    recommendations.map((rec, idx) => (
                                        <tr key={idx} className="transition-all duration-200 group hover:bg-white/5">
                                            <td className="px-10 py-6 whitespace-nowrap">
                                                <div className="flex items-center gap-4">
                                                    <div className="h-12 w-12 rounded-2xl flex items-center justify-center font-black text-sm shadow-sm transition-transform group-hover:scale-110 bg-white/5 text-zinc-100 border border-white/10">
                                                        {rec.ticker.substring(0, 2)}
                                                    </div>
                                                    <div className="text-base font-black text-yellow-400 font-mono tracking-widest">{rec.ticker}</div>
                                                </div>
                                            </td>
                                            <td className="px-10 py-6 whitespace-nowrap">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-16 h-1.5 bg-white/5 rounded-full overflow-hidden flex">
                                                        <div className={`h-full ${rec.score >= 80 ? 'bg-yellow-400' : 'bg-yellow-400/40'}`} style={{ width: `${rec.score}%` }}></div>
                                                    </div>
                                                    <span className={`text-[11px] font-black px-3 py-1 rounded-full font-mono ${rec.score >= 80 ? 'bg-yellow-400/10 text-yellow-400' : 'bg-yellow-400/5 text-yellow-400/70'}`}>
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

                                                                let color = 'bg-white/5 text-zinc-500';
                                                                if (sig.signal === 'BUY' || sig.signal === 'STRONG_BUY') color = 'bg-emerald-500/10 text-emerald-500';
                                                                else if (sig.signal === 'SELL' || sig.signal === 'STRONG_SELL') color = 'bg-rose-500/10 text-rose-500';

                                                                const labelMap = { short: '단기', medium: '중기', long: '장기' };

                                                                return (
                                                                    <span key={tf} className={`px-2 py-1 rounded text-[10px] font-bold font-mono ${color}`}>
                                                                        {labelMap[tf]}_{sig.signal}
                                                                    </span>
                                                                );
                                                            })}
                                                        </div>
                                                    )}
                                                    <div className="text-sm font-medium leading-relaxed opacity-80 whitespace-pre-wrap text-zinc-100">
                                                        {rec.reason.split('\n').filter(line => !line.includes('시계열 분석:')).join('\n')}
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-10 py-6 whitespace-nowrap text-center">
                                                <button onClick={() => handleAnalyze(rec.ticker)} className="px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all bg-yellow-400 text-black hover:bg-yellow-400/80 shadow-lg shadow-yellow-400/20">
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
                                                        <Activity className="w-16 h-16 text-yellow-400 animate-spin" />
                                                        <p className="text-sm font-black uppercase tracking-[0.2em] text-yellow-400 font-mono">Synchronizing_Neural_Fabric...</p>
                                                        <p className="text-[10px] text-zinc-500 font-bold uppercase tracking-widest font-mono">Fetching Multi-Timeframe Vectors & Market Pulsar</p>
                                                    </>
                                                ) : (
                                                    <>
                                                        <Rocket className="w-16 h-16 text-zinc-500" />
                                                        <p className="text-sm font-black uppercase tracking-[0.2em] text-zinc-100 font-mono">No_Vectors_Identified</p>
                                                    </>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </motion.div>
            </div>
        </motion.div>
    );
};

export default ScreenerPage;
