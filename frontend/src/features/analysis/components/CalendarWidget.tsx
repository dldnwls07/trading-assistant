import React from 'react';
import { motion } from 'framer-motion';
import { CalendarDays, Globe, Info } from 'lucide-react';
import { AnalysisResult } from '../../../types/api';

interface CalendarWidgetProps {
    analysis: AnalysisResult | null;
    isDark: boolean;
}

const CalendarWidget: React.FC<CalendarWidgetProps> = ({ analysis, isDark }) => {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            className="p-6 rounded-xl border bg-white/5 backdrop-blur-md border-white/10 shadow-xl relative overflow-hidden group"
        >
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                    <div className="bg-white/5 p-2 rounded-lg border border-white/10">
                        <CalendarDays className="w-5 h-5 text-zinc-500" />
                    </div>
                    <h3 className="text-sm font-bold tracking-widest uppercase font-mono text-zinc-100">MARKET_CONTEXT</h3>
                </div>
                <div className="text-[9px] font-bold text-zinc-700 uppercase tracking-widest font-mono">LIVE_FEED</div>
            </div>

            <div className="space-y-6 relative">
                {/* Vertical Timeline Line */}
                <div className="absolute left-1.5 top-2 bottom-2 w-px bg-white/5"></div>

                {/* Earnings Context */}
                <div className="relative pl-7 group/item">
                    <div className="absolute left-1 top-1.5 w-1.5 h-1.5 rounded-full bg-yellow-400 shadow-[0_0_8px_rgba(250,204,21,0.5)] z-10 transition-transform group-hover/item:scale-125"></div>
                    <p className="text-[8px] font-bold text-yellow-400/50 uppercase tracking-widest mb-1 font-mono">EARNINGS</p>
                    <p className="text-xs font-bold tracking-tight mb-1 uppercase font-mono text-zinc-200">
                        {analysis?.events?.earnings || "AWAITING_SCHEDULE"}
                    </p>
                    <p className="text-[10px] font-medium text-zinc-500 leading-relaxed font-mono">
                        Quarterly volatility mapping for {analysis?.ticker || "ASSET"}.
                    </p>
                </div>

                {/* Sector Context */}
                <div className="relative pl-7 group/item">
                    <div className="absolute left-1 top-1.5 w-1.5 h-1.5 rounded-full bg-white/20 z-10 transition-transform group-hover/item:scale-125"></div>
                    <p className="text-[8px] font-bold text-zinc-600 uppercase tracking-widest mb-1 font-mono">SECTOR_FLOW</p>
                    <p className="text-xs font-bold tracking-tight mb-1 uppercase font-mono text-zinc-400">
                        {analysis?.events?.sector || "MAPPING_CORRELATIONS..."}
                    </p>
                    <p className="text-[10px] font-medium text-zinc-600 leading-relaxed font-mono">
                        Sector-alpha harmonics and flow matrix updates.
                    </p>
                </div>
            </div>

            <div className="mt-8 pt-5 border-t border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Info size={10} className="text-zinc-700" />
                    <span className="text-[8px] font-bold text-zinc-800 uppercase tracking-widest font-mono">STITCH_V1.7_CORE</span>
                </div>
                <div className="w-1.5 h-1.5 rounded-full animate-pulse bg-emerald-500/20"></div>
            </div>
        </motion.div>
    );
};

export default CalendarWidget;
