import React from 'react';
import { motion } from 'framer-motion';
import { Target, ShieldAlert, BadgeInfo } from 'lucide-react';
import { AnalysisResult } from '../../types/api';

interface StrategicSignalsProps {
    analysis: AnalysisResult | null;
    isDark: boolean;
}

const StrategicSignals: React.FC<StrategicSignalsProps> = ({ analysis, isDark }) => {
    if (!analysis?.entry_points) return null;

    const { entry_price, take_profit, stop_loss } = analysis.entry_points;

    const signals = [
        {
            label: 'Accumulation Zone',
            value: entry_price,
            icon: Target,
            color: 'text-rose-500',
            borderColor: 'border-rose-500/20',
            bgColor: 'bg-rose-500/5'
        },
        {
            label: 'Liquidation Target',
            value: take_profit,
            icon: BadgeInfo,
            color: 'text-cyan-500',
            borderColor: 'border-cyan-500/20',
            bgColor: 'bg-cyan-500/5'
        },
        {
            label: 'Stop Loss Guard',
            value: stop_loss,
            icon: ShieldAlert,
            color: 'text-blue-500',
            borderColor: 'border-blue-500/20',
            bgColor: 'bg-blue-500/5'
        }
    ];

    return (
        <div className="grid grid-cols-1 gap-4">
            {signals.map((sig, idx) => {
                const Icon = sig.icon;
                return (
                    <motion.div
                        key={sig.label}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className={`p-6 rounded-[1.5rem] border ${sig.borderColor} ${isDark ? 'bg-slate-900/60' : 'bg-white shadow-sm'} flex flex-col gap-1 transition-all hover:scale-[1.02]`}
                    >
                        <div className="flex items-center justify-between mb-1">
                            <span className="text-[10px] font-black uppercase tracking-widest opacity-60">
                                {sig.label}
                            </span>
                            <Icon size={14} className={sig.color} />
                        </div>
                        <span className="text-2xl font-black font-mono tracking-tighter">
                            {typeof sig.value === 'number' ? sig.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : (sig.value || '---')}
                        </span>
                    </motion.div>
                );
            })}
        </div>
    );
};

export default StrategicSignals;
