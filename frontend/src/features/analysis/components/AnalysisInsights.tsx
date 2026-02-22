import React from 'react';
import { BarChart3, MessageSquare, Zap, Star, Eye, ChevronRight, Activity, AlertTriangle } from 'lucide-react';
import HelpTooltip from '../../../shared/ui/HelpTooltip';
import { AnalysisResult } from '../../../types/api';

interface AnalysisInsightsProps {
    analysis: AnalysisResult | null;
    selectedView: string;
    setSelectedView: (view: string) => void;
    setSelectedInterval: (interval: string) => void;
    isDark: boolean;
    t: Record<string, string>; // Translation object
    onOpenReport: () => void;
    onUpdateHistory: (interval: string) => void;
}

const TypewriterText = ({ text }: { text: string }) => {
    const [displayedText, setDisplayedText] = React.useState('');

    React.useEffect(() => {
        let i = 0;
        setDisplayedText('');
        const timer = setInterval(() => {
            if (i < text.length) {
                setDisplayedText((prev) => prev + text.charAt(i));
                i++;
            } else {
                clearInterval(timer);
            }
        }, 15);
        return () => clearInterval(timer);
    }, [text]);

    return <span className="animate-pulse-cursor">{displayedText}</span>;
};

const AnalysisInsights: React.FC<AnalysisInsightsProps> = ({
    analysis, selectedView, setSelectedView, setSelectedInterval, isDark, t, onOpenReport, onUpdateHistory
}) => {
    return (
        <div className="rounded-2xl border bg-white/5 backdrop-blur-md border-white/10 p-6 md:p-8 mb-8 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-yellow-400/5 blur-[100px] rounded-full pointer-events-none"></div>
            <div className="flex flex-col md:flex-row items-center justify-between mb-8 gap-4 relative z-10">
                <h3 className="text-xl font-bold flex items-center gap-3 tracking-tight text-zinc-100">
                    <BarChart3 className="w-5 h-5 text-yellow-400" />
                    AI_INSIGHT_ENGINE
                </h3>
                <div className="flex bg-white/5 p-1 rounded-xl border border-white/5">
                    {[
                        { id: 'short', label: t.ana_short_term, interval: '60m' },
                        { id: 'medium', label: t.ana_medium_term, interval: '1d' },
                        { id: 'long', label: t.ana_long_term, interval: '1wk' }
                    ].map((v) => (
                        <button
                            key={v.id}
                            onClick={() => {
                                setSelectedView(v.id);
                                setSelectedInterval(v.interval);
                                onUpdateHistory(v.interval);
                            }}
                            className={`px-4 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-widest transition-colors duration-200 ${selectedView === v.id ? 'bg-yellow-400 text-black shadow-sm' : 'text-zinc-500 hover:text-zinc-100 hover:bg-white/5'}`}
                        >
                            {v.label}
                        </button>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                <div className="lg:col-span-2 space-y-6 relative z-10">
                    <div className="p-6 rounded-xl border bg-white/[0.02] border-white/5 relative overflow-hidden group">
                        <p className="text-[10px] font-bold mb-4 flex items-center gap-2 uppercase tracking-widest text-yellow-400/70">
                            <MessageSquare className="w-3.5 h-3.5" />
                            QUANT_INTEL_STREAM
                        </p>
                        <div className="text-[15px] leading-relaxed whitespace-pre-wrap text-zinc-200 font-mono tracking-tight mb-6 bg-zinc-950/50 p-6 rounded-xl border border-white/5 shadow-inner min-h-[100px]">
                            <TypewriterText text={
                                typeof analysis?.full_report === 'object'
                                    ? JSON.stringify(analysis.full_report, null, 2)
                                    : (analysis?.full_report || "SYNCING_MARKET_HARMONICS...")
                            } />
                        </div>

                        <div className="p-5 rounded-lg border bg-yellow-400/5 border-yellow-400/10">
                            <p className="text-[8px] font-bold text-yellow-400/60 uppercase tracking-widest mb-2">PRECISION_CMD</p>
                            <p className="text-sm font-bold leading-relaxed text-zinc-100 italic">
                                "{analysis?.[`${selectedView}_term`]?.recommendation || "Calculating trade vector..."}"
                            </p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 font-black">
                        <div className={`p-7 rounded-2xl glass border border-white/5 transition-[background-color,border-color] duration-300 hover:bg-white/[0.03] hover:border-yellow-400/30 group`}>
                            <div className="text-[10px] text-yellow-400/60 mb-3 uppercase tracking-[0.25em] flex items-center gap-2 font-mono">
                                <Zap className="w-3 h-3 text-yellow-400" />
                                TECH_PARADIGM
                                <HelpTooltip indicatorId="AI Score" title="기술적 분석 관점" isDark={isDark} />
                            </div>
                            <p className="text-[13px] opacity-90 font-mono leading-relaxed text-zinc-300">{analysis?.[`${selectedView}_term`]?.focus_areas || "Architecting structural bias data..."}</p>
                        </div>
                        <div className={`p-7 rounded-2xl glass border border-white/5 transition-[background-color,border-color] duration-300 hover:bg-white/[0.03] hover:border-emerald-500/30 group`}>
                            <div className="text-[10px] text-emerald-400/60 mb-3 uppercase tracking-[0.25em] flex items-center gap-2 font-mono">
                                <Activity className="w-3 h-3 text-emerald-500" />
                                OPTIMIZED_HORIZON
                                <HelpTooltip indicatorId="SMA" title="최적 보유 기간" isDark={isDark} />
                            </div>
                            <p className="text-[13px] opacity-90 font-mono leading-relaxed text-zinc-300">{analysis?.[`${selectedView}_term`]?.holding_period || "Calculating time-series decay..."}</p>
                        </div>
                    </div>
                </div>

                <div className="space-y-6 relative z-10">
                    <div className="p-6 rounded-xl border bg-white/5 border-white/10 shadow-xl relative overflow-hidden group">
                        <div className="flex items-center gap-2 mb-6 text-yellow-400/70">
                            <Zap className="w-4 h-4 fill-yellow-400/30 animate-pulse" />
                            <span className="text-[9px] font-bold uppercase tracking-widest font-mono">PATTERN_HUB</span>
                        </div>

                        <div className="space-y-6">
                            {analysis?.all_patterns?.slice(0, 3).map((p, i) => {
                                const isWarning = p.desc.includes('⚠️') || p.desc.includes('미달') || p.desc.includes('주의');
                                return (
                                    <div key={i} className="pb-6 last:pb-0 border-b last:border-0 border-white/5 group/item">
                                        <div className="flex justify-between items-start mb-2">
                                            <div>
                                                <p className="text-xs font-bold text-zinc-100 group-hover/item:text-yellow-400 transition-colors uppercase tracking-tight font-mono">{p.name}</p>
                                                <span className="text-[8px] font-bold text-zinc-600 uppercase tracking-widest font-mono">{p.timeframe}</span>
                                            </div>
                                            <span className="text-[8px] font-bold bg-white/5 text-yellow-400/50 px-2 py-0.5 rounded border border-yellow-400/10 uppercase font-mono">active</span>
                                        </div>
                                        <div className="space-y-2">
                                            <p className="text-[11px] font-medium leading-relaxed text-zinc-400 font-mono">
                                                {p.desc.split('\n')[0]}
                                            </p>
                                            {isWarning && (
                                                <div className="flex items-start gap-1.5 p-2 rounded-lg bg-rose-400/5 border border-rose-400/10">
                                                    <AlertTriangle size={10} className="text-rose-400 shrink-0 mt-0.5" />
                                                    <p className="text-[9px] font-bold text-rose-400/70 leading-snug font-mono">
                                                        {p.desc.includes('⚠️') ? p.desc.split('⚠️')[1] : p.desc}
                                                    </p>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    <button
                        onClick={onOpenReport}
                        className="group relative overflow-hidden w-full py-4 rounded-xl font-bold text-[10px] uppercase tracking-widest flex items-center justify-center gap-3 transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] bg-yellow-400 text-black shadow-lg shadow-yellow-400/20"
                    >
                        <Eye className="w-4 h-4" />
                        FULL_REPORT
                        <ChevronRight className="w-3.5 h-3.5 opacity-50 group-hover:translate-x-1 transition-transform" />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AnalysisInsights;
