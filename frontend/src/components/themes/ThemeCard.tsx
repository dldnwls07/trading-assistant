import React from 'react';
import { motion } from 'framer-motion';
import { Activity, BatteryCharging, Cpu, Rocket, TrendingUp } from 'lucide-react';
import { InvestmentTheme } from '../../types';

interface ThemeCardProps {
    theme: InvestmentTheme;
    onClick?: (theme: InvestmentTheme) => void;
}

const getIcon = (iconName: string) => {
    switch (iconName) {
        case 'cpu': return <Cpu className="w-6 h-6 text-cyan-400" />;
        case 'battery-charging': return <BatteryCharging className="w-6 h-6 text-green-400" />;
        case 'rocket': return <Rocket className="w-6 h-6 text-orange-400" />;
        case 'activity': return <Activity className="w-6 h-6 text-pink-400" />;
        default: return <TrendingUp className="w-6 h-6 text-blue-400" />;
    }
};

export const ThemeCard: React.FC<ThemeCardProps> = ({ theme, onClick }) => {
    return (
        <motion.div
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            className="bg-[#1e293b] rounded-xl p-5 border border-slate-700/50 hover:border-blue-500/50 cursor-pointer shadow-lg hover:shadow-blue-500/10 transition-all group"
            onClick={() => onClick?.(theme)}
        >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
                <div className="p-3 bg-slate-800/50 rounded-lg group-hover:bg-slate-700/50 transition-colors">
                    {getIcon(theme.icon)}
                </div>
                <div className="text-right">
                    <span className={`text-sm font-bold ${theme.avgPerformance >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {theme.avgPerformance >= 0 ? '+' : ''}{theme.avgPerformance}%
                    </span>
                    <p className="text-xs text-slate-500">Avg. Return</p>
                </div>
            </div>

            {/* Content */}
            <h3 className="text-lg font-bold text-slate-100 mb-2 group-hover:text-blue-400 transition-colors">
                {theme.name}
            </h3>
            <p className="text-sm text-slate-400 line-clamp-2 mb-4 min-h-[40px]">
                {theme.description}
            </p>

            {/* Momentum Bar */}
            <div className="mb-4">
                <div className="flex justify-between text-xs text-slate-400 mb-1">
                    <span>Momentum Score</span>
                    <span className="text-slate-200">{theme.momentumScore}</span>
                </div>
                <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${theme.momentumScore}%` }}
                        transition={{ duration: 1, ease: 'easeOut' }}
                        className={`h-full rounded-full ${theme.momentumScore > 80 ? 'bg-gradient-to-r from-blue-500 to-cyan-400' :
                                theme.momentumScore > 50 ? 'bg-gradient-to-r from-blue-600 to-blue-400' :
                                    'bg-slate-500'
                            }`}
                    />
                </div>
            </div>

            {/* Tags & Tickers */}
            <div className="flex items-center justify-between mt-auto pt-4 border-t border-slate-700/50">
                <div className="flex gap-1.5 flex-wrap">
                    {theme.tags.slice(0, 2).map(tag => (
                        <span key={tag} className="px-2 py-0.5 text-[10px] bg-slate-800 text-slate-300 rounded-full border border-slate-700">
                            #{tag}
                        </span>
                    ))}
                </div>
                <div className="text-xs text-slate-400 font-mono">
                    {theme.tickers.length} Assets
                </div>
            </div>
        </motion.div>
    );
};
