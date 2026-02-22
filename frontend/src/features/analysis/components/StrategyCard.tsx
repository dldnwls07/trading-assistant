import React from 'react';
import { motion } from 'framer-motion';
import { Shield, LayoutDashboard, CheckCircle2, AlertTriangle, TrendingUp, Zap } from 'lucide-react';
import { AnalysisResult } from '../../../types/api';

interface StrategyCardProps {
    analysis: AnalysisResult | null;
    isDark: boolean;
}

const StrategyCard: React.FC<StrategyCardProps> = ({ analysis, isDark }) => {
    if (!analysis?.market_regime) return null;

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
        >
            {/* Market Regime Section - Stitch Minimalist */}
            <div className="p-6 rounded-xl border bg-white/5 backdrop-blur-md border-white/10 shadow-xl relative overflow-hidden group">
                <div className="absolute inset-x-0 top-0 h-[2px] opacity-40" style={{ backgroundColor: analysis.market_regime.color }}></div>

                <div className="flex items-center gap-4 mb-6">
                    <div className="p-2 rounded-lg border border-white/5 bg-white/5">
                        <Shield className="w-5 h-5 text-zinc-400" />
                    </div>
                    <div>
                        <h3 className="text-sm font-bold tracking-widest uppercase font-mono text-zinc-500">REGIME_SIGNAL</h3>
                    </div>
                </div>

                <div className="mb-8">
                    <div className="text-3xl font-bold mb-2 tracking-tighter font-mono uppercase leading-tight" style={{ color: analysis.market_regime.color }}>
                        {analysis.market_regime.label}
                    </div>
                    <p className="text-[11px] font-medium text-zinc-400 leading-relaxed font-mono">
                        {analysis.market_regime.desc}
                    </p>
                </div>

                <div className="p-4 rounded-lg flex items-center gap-3 bg-white/[0.02] border border-white/5">
                    <div className="w-10 h-10 rounded-lg bg-yellow-400/10 flex items-center justify-center text-yellow-400 border border-yellow-400/10">
                        <TrendingUp size={20} />
                    </div>
                    <div>
                        <p className="text-[8px] font-bold text-zinc-600 uppercase tracking-widest font-mono">PRIMARY_DRIVER</p>
                        <p className="text-[10px] font-bold text-zinc-300 uppercase font-mono">{analysis.market_regime.regime === 'Bull' ? 'MOMENTUM_ACCUM' : analysis.market_regime.regime === 'VCP' ? 'VOL_CONTRACTION' : 'RISK_SHIELD'}</p>
                    </div>
                </div>
            </div>

            {/* Alpha Selection Box (Strategy Checklist) */}
            <div className="p-6 rounded-xl border bg-white/5 backdrop-blur-md border-white/10 shadow-xl relative overflow-hidden group">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-4">
                        <div className="bg-yellow-400/10 p-2 rounded-lg text-yellow-400 border border-yellow-400/20">
                            <LayoutDashboard className="w-5 h-5" />
                        </div>
                        <h3 className="text-sm font-bold tracking-widest uppercase font-mono text-zinc-100">ALPHA_BOX</h3>
                    </div>
                    <div className="flex items-center gap-1.5 px-2 py-1 bg-yellow-400/10 text-yellow-400 border border-yellow-400/20 rounded text-[8px] font-bold uppercase tracking-widest">
                        <div className="w-1 h-1 rounded-full bg-yellow-400 animate-pulse"></div>
                        SYNC
                    </div>
                </div>

                <div className="space-y-2.5">
                    {analysis.strategy_checklist ? analysis.strategy_checklist.map((item) => (
                        <div
                            key={item.id}
                            className={`p-4 rounded-lg border transition-colors duration-200 flex items-center justify-between hover:bg-white/[0.04] ${item.status ? 'bg-yellow-400/5 border-yellow-400/20' : 'bg-transparent border-white/5 opacity-40'}`}
                        >
                            <div className="flex items-center gap-3">
                                <div className={`p-1 rounded-md border border-white/5 ${item.status ? 'bg-yellow-400/20 text-yellow-400' : 'bg-white/5 text-zinc-500'}`}>
                                    {item.status ?
                                        <CheckCircle2 size={12} strokeWidth={3} /> :
                                        <AlertTriangle size={12} />
                                    }
                                </div>
                                <p className={`text-[11px] font-bold tracking-tight ${item.status ? 'text-zinc-100' : 'text-zinc-600'}`}>
                                    {item.text}
                                </p>
                            </div>
                        </div>
                    )) : (
                        <div className="py-6 text-center text-zinc-800 text-[10px] font-bold uppercase tracking-widest font-mono">NO_DATA_STREAMS</div>
                    )}
                </div>

                <div className="mt-6 pt-5 border-t border-white/5 flex items-center gap-2 text-[8px] font-bold text-zinc-700 tracking-widest font-mono uppercase">
                    <Zap size={10} className="text-yellow-400/50 shrink-0" />
                    RULES: O'NEIL_V2.1_ALPHA
                </div>
            </div>
        </motion.div>
    );
};

export default StrategyCard;
