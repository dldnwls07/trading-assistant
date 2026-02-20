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
            label: 'ACCUMULATION_ZONE',
            value: entry_price,
            icon: Target,
            color: 'text-yellow-400',
            borderColor: 'border-yellow-400/20',
            bgColor: 'bg-yellow-400/5'
        },
        {
            label: 'LIQUIDATION_TARGET',
            value: take_profit,
            icon: BadgeInfo,
            color: 'text-emerald-400',
            borderColor: 'border-emerald-400/20',
            bgColor: 'bg-emerald-400/5'
        },
        {
            label: 'STOP_LOSS_GUARD',
            value: stop_loss,
            icon: ShieldAlert,
            color: 'text-rose-400',
            borderColor: 'border-rose-400/20',
            bgColor: 'bg-rose-400/5'
        }
    ];

    return (
        <div className="flex flex-col gap-6">
            {signals.map((sig, idx) => {
                const Icon = sig.icon;
                return (
                    <motion.div
                        key={sig.label}
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: idx * 0.05 }}
                        className={`p-6 rounded-xl border bg-white/5 backdrop-blur-md border-white/10 transition-colors duration-200 hover:bg-white/[0.08] ${sig.borderColor} relative overflow-hidden group shadow-xl`}
                    >
                        <div className="flex items-center justify-between mb-3 text-zinc-500">
                            <span className="text-[9px] font-bold uppercase tracking-widest font-mono">
                                {sig.label}
                            </span>
                            <div className={`p-2 rounded-xl bg-white/5 border border-white/10`}>
                                <Icon size={14} className={sig.color} />
                            </div>
                        </div>
                        <div className="flex items-baseline gap-2">
                            <span className={`text-4xl font-bold font-mono tracking-tighter ${sig.color}`}>
                                {typeof sig.value === 'number' ? sig.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 }) : (sig.value || '---')}
                            </span>
                            <span className="text-[9px] font-bold text-zinc-600 uppercase tracking-widest font-mono">USD</span>
                        </div>
                    </motion.div>
                );
            })}
        </div>
    );
};

export default StrategicSignals;
