import React from 'react';
import { motion } from 'framer-motion';
import { Zap, Activity, Clock, Star } from 'lucide-react';
import { AnalysisResult } from '../../types/api';

interface TradingSetupProps {
    analysis: AnalysisResult | null;
    isDark: boolean;
}

const TradingSetup: React.FC<TradingSetupProps> = ({ analysis, isDark }) => {
    if (!analysis?.consensus?.global_ensemble) return null;

    const setup = analysis.consensus.global_ensemble;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-8 rounded-2xl border bg-white/5 backdrop-blur-md border-white/10 shadow-2xl relative overflow-hidden"
        >
            <div className="flex items-center gap-4 mb-8">
                <div className="bg-yellow-400/10 p-2.5 rounded-xl border border-yellow-400/20">
                    <Zap className="w-6 h-6 text-yellow-400 fill-yellow-400/20" />
                </div>
                <div>
                    <h3 className="text-xl font-bold tracking-tight uppercase font-mono text-zinc-100">STRATEGY_CMD</h3>
                    <p className="text-[10px] text-zinc-500 font-bold tracking-widest uppercase">Multi-Engine Ensemble</p>
                </div>
            </div>

            <div className="flex flex-col gap-5">
                {/* 1. Grade & Risk - Top Priority Segment */}
                <div className="p-6 rounded-xl border bg-white/[0.02] border-white/5 relative overflow-hidden group">
                    <div className="flex justify-between items-start mb-4">
                        <div>
                            <span className="text-[10px] font-bold text-yellow-400/70 uppercase tracking-widest font-mono block mb-1">GRADE</span>
                            <div className="text-6xl font-bold text-yellow-400 font-mono tracking-tighter">
                                {setup.grade?.split(' ')[0] || 'C'}
                            </div>
                        </div>
                        <div className="text-right">
                            <span className="text-[9px] font-bold text-zinc-600 uppercase tracking-widest font-mono block mb-1.5">CONFIDENCE</span>
                            <div className="px-2.5 py-1 rounded bg-yellow-400/10 border border-yellow-400/20 text-yellow-400 text-xs font-bold font-mono">
                                {setup.confidence}%
                            </div>
                        </div>
                    </div>

                    <div className="space-y-2.5">
                        <div className="flex items-center justify-between font-mono">
                            <span className="text-[9px] font-bold text-rose-400/50 uppercase tracking-widest">RISK_EXPOSURE</span>
                            <span className="text-[10px] font-bold text-rose-400">{(setup.risk_impact * 100).toFixed(0)}%</span>
                        </div>
                        <div className="w-full h-1 rounded-full bg-white/5 overflow-hidden">
                            <div
                                className={`h-full transition-all duration-1000 ease-out ${setup.risk_impact > 0.7 ? 'bg-rose-500' : 'bg-yellow-400'}`}
                                style={{ width: `${setup.risk_impact * 100}%` }}
                            ></div>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                    {/* 2. ML Prediction */}
                    <div className={`p-6 rounded-[1.5rem] border glass border-white/5 bg-white/[0.01] shadow-inner`}>
                        <p className="text-[9px] font-black text-muted-foreground uppercase tracking-[0.2em] mb-4 flex items-center gap-3 font-mono">
                            <Activity className="w-3 h-3 text-secondary" />
                            ML_PRED
                        </p>
                        {analysis.medium_term?.full_analysis?.ml_forecast?.success ? (
                            <div className="space-y-2">
                                <div className={`text-2xl font-black font-mono tracking-tighter ${analysis.medium_term!.full_analysis!.ml_forecast!.direction === '상승' ? 'text-green-500' : 'text-red-500'}`}>
                                    {(analysis.medium_term!.full_analysis!.ml_forecast!.predicted_return * 100).toFixed(1)}%
                                </div>
                                <div className="text-[10px] font-bold opacity-30 uppercase font-mono">{analysis.medium_term!.full_analysis!.ml_forecast!.direction === '상승' ? 'BULLISH' : 'BEARISH'}</div>
                            </div>
                        ) : (
                            <div className="py-4 text-center opacity-10 font-black text-[8px] tracking-[0.3em] font-mono">CALC...</div>
                        )}
                    </div>

                    {/* 3. Backtest */}
                    <div className={`p-6 rounded-[1.5rem] border glass border-white/5 bg-white/[0.01] shadow-inner`}>
                        <p className="text-[9px] font-black text-muted-foreground uppercase tracking-[0.2em] mb-4 flex items-center gap-3 font-mono">
                            <Clock className="w-3 h-3 text-secondary" />
                            WIN_RT
                        </p>
                        {analysis.medium_term?.full_analysis?.backtest?.success ? (
                            <div className="space-y-2">
                                <div className="text-2xl font-black font-mono tracking-tighter text-foreground">
                                    {analysis.medium_term!.full_analysis!.backtest!.win_rate}%
                                </div>
                                <div className="text-[10px] font-bold opacity-30 uppercase font-mono">SIM_SUCCESS</div>
                            </div>
                        ) : (
                            <div className="py-4 text-center opacity-10 font-black text-[8px] tracking-[0.3em] font-mono">SIM...</div>
                        )}
                    </div>
                </div>
            </div>

            {/* Confluence Details */}
            <div className="mt-8 p-6 rounded-xl border bg-white/[0.01] border-white/5">
                <h4 className="text-[9px] font-bold uppercase tracking-widest text-yellow-400/50 mb-5 flex items-center gap-2">
                    <Star className="w-3 h-3 fill-yellow-400/30" />
                    CONFLUENCE_STREAM
                </h4>
                <div className="space-y-3.5">
                    {setup.confluence_details?.map((detail, idx) => (
                        <div key={idx} className="flex items-start gap-3 text-xs font-medium text-zinc-400 group">
                            <div className="w-1 h-1 rounded-full bg-yellow-400 mt-1.5 shrink-0 opacity-50"></div>
                            <span className="line-clamp-2 leading-relaxed">{detail}</span>
                        </div>
                    ))}
                    <div className="pt-5 border-t border-white/5 mt-4 flex items-start gap-3">
                        <span className="text-[9px] font-bold text-yellow-400 leading-tight uppercase tracking-widest mt-0.5 shrink-0">MSG:</span>
                        <span className="text-xs font-bold leading-relaxed text-zinc-200">{setup.recommendation}</span>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default TradingSetup;
