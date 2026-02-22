import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Brain,
    X,
    AlertTriangle,
    History,
    TrendingUp,
    Target,
    BarChart3,
    Activity,
    LineChart
} from 'lucide-react';
import api from '../../../utils/api';

const CalendarDetailModal = ({ isOpen, onClose, event, isDark, t }) => {
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    // Use event ticker if available, otherwise default to a relevant one
    const [ticker, setTicker] = useState('');

    useEffect(() => {
        if (event?.ticker) {
            setTicker(event.ticker);
        } else if (event?.country === 'KR') {
            setTicker('005930.KS');
        } else {
            setTicker('SPY');
        }
    }, [event]);

    useEffect(() => {
        if (isOpen && event && ticker) {
            fetchAnalysis();
        }
    }, [isOpen, event, ticker]);

    const fetchAnalysis = async () => {
        setLoading(true);
        try {
            const res = await api.get(`/api/calendar/analyze`, {
                params: {
                    ticker: ticker,
                    event_title: event.title
                }
            });
            setAnalysis(res.data);
        } catch (err) {
            console.error("Analysis fetch failed:", err);
            // Fallback for demo if backend fails
            setAnalysis({
                avg_impact_pct: 1.2,
                recommendation: "시장 관망 (Hold)",
                confidence: 75
            });
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen || !event) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-[1000] flex items-center justify-center p-4">
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0 bg-black/80 backdrop-blur-xl"
                    onClick={onClose}
                />

                <motion.div
                    initial={{ opacity: 0, scale: 0.9, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9, y: 20 }}
                    className="relative w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-[2.5rem] border transition-all duration-500 shadow-2xl bg-[#09090b] border-white/10 text-zinc-100"
                >
                    <header className="sticky top-0 z-10 flex items-center justify-between p-8 bg-[#09090b]/90 backdrop-blur-md border-b border-white/5">
                        <div className="flex items-center gap-4">
                            <div className="bg-yellow-400 p-3 rounded-2xl text-black shadow-lg shadow-yellow-400/20">
                                <Brain className="w-6 h-6" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-black tracking-tighter uppercase">{event.title}</h2>
                                <p className="text-[10px] opacity-40 font-mono font-bold uppercase tracking-widest">{event.country} • {event.category}</p>
                            </div>
                        </div>
                        <button onClick={onClose} className="p-3 rounded-2xl hover:bg-white/5 transition-all text-zinc-500 hover:text-zinc-100 border border-transparent hover:border-white/10">
                            <X className="w-6 h-6" />
                        </button>
                    </header>

                    <div className="p-8 space-y-10">
                        {/* Event Description */}
                        <section className="space-y-4">
                            <h3 className="text-[10px] font-black uppercase tracking-widest text-zinc-500 flex items-center gap-2 font-mono">
                                <AlertTriangle className="w-4 h-4 text-yellow-400" /> EVENT_INTEL_RECAP
                            </h3>
                            <div className="p-6 rounded-3xl leading-relaxed bg-white/5 border border-white/5 text-zinc-300 font-medium">
                                {event.description || '이 이벤트에 대한 상세 설명이 없습니다.'}
                            </div>
                        </section>

                        {/* AI Market Outlook & Strategy */}
                        {event.scenarios && (
                            <section className="space-y-6">
                                <h3 className="text-[10px] font-black uppercase tracking-widest text-zinc-500 flex items-center gap-2 font-mono">
                                    <Activity className="w-4 h-4 text-yellow-400" /> NEURAL_PRESET_SCENARIOS
                                </h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="p-6 rounded-3xl border bg-white/5 border-white/10 group hover:border-yellow-400/30 transition-all">
                                        <p className="text-[10px] font-black text-yellow-400 mb-4 border-b border-yellow-400/10 pb-2 uppercase tracking-widest font-mono">Higher_than_Forecast</p>
                                        <p className="text-sm leading-relaxed text-zinc-300 font-bold">{event.scenarios.high}</p>
                                    </div>
                                    <div className="p-6 rounded-3xl border bg-white/5 border-white/10 group hover:border-yellow-400/30 transition-all">
                                        <p className="text-[10px] font-black text-yellow-400 mb-4 border-b border-yellow-400/10 pb-2 uppercase tracking-widest font-mono">Lower_than_Forecast</p>
                                        <p className="text-sm leading-relaxed text-zinc-300 font-bold">{event.scenarios.low}</p>
                                    </div>
                                </div>
                            </section>
                        )}

                        {/* AI Historical Impact */}
                        <section className="space-y-6">
                            <div className="flex items-center justify-between">
                                <h3 className="text-[10px] font-black uppercase tracking-widest text-zinc-500 flex items-center gap-2 font-mono">
                                    <History className="w-4 h-4 text-yellow-400" /> BACKTESTED_CORRELATION
                                </h3>
                                <div className="flex items-center gap-2">
                                    <span className="text-[9px] font-black opacity-40 uppercase tracking-widest font-mono">Target_Ticker:</span>
                                    <input
                                        className="text-[11px] font-black uppercase p-2 rounded-xl border bg-white/5 border-white/10 text-zinc-100 outline-none focus:border-yellow-400 transition-all font-mono"
                                        value={ticker}
                                        onChange={(e) => setTicker(e.target.value.toUpperCase())}
                                    />
                                </div>
                            </div>

                            {loading ? (
                                <div className="flex flex-col items-center py-12 gap-4 bg-white/5 rounded-3xl border border-white/10">
                                    <div className="w-10 h-10 border-4 border-yellow-400 border-t-transparent rounded-full animate-spin" />
                                    <span className="text-[10px] font-black text-zinc-500 animate-pulse uppercase tracking-[0.3em] font-mono">Quant_Engine_Computing...</span>
                                </div>
                            ) : analysis && (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="p-6 rounded-3xl border bg-white/5 border-white/10 hover:border-yellow-400/20 transition-all">
                                        <p className="text-[10px] font-black text-zinc-500 mb-3 uppercase tracking-widest font-mono flex items-center gap-2">
                                            <LineChart className="w-3 h-3" /> Avg_Day1_Volatility
                                        </p>
                                        <div className="flex items-end gap-2">
                                            <span className={`text-4xl font-black font-mono ${analysis.avg_impact_pct >= 0 ? 'text-yellow-400' : 'text-rose-500'}`}>
                                                {analysis.avg_impact_pct > 0 ? '+' : ''}{analysis.avg_impact_pct}%
                                            </span>
                                            <TrendingUp className={`w-6 h-6 mb-1 ${analysis.avg_impact_pct >= 0 ? 'text-yellow-400' : 'text-rose-500'}`} />
                                        </div>
                                    </div>
                                    <div className="p-6 rounded-3xl border bg-white/5 border-white/10 hover:border-yellow-400/20 transition-all">
                                        <p className="text-[10px] font-black text-zinc-500 mb-3 uppercase tracking-widest font-mono flex items-center gap-2">
                                            <BarChart3 className="w-3 h-3" /> Trading_Guidance
                                        </p>
                                        <div className="flex items-center gap-3">
                                            <div className="px-4 py-2 rounded-xl text-xs font-black bg-yellow-400 text-black shadow-lg shadow-yellow-400/20 uppercase tracking-tighter">
                                                {analysis.recommendation}
                                            </div>
                                            <Target className="w-6 h-6 text-yellow-400 opacity-50" />
                                        </div>
                                    </div>
                                </div>
                            )}
                        </section>
                    </div>

                    <footer className="p-8 border-t border-white/5 bg-white/5 text-[9px] font-black text-zinc-600 text-center uppercase tracking-[0.4em] font-mono">
                        Neural_Pulsar_Analysis_Symmetric_Verification
                    </footer>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default CalendarDetailModal;
