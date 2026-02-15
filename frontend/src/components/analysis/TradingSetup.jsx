import React from 'react';
import { motion } from 'framer-motion';
import { Zap, Activity, Clock, Star } from 'lucide-react';

const TradingSetup = ({ analysis, isDark }) => {
    if (!analysis?.consensus?.global_ensemble) return null;

    const setup = analysis.consensus.global_ensemble;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`p-8 rounded-3xl border shadow-2xl transition-all duration-300 ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}
        >
            <div className="flex items-center gap-3 mb-8">
                <div className="bg-blue-600/10 p-2.5 rounded-2xl">
                    <Zap className="w-6 h-6 text-blue-500" />
                </div>
                <div>
                    <h3 className="text-xl font-black">🛡️ Strategic Trading Setup</h3>
                    <p className="text-xs opacity-50 font-medium tracking-tight">Multi-Engine High-Precision Analysis</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Grade & Risk */}
                <div className="flex flex-col items-center justify-center p-6 rounded-2xl bg-blue-500/5 border border-blue-500/10">
                    <span className="text-[10px] font-black text-blue-500 uppercase tracking-widest mb-3">Setup Grade</span>
                    <div className="text-5xl font-black text-blue-600 mb-2">
                        {setup.grade?.split(' ')[0] || 'C'}
                    </div>
                    <div className="text-[10px] font-bold opacity-60">Confidence: {setup.confidence}%</div>
                    <div className="mt-4 flex items-center gap-2">
                        <span className="text-[10px] font-black opacity-40">Risk Index:</span>
                        <div className="w-20 h-1.5 rounded-full bg-gray-200 overflow-hidden">
                            <div
                                className={`h-full ${setup.risk_impact > 0.7 ? 'bg-red-500' : 'bg-green-500'}`}
                                style={{ width: `${setup.risk_impact * 100}%` }}
                            ></div>
                        </div>
                    </div>
                </div>

                {/* ML Prediction */}
                <div className="p-6 rounded-2xl bg-slate-500/5 border border-slate-500/10">
                    <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                        <Activity className="w-3 h-3" />
                        🤖 AI ML Forecast (5D)
                    </p>
                    {analysis.medium_term?.full_analysis?.ml_forecast?.success ? (
                        <>
                            <div className={`text-2xl font-black mb-1 ${analysis.medium_term.full_analysis.ml_forecast.direction === '상승' ? 'text-green-500' : 'text-red-500'}`}>
                                {analysis.medium_term.full_analysis.ml_forecast.direction} ({(analysis.medium_term.full_analysis.ml_forecast.predicted_return * 100).toFixed(1)}%)
                            </div>
                            <p className="text-[11px] font-medium opacity-60 leading-relaxed">
                                {analysis.medium_term.full_analysis.ml_forecast.message}
                            </p>
                        </>
                    ) : (
                        <div className="text-xs opacity-40 italic">Calculating prediction vectors...</div>
                    )}
                </div>

                {/* Backtest */}
                <div className="p-6 rounded-2xl bg-slate-500/5 border border-slate-500/10">
                    <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                        <Clock className="w-3 h-3" />
                        📊 Strategy Backtest (1Y)
                    </p>
                    {analysis.medium_term?.full_analysis?.backtest?.success ? (
                        <div className="space-y-3">
                            <div className="flex items-end gap-2">
                                <span className="text-2xl font-black">{analysis.medium_term.full_analysis.backtest.win_rate}%</span>
                                <span className="text-[10px] font-bold opacity-50 mb-1">Win Rate</span>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <p className="text-[9px] font-black opacity-40 uppercase">Profit Factor</p>
                                    <p className="text-sm font-bold">{analysis.medium_term.full_analysis.backtest.profit_factor}</p>
                                </div>
                                <div>
                                    <p className="text-[9px] font-black opacity-40 uppercase">Max Drawdown</p>
                                    <p className="text-sm font-bold text-red-500">{analysis.medium_term.full_analysis.backtest.mdd_pct}%</p>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-xs opacity-40 italic">Simulating historical performance...</div>
                    )}
                </div>
            </div>

            {/* Confluence Details */}
            <div className="mt-8 p-6 rounded-2xl bg-blue-600/5 border border-blue-600/10">
                <h4 className="text-xs font-black uppercase tracking-widest text-blue-500 mb-4 flex items-center gap-2">
                    <Star className="w-3 h-3 fill-current" />
                    Confluence & Intelligence Insights
                </h4>
                <div className="space-y-2.5">
                    {setup.confluence_details?.map((detail, idx) => (
                        <div key={idx} className="flex items-start gap-3 text-sm font-medium opacity-80 decoration-blue-500/30">
                            <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5 shrink-0"></div>
                            {detail}
                        </div>
                    ))}
                    <div className="pt-4 border-t border-blue-600/10 mt-2 text-sm font-black text-blue-600 italic">
                        💡 recommendation: {setup.recommendation}
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default TradingSetup;
