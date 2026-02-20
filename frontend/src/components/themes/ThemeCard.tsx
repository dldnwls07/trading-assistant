import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Activity, BatteryCharging, Cpu, Rocket, TrendingUp, TrendingDown,
    Cloud, Zap, ShoppingBag, Server, BarChart3, Shield, ChevronDown,
    ExternalLink
} from 'lucide-react';
import { InvestmentTheme } from '../../types';

interface ThemeCardProps {
    theme: InvestmentTheme;
    onClick?: (theme: InvestmentTheme) => void;
}

// 아이콘 이름 → 컴포넌트 매핑 (신규 테마들 아이콘 포함)
const getIcon = (iconName: string) => {
    switch (iconName) {
        case 'cpu': return <Cpu className="w-5 h-5 text-cyan-400" />;
        case 'battery-charging': return <BatteryCharging className="w-5 h-5 text-green-400" />;
        case 'rocket': return <Rocket className="w-5 h-5 text-orange-400" />;
        case 'activity': return <Activity className="w-5 h-5 text-pink-400" />;
        case 'cloud': return <Cloud className="w-5 h-5 text-blue-400" />;
        case 'zap': return <Zap className="w-5 h-5 text-emerald-400" />;
        case 'trending-up': return <TrendingUp className="w-5 h-5 text-purple-400" />;
        case 'trending-down': return <TrendingDown className="w-5 h-5 text-rose-400" />;
        case 'shield': return <Shield className="w-5 h-5 text-indigo-400" />;
        case 'server': return <Server className="w-5 h-5 text-sky-400" />;
        case 'bar-chart': return <BarChart3 className="w-5 h-5 text-amber-400" />;
        case 'shopping-bag': return <ShoppingBag className="w-5 h-5 text-rose-300" />;
        default: return <TrendingUp className="w-5 h-5 text-yellow-400" />;
    }
};

// 모멘텀 점수에 따른 색상 그라디언트
const getMomentumColor = (score: number) => {
    if (score >= 80) return 'from-yellow-400 to-orange-400';
    if (score >= 60) return 'from-emerald-400 to-cyan-400';
    if (score >= 40) return 'from-blue-400 to-indigo-400';
    return 'from-zinc-600 to-zinc-500';
};

// 수익률 색상
const getPerfColor = (n: number) => {
    if (n > 0) return 'text-emerald-400';
    if (n < 0) return 'text-rose-400';
    return 'text-zinc-400';
};

export const ThemeCard: React.FC<ThemeCardProps> = ({ theme, onClick }) => {
    const [etfOpen, setEtfOpen] = useState(false);

    const handleMainClick = () => {
        onClick?.(theme);
    };

    return (
        <motion.div
            whileHover={{ scale: 1.015, y: -3 }}
            whileTap={{ scale: 0.98 }}
            className="relative bg-white/[0.03] backdrop-blur-md rounded-2xl border border-white/10
                       hover:border-yellow-400/40 shadow-lg hover:shadow-yellow-400/10 transition-all
                       group overflow-hidden flex flex-col"
        >
            {/* 상단 글로우 라인 */}
            <div className="absolute top-0 inset-x-0 h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent" />

            {/* 메인 콘텐츠 영역 */}
            <div className="p-5 flex flex-col gap-3 flex-1">
                {/* 헤더: 아이콘 + 수익률 */}
                <div className="flex items-start justify-between">
                    <div className="p-2.5 bg-white/5 rounded-xl border border-white/10 group-hover:bg-white/10 transition-colors">
                        {getIcon(theme.icon)}
                    </div>
                    <div className="text-right">
                        <span className={`text-base font-black font-mono ${getPerfColor(theme.avgPerformance)}`}>
                            {theme.avgPerformance >= 0 ? '+' : ''}{theme.avgPerformance}%
                        </span>
                        <p className="text-[9px] text-zinc-600 uppercase tracking-widest font-mono">Avg. Return</p>
                    </div>
                </div>

                {/* 테마명 + 설명 */}
                <div>
                    <h3 className="text-sm font-black text-zinc-100 mb-1 group-hover:text-yellow-400 transition-colors leading-tight">
                        {theme.name}
                    </h3>
                    <p className="text-[11px] text-zinc-500 line-clamp-2 leading-relaxed min-h-[30px]">
                        {theme.description}
                    </p>
                </div>

                {/* 모멘텀 바 */}
                <div>
                    <div className="flex justify-between text-[9px] text-zinc-500 mb-1.5 font-mono">
                        <span>MOMENTUM</span>
                        <span className="text-zinc-300 font-black">{theme.momentumScore}</span>
                    </div>
                    <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${theme.momentumScore}%` }}
                            transition={{ duration: 1, ease: 'easeOut', delay: 0.1 }}
                            className={`h-full rounded-full bg-gradient-to-r ${getMomentumColor(theme.momentumScore)}`}
                        />
                    </div>
                </div>

                {/* 대표 티커 배지 */}
                <div className="flex flex-wrap gap-1.5">
                    {theme.tickers.slice(0, 4).map(t => (
                        <span
                            key={t}
                            className="px-2 py-0.5 text-[9px] font-mono font-black bg-white/5 text-zinc-400 rounded-lg border border-white/10"
                        >
                            {t}
                        </span>
                    ))}
                    {theme.tickers.length > 4 && (
                        <span className="px-2 py-0.5 text-[9px] font-mono bg-white/5 text-zinc-600 rounded-lg border border-white/10">
                            +{theme.tickers.length - 4}
                        </span>
                    )}
                </div>

                {/* 태그 */}
                <div className="flex gap-1.5 flex-wrap">
                    {theme.tags.slice(0, 3).map(tag => (
                        <span key={tag} className="px-2 py-0.5 text-[9px] bg-yellow-400/5 text-yellow-400/80 rounded-full border border-yellow-400/10 font-black tracking-wider">
                            #{tag}
                        </span>
                    ))}
                </div>
            </div>

            {/* 하단 버튼 라인 */}
            <div className="px-5 pb-4 flex gap-2 mt-auto">
                {/* AI 분석 버튼 */}
                <button
                    onClick={handleMainClick}
                    className="flex-1 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest
                               bg-yellow-400/10 text-yellow-400 hover:bg-yellow-400 hover:text-black
                               transition-all flex items-center justify-center gap-1.5 border border-yellow-400/20 hover:border-yellow-400"
                >
                    AI 분석 <ExternalLink className="w-3 h-3" />
                </button>

                {/* ETF 추천 토글 버튼 (데이터 있는 경우만) */}
                {theme.recommendedEtfs && theme.recommendedEtfs.length > 0 && (
                    <button
                        onClick={() => setEtfOpen(prev => !prev)}
                        className="px-3 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest
                                   bg-white/5 text-zinc-400 hover:bg-white/10 hover:text-zinc-100
                                   transition-all border border-white/10 flex items-center gap-1"
                        title="ETF 추천 보기"
                    >
                        ETF
                        <motion.div animate={{ rotate: etfOpen ? 180 : 0 }} transition={{ duration: 0.2 }}>
                            <ChevronDown className="w-3 h-3" />
                        </motion.div>
                    </button>
                )}
            </div>

            {/* ETF 추천 펼침 패널 */}
            <AnimatePresence>
                {etfOpen && theme.recommendedEtfs && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.25, ease: 'easeInOut' }}
                        className="overflow-hidden"
                    >
                        <div className="px-5 pb-4 border-t border-white/5 pt-3 space-y-2 bg-white/[0.02]">
                            <p className="text-[9px] font-black text-yellow-400/60 uppercase tracking-[0.3em] font-mono mb-2">
                                📦 추천 ETF
                            </p>
                            {theme.recommendedEtfs.map(etf => (
                                <div key={etf.ticker} className="flex items-center gap-3 py-2 px-3 rounded-xl bg-white/5 border border-white/10 hover:border-yellow-400/20 transition-colors">
                                    <span className="font-mono font-black text-[11px] text-yellow-400 min-w-[48px]">
                                        {etf.ticker}
                                    </span>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-[10px] font-bold text-zinc-300 truncate">{etf.name}</p>
                                        <p className="text-[9px] text-zinc-600 truncate">{etf.description}</p>
                                    </div>
                                    <a
                                        href={`https://finance.yahoo.com/quote/${etf.ticker}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        onClick={e => e.stopPropagation()}
                                        className="p-1 rounded-lg text-zinc-600 hover:text-zinc-100 transition-colors"
                                    >
                                        <ExternalLink className="w-3 h-3" />
                                    </a>
                                </div>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};
