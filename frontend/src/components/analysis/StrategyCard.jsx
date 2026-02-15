import React from 'react';
import { motion } from 'framer-motion';
import { Shield, LayoutDashboard, CheckCircle2, AlertTriangle, TrendingUp, Zap } from 'lucide-react';

const StrategyCard = ({ analysis, isDark }) => {
    if (!analysis?.market_regime) return null;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 lg:grid-cols-12 gap-6"
        >
            {/* Market Regime Card (5 columns) */}
            <div className={`lg:col-span-5 p-8 rounded-3xl border shadow-xl flex flex-col justify-between transition-all duration-300 ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-2.5 rounded-2xl" style={{ backgroundColor: `${analysis.market_regime.color}15` }}>
                        <Shield className="w-6 h-6" style={{ color: analysis.market_regime.color }} />
                    </div>
                    <div>
                        <h3 className="text-xl font-black">Market Regime</h3>
                        <p className="text-[10px] opacity-50 font-black uppercase tracking-widest">Core Narrative Focus</p>
                    </div>
                </div>

                <div>
                    <div className="text-4xl font-black mb-3 tracking-tighter" style={{ color: analysis.market_regime.color }}>
                        {analysis.market_regime.label}
                    </div>
                    <p className="text-sm font-medium opacity-70 leading-relaxed mb-8">
                        {analysis.market_regime.desc}
                    </p>
                </div>

                <div className={`p-4 rounded-2xl flex items-center gap-4 ${isDark ? 'bg-slate-800/50' : 'bg-gray-50'}`}>
                    <div className="w-12 h-12 rounded-xl bg-blue-600/10 flex items-center justify-center text-blue-500">
                        <TrendingUp size={24} />
                    </div>
                    <div>
                        <p className="text-[10px] font-black opacity-40 uppercase">Primary Driver</p>
                        <p className="text-xs font-black">{analysis.market_regime.regime === 'Bull' ? 'Momentum Accumulation' : analysis.market_regime.regime === 'VCP' ? 'Volatility Contraction' : 'Distribution / Risk Off'}</p>
                    </div>
                </div>
            </div>

            {/* Strategy Checklist (7 columns) */}
            <div className={`lg:col-span-7 p-8 rounded-3xl border shadow-xl transition-all duration-300 ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-3">
                        <div className="bg-orange-500/10 p-2.5 rounded-2xl text-orange-500">
                            <LayoutDashboard className="w-6 h-6" />
                        </div>
                        <h3 className="text-xl font-black">Alpha Selection Box</h3>
                    </div>
                    <div className="flex items-center gap-1.5 px-3 py-1 bg-green-500/10 text-green-500 rounded-full text-[10px] font-black uppercase">
                        <div className="w-1 h-1 rounded-full bg-green-500 animate-pulse"></div>
                        Live Strategy Sync
                    </div>
                </div>

                <div className="space-y-3">
                    {analysis.strategy_checklist?.map((item) => (
                        <div
                            key={item.id}
                            className={`p-4 rounded-2xl border flex items-center justify-between transition-all ${item.status ? (isDark ? 'bg-green-500/5 border-green-500/20' : 'bg-green-50 border-green-100') : (isDark ? 'bg-slate-800/30 border-slate-700 opacity-60' : 'bg-gray-50 border-gray-100 opacity-60')}`}
                        >
                            <div className="flex items-center gap-4">
                                {item.status ?
                                    <CheckCircle2 size={18} className="text-green-500 shrink-0" /> :
                                    <AlertTriangle size={18} className="text-slate-400 shrink-0" />
                                }
                                <div>
                                    <p className={`text-sm font-bold ${item.status ? (isDark ? 'text-green-400' : 'text-green-700') : 'text-slate-400'}`}>
                                        {item.text}
                                    </p>
                                    <span className="text-[9px] font-black uppercase opacity-40">Priority: {item.importance}</span>
                                </div>
                            </div>
                            {item.status && (
                                <div className="px-2.5 py-1 rounded bg-green-500/20 text-green-500 text-[10px] font-black">
                                    PASS
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                <div className="mt-6 flex items-center gap-2 text-[11px] font-medium opacity-50 italic">
                    <Zap size={12} className="text-blue-500" />
                    These criteria are based on O'Neil & Minervini's institutional-grade selection rules.
                </div>
            </div>
        </motion.div>
    );
};

export default StrategyCard;
