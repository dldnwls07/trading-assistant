import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, Clock, Globe, AlertCircle } from 'lucide-react';
import { AnalysisResult } from '../../types/api';

interface CalendarWidgetProps {
    analysis: AnalysisResult | null;
    isDark: boolean;
}

const CalendarWidget: React.FC<CalendarWidgetProps> = ({ analysis, isDark }) => {
    // events from analysis might contain earnings_date, dividends, or other stock-specific info
    const stockEvents = analysis?.events || {};

    // Check if there's actual data to display
    const hasData = Object.keys(stockEvents).length > 0;

    return (
        <div className={`rounded-3xl p-8 border shadow-xl transition-all duration-300 ${isDark ? 'bg-[#0f172a] border-slate-800' : 'bg-white border-gray-100'}`}>
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                    <div className="bg-purple-600/10 p-2.5 rounded-2xl">
                        <Calendar className="w-6 h-6 text-purple-500" />
                    </div>
                    <div>
                        <h3 className="text-xl font-black">📅 Market Context</h3>
                        <p className="text-[10px] opacity-50 font-black uppercase tracking-widest">Event Sync Engine</p>
                    </div>
                </div>
                {hasData && (
                    <div className="px-2 py-1 rounded bg-purple-500/10 text-purple-500 text-[10px] font-black animate-pulse">
                        LIVE
                    </div>
                )}
            </div>

            <div className="space-y-4">
                {hasData ? (
                    <>
                        {/* Earnings */}
                        <div className={`p-4 rounded-2xl border ${isDark ? 'bg-slate-900/50 border-slate-800' : 'bg-gray-50 border-gray-100'} flex items-center justify-between`}>
                            <div className="flex items-center gap-3">
                                <Clock className="w-4 h-4 text-slate-500" />
                                <span className="text-xs font-bold opacity-60">Earnings Date</span>
                            </div>
                            <span className="text-xs font-black">{stockEvents.earnings_date || 'N/A'}</span>
                        </div>

                        {/* Sector */}
                        <div className={`p-4 rounded-2xl border ${isDark ? 'bg-slate-900/50 border-slate-800' : 'bg-gray-50 border-gray-100'} flex items-center justify-between`}>
                            <div className="flex items-center gap-3">
                                <Globe className="w-4 h-4 text-slate-500" />
                                <span className="text-xs font-bold opacity-60">Market Sector</span>
                            </div>
                            <span className="text-xs font-black">{stockEvents.sector || 'N/A'}</span>
                        </div>

                        {/* Risk / Volatility (Mock for now or extract from events) */}
                        <div className={`p-4 rounded-2xl border ${isDark ? 'bg-slate-900/50 border-slate-800' : 'bg-gray-50 border-gray-100'} flex items-center justify-between`}>
                            <div className="flex items-center gap-3">
                                <AlertCircle className="w-4 h-4 text-slate-500" />
                                <span className="text-xs font-bold opacity-60">Impending Risk</span>
                            </div>
                            <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${isDark ? 'bg-emerald-500/20 text-emerald-400' : 'bg-emerald-100 text-emerald-700'}`}>LOW VOLATILITY</span>
                        </div>
                    </>
                ) : (
                    <div className="py-10 text-center space-y-3 opacity-30">
                        <Clock size={32} className="mx-auto" />
                        <p className="text-xs font-bold italic uppercase tracking-widest">No scheduled events for this asset</p>
                    </div>
                )}
            </div>

            <div className="mt-8 pt-6 border-t border-slate-800/50">
                <p className="text-[10px] font-medium opacity-40 leading-relaxed italic">
                    AI-driven context extraction from global news streams and official financial filings.
                </p>
            </div>
        </div>
    );
};

export default CalendarWidget;
