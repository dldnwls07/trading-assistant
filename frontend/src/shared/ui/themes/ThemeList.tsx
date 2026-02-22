import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ThemeCard } from './ThemeCard';
import { MOCK_THEMES } from '../../../data/themes';
import { InvestmentTheme } from '../../../types';
import { LayoutGrid, TrendingUp, Filter } from 'lucide-react';

interface ThemeListProps {
    onThemeSelect?: (theme: InvestmentTheme) => void;
}

// 테마 카테고리 필터 옵션
const FILTER_OPTIONS = [
    { label: '전체', value: 'all' },
    { label: 'Tech', value: 'tech' },
    { label: 'Energy', value: 'energy' },
    { label: 'Finance', value: 'finance' },
    { label: 'Defense', value: 'defense' },
    { label: 'Healthcare', value: 'healthcare' },
];

// tags 기반 필터링 매핑
const FILTER_MAP: Record<string, string[]> = {
    tech: ['Tech', 'AI', 'Cloud', 'SaaS', 'Robotics', 'Auto', 'Deep Tech', 'Security'],
    energy: ['Energy', 'ESG', 'Green', 'EV', 'Cyclical'],
    finance: ['Fintech', 'Payments', 'Crypto'],
    defense: ['Defense', 'Geopolitics'],
    healthcare: ['Bio', 'Pharma'],
};

const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.07, delayChildren: 0.05 } }
};

const itemVariants = {
    hidden: { y: 20, opacity: 0, scale: 0.97 },
    visible: { y: 0, opacity: 1, scale: 1, transition: { type: 'spring' as const, stiffness: 260, damping: 22 } }
};

export const ThemeList: React.FC<ThemeListProps> = ({ onThemeSelect }) => {
    const [activeFilter, setActiveFilter] = useState('all');

    // 모멘텀 기준 정렬 + 필터
    const filteredThemes = MOCK_THEMES
        .filter(t => {
            if (activeFilter === 'all') return true;
            const filterTags = FILTER_MAP[activeFilter] || [];
            return t.tags.some(tag => filterTags.some(ft => tag.toLowerCase().includes(ft.toLowerCase())));
        })
        .sort((a, b) => b.momentumScore - a.momentumScore);

    // 상위 모멘텀 지표 계산
    const avgMomentum = Math.round(filteredThemes.reduce((s, t) => s + t.momentumScore, 0) / (filteredThemes.length || 1));
    const topPerformer = filteredThemes.reduce((best, t) => t.avgPerformance > best.avgPerformance ? t : best, filteredThemes[0]);

    return (
        <div className="space-y-6 pb-6">
            {/* 헤더 영역 */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 px-1">
                <div className="space-y-1">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-yellow-400 rounded-xl text-black">
                            <LayoutGrid className="w-5 h-5" />
                        </div>
                        <h2 className="text-2xl font-black tracking-tighter text-zinc-100 uppercase">
                            투자 테마 <span className="text-yellow-400">레이더</span>
                        </h2>
                    </div>
                    <p className="text-[10px] text-zinc-500 font-mono uppercase tracking-widest ml-1">
                        {filteredThemes.length} Themes Active · Avg Momentum {avgMomentum} · Top: {topPerformer?.name}
                    </p>
                </div>

                {/* 요약 배지 */}
                <div className="flex gap-3">
                    <div className="px-4 py-2 rounded-xl bg-yellow-400/10 border border-yellow-400/20 text-center">
                        <p className="text-[9px] text-yellow-400/60 font-mono uppercase tracking-widest">테마 수</p>
                        <p className="text-xl font-black text-yellow-400 font-mono">{MOCK_THEMES.length}</p>
                    </div>
                    <div className="px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-center">
                        <p className="text-[9px] text-zinc-500 font-mono uppercase tracking-widest">ETF 포함</p>
                        <p className="text-xl font-black text-zinc-100 font-mono">
                            {MOCK_THEMES.filter(t => t.recommendedEtfs?.length).length}
                        </p>
                    </div>
                </div>
            </div>

            {/* 필터 탭 */}
            <div className="flex gap-2 flex-wrap px-1">
                <div className="flex items-center gap-1.5 text-[10px] text-zinc-600 font-mono mr-1">
                    <Filter className="w-3 h-3" /> FILTER
                </div>
                {FILTER_OPTIONS.map(opt => (
                    <button
                        key={opt.value}
                        onClick={() => setActiveFilter(opt.value)}
                        className={`px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-wider transition-all ${activeFilter === opt.value
                            ? 'bg-yellow-400 text-black shadow-sm shadow-yellow-400/20'
                            : 'bg-white/5 text-zinc-500 hover:bg-white/10 hover:text-zinc-200 border border-white/10'
                            }`}
                    >
                        {opt.label}
                    </button>
                ))}
            </div>

            {/* 그리드 */}
            <motion.div
                key={activeFilter}
                variants={containerVariants}
                initial="hidden"
                animate="visible"
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
            >
                {filteredThemes.map(theme => (
                    <motion.div key={theme.id} variants={itemVariants}>
                        <ThemeCard
                            theme={theme}
                            onClick={onThemeSelect}
                        />
                    </motion.div>
                ))}
            </motion.div>

            {/* 빈 상태 */}
            {filteredThemes.length === 0 && (
                <div className="text-center py-20 text-zinc-600">
                    <TrendingUp className="w-10 h-10 mx-auto mb-3 opacity-30" />
                    <p className="text-sm font-bold uppercase tracking-widest">해당 카테고리 테마 없음</p>
                </div>
            )}
        </div>
    );
};
