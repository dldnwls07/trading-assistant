import React from 'react';
import { BarChart3, MessageSquare, Zap, Star, Eye, ChevronRight, Activity } from 'lucide-react';
import HelpTooltip from '../HelpTooltip';
import { AnalysisResult } from '../../types/api';

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
        <div className={`rounded-2xl border glass p-6 mb-8 transition-all duration-300 ${isDark ? 'border-slate-800' : 'border-gray-100'}`}>
            <div className="flex flex-col md:flex-row items-center justify-between mb-6 gap-4">
                <h3 className="text-xl font-black flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-blue-500" />
                    AI Insight Engine 4.0
                </h3>
                <div className={`flex p-1.5 rounded-2xl ${isDark ? 'bg-slate-800' : 'bg-gray-100'}`}>
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
                            className={`px-6 py-2 rounded-xl text-xs font-black transition-all ${selectedView === v.id ? (isDark ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/20' : 'bg-white text-blue-600 shadow-md') : 'text-gray-400 hover:text-gray-600'}`}
                        >
                            {v.label}
                        </button>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                <div className="lg:col-span-2 space-y-6">
                    <div className={`p-8 rounded-3xl glass-blue border-l-[6px] border-blue-600 relative overflow-hidden`}>
                        <div className="absolute top-4 right-6 opacity-5">
                            <Zap className="w-24 h-24 fill-current" />
                        </div>
                        <p className="text-xl font-black mb-6 flex items-center gap-2">
                            <MessageSquare className="w-5 h-5 text-blue-500" />
                            Quantitative Intelligence Report
                        </p>
                        <div className="text-sm leading-relaxed whitespace-pre-wrap opacity-90 font-medium terminal-font mb-8 bg-black/30 p-6 rounded-2xl border border-white/5 shadow-inner min-h-[100px]">
                            <TypewriterText text={
                                typeof analysis?.full_report === 'object'
                                    ? JSON.stringify(analysis.full_report, null, 2)
                                    : (analysis?.full_report || "Analyzing real-time harmonics and structural shifts...")
                            } />
                        </div>

                        <div className={`p-5 rounded-2xl border ${isDark ? 'bg-blue-500/5 border-blue-500/20' : 'bg-blue-50 border-blue-100'}`}>
                            <p className="text-[10px] font-black text-blue-500 uppercase tracking-widest mb-2">Selected Timeframe Strategy</p>
                            <p className="text-sm font-bold leading-relaxed whitespace-pre-wrap">
                                {analysis?.[`${selectedView}_term`]?.recommendation || "Generating strategic alignment..."}
                            </p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 font-black">
                        <div className={`p-6 rounded-2xl glass border border-blue-500/20 transition-all hover:bg-blue-500/5 group`}>
                            <p className="text-[10px] text-blue-400 mb-2 uppercase tracking-[0.2em] flex items-center gap-2">
                                <Zap className="w-3 h-3" />
                                Technical Paradigm
                                <HelpTooltip indicatorId="AI Score" title="기술적 분석 관점" isDark={isDark} />
                            </p>
                            <p className="text-sm opacity-90 terminal-font leading-relaxed">{analysis?.[`${selectedView}_term`]?.focus_areas || "Architecting structural bias data..."}</p>
                        </div>
                        <div className={`p-6 rounded-2xl glass border border-emerald-500/20 transition-all hover:bg-emerald-500/5 group`}>
                            <p className="text-[10px] text-emerald-400 mb-2 uppercase tracking-[0.2em] flex items-center gap-2">
                                <Activity className="w-3 h-3" />
                                Optimized Horizon
                                <HelpTooltip indicatorId="SMA" title="최적 보유 기간" isDark={isDark} />
                            </p>
                            <p className="text-sm opacity-90 terminal-font leading-relaxed">{analysis?.[`${selectedView}_term`]?.holding_period || "Calculating time-series decay..."}</p>
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    <div className={`p-6 rounded-3xl shadow-2xl relative overflow-hidden transition-all duration-500 group ${isDark ? 'bg-slate-900 border border-slate-800' : 'bg-gray-900 text-white'}`}>
                        <div className="absolute -bottom-10 -right-10 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl group-hover:bg-blue-500/20 transition-all"></div>
                        <div className="flex items-center gap-2 mb-6 text-blue-400">
                            <Zap className="w-5 h-5 fill-current" />
                            <span className="text-xs font-black uppercase tracking-widest">Active Pattern Hub</span>
                        </div>
                        <div className="space-y-4 relative z-10">
                            {analysis?.all_patterns?.slice(0, 3).map((p, i) => (
                                <div key={i} className={`pb-4 last:pb-0 border-b last:border-0 ${isDark ? 'border-slate-800' : 'border-white/10'}`}>
                                    <div className="flex justify-between items-center mb-1.5">
                                        <p className="text-sm font-black group-hover:text-blue-400 transition-colors uppercase">{p.name}</p>
                                        <span className="text-[9px] font-black bg-blue-600/20 text-blue-500 px-2 py-0.5 rounded-lg border border-blue-500/20">{p.timeframe}</span>
                                    </div>
                                    <p className={`text-[11px] font-medium leading-relaxed ${isDark ? 'text-slate-400' : 'text-gray-300 opacity-70'}`}>{p.desc}</p>
                                </div>
                            ))}
                            {(!analysis?.all_patterns || analysis.all_patterns.length === 0) && (
                                <p className="text-[11px] text-gray-500 italic py-4">No structural patterns detected in the current window.</p>
                            )}
                        </div>
                    </div>

                    <button
                        onClick={onOpenReport}
                        className={`w-full py-5 rounded-2xl font-black flex items-center justify-center gap-3 transition-all transform hover:scale-[1.02] active:scale-[0.98] shadow-2xl ${isDark ? 'bg-blue-600 text-white shadow-blue-900/40 hover:bg-blue-500' : 'bg-blue-600 text-white shadow-blue-200 hover:bg-blue-700'}`}
                    >
                        <Eye className="w-6 h-6" />
                        READ FULL REPORT
                        <ChevronRight className="w-4 h-4 ml-1" />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AnalysisInsights;
