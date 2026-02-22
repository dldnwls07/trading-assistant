import { motion } from 'framer-motion';
import {
    Activity,
    PieChart,
    Cpu,
    Wallet,
    ShieldAlert,
    RefreshCcw,
    TrendingUp,
    TrendingDown,
    BarChart3
} from 'lucide-react';
import { useTranslation } from '../utils/translations';
import { usePortfolio } from '../features/portfolio/hooks/usePortfolio';

const PortfolioPage = ({ settings }) => {
    const t = useTranslation(settings);
    const {
        activeTab, setActiveTab,
        displayCurrency, setDisplayCurrency,
        account,
        positions,
        exchangeRate,
        loading,
        error,
        totalValue,
        fetchData,
        formatNumber,
        getSymbol
    } = usePortfolio();

    // 로딩 중 표시
    if (loading && !account && activeTab === 'virtual') {
        return (
            <div className="min-h-screen py-20 flex flex-col items-center justify-center bg-[#09090b] text-foreground animate-pulse">
                <Activity className="w-12 h-12 text-yellow-400 mb-4" />
                <p className="text-lg font-bold text-zinc-100 uppercase tracking-widest font-mono">SYNCHRONIZING_ASSETS...</p>
            </div>
        );
    }

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: { opacity: 1, transition: { staggerChildren: 0.1, delayChildren: 0.1 } }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 30, scale: 0.98 },
        visible: { opacity: 1, y: 0, scale: 1, transition: { type: 'spring', stiffness: 300, damping: 24 } }
    };

    return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="min-h-screen py-10 transition-all duration-300 bg-[#09090b] text-foreground">
            <motion.div initial="hidden" animate="visible" variants={containerVariants} className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
                <motion.div variants={itemVariants} className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <h1 className="text-3xl font-black tracking-tighter flex items-center gap-3 text-zinc-100 uppercase">
                        <div className="bg-yellow-400 p-2 rounded-xl text-black shadow-lg shadow-yellow-400/20">
                            <PieChart className="w-7 h-7" />
                        </div>
                        {t.portfolio}
                    </h1>

                    <div className="flex items-center gap-4">
                        <div className="flex p-1 rounded-xl border bg-white/5 border-white/10">
                            <button onClick={() => setDisplayCurrency('KRW')} className={`px-4 py-1.5 rounded-lg text-[10px] font-black transition-all ${displayCurrency === 'KRW' ? 'bg-yellow-400 text-black shadow-lg shadow-yellow-400/20' : 'text-zinc-500 hover:text-zinc-300'}`}>KRW (₩)</button>
                            <button onClick={() => setDisplayCurrency('USD')} className={`px-4 py-1.5 rounded-lg text-[10px] font-black transition-all ${displayCurrency === 'USD' ? 'bg-yellow-400 text-black shadow-lg shadow-yellow-400/20' : 'text-zinc-500 hover:text-zinc-300'}`}>USD ($)</button>
                        </div>
                        <div className="flex p-1 rounded-xl border bg-white/5 border-white/10">
                            <button onClick={() => setActiveTab('manual')} className={`px-4 py-1.5 rounded-lg text-[10px] font-black transition-all ${activeTab === 'manual' ? 'bg-white/10 text-yellow-400 border border-yellow-400/20' : 'text-zinc-500 hover:text-zinc-300'}`}>MANUAL</button>
                            <button onClick={() => setActiveTab('virtual')} className={`px-4 py-1.5 rounded-lg text-[10px] font-black flex items-center gap-2 transition-all ${activeTab === 'virtual' ? 'bg-yellow-400 text-black shadow-lg shadow-yellow-400/20' : 'text-zinc-500 hover:text-zinc-300'}`}><Cpu className="w-3 h-3" />AI VIRTUAL</button>
                        </div>
                    </div>
                </motion.div>

                <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="p-6 rounded-3xl shadow-xl border bg-white/5 backdrop-blur-md border-white/10 hover:scale-[1.02] transition-transform">
                        <div className="flex items-center gap-3 mb-2 text-zinc-500"><Wallet className="w-4 h-4" /><span className="text-[10px] font-black uppercase tracking-widest font-mono">Total_Asset_Value</span></div>
                        <p className="text-2xl font-black tracking-tight text-zinc-100 font-mono"><span className="text-sm mr-1 opacity-50">{getSymbol()}</span>{formatNumber(displayCurrency === 'KRW' ? totalValue : totalValue / exchangeRate, displayCurrency === 'USD' ? 2 : 0)}</p>
                    </div>
                    {activeTab === 'virtual' && account && (
                        <div className="p-6 rounded-3xl shadow-xl border bg-white/5 backdrop-blur-md border-white/10 hover:scale-[1.02] transition-transform">
                            <div className="flex items-center gap-3 mb-2 text-zinc-500"><BarChart3 className="w-4 h-4" /><span className="text-[10px] font-black uppercase tracking-widest font-mono">Available_Balance</span></div>
                            <p className="text-2xl font-black tracking-tight text-yellow-400 font-mono"><span className="text-sm mr-1 opacity-50">{getSymbol()}</span>{formatNumber(displayCurrency === 'KRW' ? account.balance : account.balance / exchangeRate, displayCurrency === 'USD' ? 2 : 0)}</p>
                        </div>
                    )}
                </motion.div>

                {error && activeTab === 'virtual' && (
                    <div className="p-8 rounded-3xl border border-rose-500/50 bg-rose-500/5 text-center">
                        <ShieldAlert className="w-10 h-10 text-rose-500 mx-auto mb-4" />
                        <h3 className="text-xl font-bold text-rose-500 mb-2 uppercase tracking-tighter">Connection Error</h3>
                        <p className="text-zinc-500 mb-6">{error}</p>
                        <button onClick={fetchData} className="px-6 py-2 bg-rose-500 text-white rounded-lg font-bold hover:bg-rose-600 transition-colors uppercase text-xs tracking-widest">
                            Retry Connection
                        </button>
                    </div>
                )}

                {activeTab === 'virtual' && !error && (
                    <motion.div variants={itemVariants} className="p-8 rounded-[2.5rem] shadow-xl border bg-white/5 backdrop-blur-md border-white/10">
                        <div className="flex items-center justify-between mb-8">
                            <h3 className="text-xl font-black flex items-center gap-3 text-zinc-100 uppercase tracking-tighter"><Activity className="w-6 h-6 text-yellow-400" />AI Active Positions</h3>
                            <button onClick={fetchData} className="p-2 hover:bg-white/5 rounded-xl transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-yellow-400" aria-label="Refresh positions">
                                <RefreshCcw className={`w-5 h-5 text-zinc-500 ${loading ? 'animate-spin' : ''}`} />
                            </button>
                        </div>

                        {positions.length === 0 ? (
                            <div className="text-center py-20 text-zinc-500">
                                <Wallet className="w-16 h-16 mx-auto mb-4 opacity-20" />
                                <p className="font-bold uppercase tracking-widest text-xs">No active positions found.</p>
                                <p className="text-[10px] opacity-70 mt-2 font-mono uppercase">The AI auto-trader has not executed any trades yet.</p>
                            </div>
                        ) : (
                            <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {positions.map((p, idx) => {
                                    return (
                                        <motion.div variants={itemVariants} key={idx} className="p-6 rounded-3xl border transition-all hover:scale-[1.05] bg-white/5 border-white/10 hover:shadow-2xl hover:border-yellow-400/50 group flex flex-col justify-between">
                                            <div className="flex justify-between items-start mb-6">
                                                <div>
                                                    <h4 className="text-xl font-black group-hover:text-yellow-400 transition-colors tracking-tighter text-zinc-100">{p.ticker}</h4>
                                                    <p className="text-[9px] font-black text-yellow-400/50 uppercase tracking-widest font-mono">{p.quantity} SHARES</p>
                                                </div>
                                                <div className="text-right">
                                                    <span className={`px-2 py-1 rounded-lg text-[10px] font-black font-mono ${p.profit_rate >= 0 ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>
                                                        {p.profit_rate >= 0 ? '+' : ''}{p.profit_rate.toFixed(2)}%
                                                    </span>
                                                </div>
                                            </div>

                                            <div className="pt-4 border-t border-white/5">
                                                <div className="flex justify-between items-center text-xs font-mono">
                                                    <span className="text-zinc-500 uppercase">PRC_CURR</span>
                                                    <span className="font-bold text-zinc-200">{getSymbol()}{formatNumber(displayCurrency === 'KRW' ? p.current_price_krw : (p.current_price_krw / exchangeRate), displayCurrency === 'USD' ? 2 : 0)}</span>
                                                </div>
                                                <div className="flex justify-between items-center text-xs mt-2 font-mono">
                                                    <span className="text-zinc-500 uppercase">PROFIT_LOSS</span>
                                                    <span className={`font-bold ${p.profit_amount_krw >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                                                        {p.profit_amount_krw >= 0 ? '+' : ''}
                                                        {getSymbol()}{formatNumber(displayCurrency === 'KRW' ? p.profit_amount_krw : (p.profit_amount_krw / exchangeRate), displayCurrency === 'USD' ? 2 : 0)}
                                                    </span>
                                                </div>
                                            </div>
                                        </motion.div>
                                    );
                                })}
                            </motion.div>
                        )}
                    </motion.div>
                )}
            </motion.div>
        </motion.div>
    );
};

export default PortfolioPage;
