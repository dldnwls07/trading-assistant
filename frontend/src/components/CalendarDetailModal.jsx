import React, { useState, useEffect } from 'react';
import { X, TrendingUp, AlertTriangle, Brain, History, Target } from 'lucide-react';
import api from '../utils/api';

const CalendarDetailModal = ({ isOpen, onClose, event, isDark, t }) => {
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [ticker, setTicker] = useState('005930.KS'); // Default to Samsung for demo

    useEffect(() => {
        if (isOpen && event) {
            fetchAnalysis();
        }
    }, [isOpen, event, ticker]);

    const fetchAnalysis = async () => {
        setLoading(true);
        try {
            const res = await api.get(`/api/calendar/analyze?ticker=${ticker}&event_title=${event.title}`);
            setAnalysis(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen || !event) return null;

    return (
        <div className="fixed inset-0 z-[1000] flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-md" onClick={onClose} />

            <div className={`relative w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-[2rem] border transition-all duration-500 shadow-2xl ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200'
                }`}>
                <header className="sticky top-0 z-10 flex items-center justify-between p-8 bg-inherit/90 backdrop-blur-md border-b border-inherit">
                    <div className="flex items-center gap-4">
                        <div className="bg-blue-600 p-3 rounded-2xl text-white shadow-lg shadow-blue-600/20">
                            <Brain className="w-6 h-6" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-black tracking-tight">{event.title}</h2>
                            <p className="text-sm opacity-50 font-medium capitalize">{event.country} • {event.category}</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-3 rounded-2xl hover:bg-slate-500/10 transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </header>

                <div className="p-8 space-y-10">
                    {/* Event Description */}
                    <section className="space-y-4">
                        <h3 className="text-xs font-bold uppercase tracking-widest opacity-40 flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4" /> 상세 정보 및 리스크
                        </h3>
                        <div className={`p-6 rounded-3xl leading-relaxed ${isDark ? 'bg-slate-950/50' : 'bg-slate-50'}`}>
                            {event.description || '이 이벤트에 대한 상세 설명이 없습니다.'}
                        </div>
                    </section>

                    {/* AI Market Outlook & Strategy (New) */}
                    {event.scenarios && (
                        <section className="space-y-6">
                            <h3 className="text-xs font-bold uppercase tracking-widest opacity-40 flex items-center gap-2">
                                <Brain className="w-4 h-4 text-purple-400" /> AI 시장 전망 및 대응 전략
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className={`p-6 rounded-3xl border ${isDark ? 'bg-slate-950/50 border-slate-800' : 'bg-red-50/50 border-red-100'}`}>
                                    <p className="text-sm font-black text-red-500 mb-3 border-b border-red-100 pb-2">기대치 상회 시 (Higher than Forecast)</p>
                                    <p className="text-sm leading-relaxed opacity-80 font-bold">{event.scenarios.high}</p>
                                </div>
                                <div className={`p-6 rounded-3xl border ${isDark ? 'bg-slate-950/50 border-slate-800' : 'bg-green-50/50 border-green-100'}`}>
                                    <p className="text-sm font-black text-green-600 mb-3 border-b border-green-100 pb-2">기대치 하회 시 (Lower than Forecast)</p>
                                    <p className="text-sm leading-relaxed opacity-80 font-bold">{event.scenarios.low}</p>
                                </div>
                            </div>
                        </section>
                    )}

                    {/* AI Historical Impact */}
                    <section className="space-y-6">
                        <div className="flex items-center justify-between">
                            <h3 className="text-xs font-bold uppercase tracking-widest opacity-40 flex items-center gap-2">
                                <History className="w-4 h-4" /> 과거 데이터 기반 상관분석
                            </h3>
                            <div className="flex items-center gap-2">
                                <span className="text-[10px] font-bold opacity-40 uppercase">Target Ticker:</span>
                                <input
                                    className={`text-[10px] font-bold uppercase p-1 rounded-lg border ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}
                                    value={ticker}
                                    onChange={(e) => setTicker(e.target.value.toUpperCase())}
                                />
                            </div>
                        </div>

                        {loading ? (
                            <div className="flex flex-col items-center py-10 gap-3">
                                <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
                                <span className="text-xs font-bold opacity-40 animate-pulse">퀀트 엔진 가동 중...</span>
                            </div>
                        ) : analysis && (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className={`p-6 rounded-3xl border ${isDark ? 'bg-slate-950/50 border-slate-800' : 'bg-slate-50 border-slate-100'}`}>
                                    <p className="text-xs font-bold opacity-40 mb-2 uppercase">평균 변동률 (Day 1)</p>
                                    <div className="flex items-end gap-2">
                                        <span className={`text-4xl font-black ${analysis.avg_impact_pct >= 0 ? 'text-red-500' : 'text-blue-500'}`}>
                                            {analysis.avg_impact_pct > 0 ? '+' : ''}{analysis.avg_impact_pct}%
                                        </span>
                                        <TrendingUp className={`w-6 h-6 mb-1 ${analysis.avg_impact_pct >= 0 ? 'text-red-500' : 'text-blue-500'}`} />
                                    </div>
                                </div>
                                <div className={`p-6 rounded-3xl border ${isDark ? 'bg-slate-950/50 border-slate-800' : 'bg-slate-50 border-slate-100'}`}>
                                    <p className="text-xs font-bold opacity-40 mb-2 uppercase">트레이딩 가이던스</p>
                                    <div className="flex items-center gap-3">
                                        <div className={`px-4 py-2 rounded-xl text-sm font-black text-white ${analysis.recommendation.includes('매수') ? 'bg-red-500' : 'bg-slate-500'
                                            }`}>
                                            {analysis.recommendation}
                                        </div>
                                        <Target className="w-6 h-6 text-blue-600" />
                                    </div>
                                </div>
                            </div>
                        )}
                    </section>
                </div>

                <footer className="p-8 border-t border-inherit bg-slate-500/5 text-[10px] font-bold opacity-40 text-center uppercase tracking-widest">
                    AI Analysis based on Historical Market Response Correlation
                </footer>
            </div>
        </div>
    );
};

export default CalendarDetailModal;
