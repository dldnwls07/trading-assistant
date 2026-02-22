import { motion, AnimatePresence } from 'framer-motion';
import {
    Calendar as CalendarIcon,
    CalendarDays,
    History as HistoryIcon,
    Search,
    Filter,
    ChevronRight,
    Globe,
    TrendingUp,
    TrendingDown,
    Info,
    Clock,
    Minus,
    BarChart3,
    ChevronDown,
    AlertCircle
} from 'lucide-react';
import { useTranslation } from '../utils/translations';
import CalendarDetailModal from '../features/calendar/components/CalendarDetailModal';
import { useCalendar } from '../features/calendar/hooks/useCalendar';

// Animation variants
const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.05, delayChildren: 0.1 } }
};

const itemVariants = {
    hidden: { y: 20, opacity: 0, scale: 0.98 },
    visible: { y: 0, opacity: 1, scale: 1, transition: { type: 'spring', stiffness: 300, damping: 24 } }
};

const StyledSelect = ({ label, value, options, onChange, icon: Icon }) => (
    <div className="flex flex-col gap-1.5 flex-1 min-w-[140px]">
        <label className="text-[10px] font-black uppercase tracking-widest text-zinc-500 ml-1 flex items-center gap-1.5">
            {Icon && <Icon className="w-3 h-3" />} {label}
        </label>
        <div className="relative group/select">
            <select
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="w-full appearance-none bg-white/5 border border-white/10 rounded-2xl px-5 py-3.5 text-sm font-bold text-zinc-100 outline-none focus:border-yellow-400 focus:ring-1 focus:ring-yellow-400 transition-all cursor-pointer group-hover/select:bg-white/10"
            >
                {options.map(opt => (
                    <option key={opt.value} value={opt.value} className="bg-[#18181b] text-zinc-100">
                        {opt.label}
                    </option>
                ))}
            </select>
            <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 pointer-events-none group-focus-within/select:text-yellow-400 transition-colors" />
        </div>
    </div>
);

const CalendarPage = ({ settings }) => {
    const t = useTranslation(settings);
    const {
        loading, fetchError,
        activeTab, setActiveTab,
        searchQuery, setSearchQuery,
        selectedCategory, setSelectedCategory,
        selectedImportance, setSelectedImportance,
        selectedEvent,
        isModalOpen, setIsModalOpen,
        filteredEvents, groupedEvents,
        fetchEvents, handleEventClick
    } = useCalendar();

    const getImportanceColor = (imp) => {
        switch (imp) {
            case 'critical': return 'bg-rose-500 shadow-[0_0_15px_rgba(244,63,94,0.4)]';
            case 'high': return 'bg-yellow-400 shadow-[0_0_15px_rgba(250,204,21,0.3)]';
            case 'medium': return 'bg-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.3)]';
            default: return 'bg-zinc-600';
        }
    };

    const getCategoryIcon = (cat) => {
        switch (cat) {
            case 'macro': return <Globe className="w-4 h-4" />;
            case 'stock': return <TrendingUp className="w-4 h-4" />;
            case 'inflation': return <TrendingDown className="w-4 h-4" />;
            case 'policy': return <Info className="w-4 h-4" />;
            case 'labor': return <Clock className="w-4 h-4 text-rose-400" />;
            case 'production': return <TrendingUp className="w-4 h-4 text-emerald-400" />;
            case 'realestate': return <Globe className="w-4 h-4 text-emerald-400/60" />;
            default: return <Minus className="w-4 h-4" />;
        }
    };

    const categories = [
        { value: 'all', label: '모든 카테고리' },
        { value: 'macro', label: '매크로' },
        { value: 'stock', label: '주식' },
        { value: 'inflation', label: '인플레이션' },
        { value: 'policy', label: '정책/금리' },
        { value: 'consumption', label: '소비' },
        { value: 'labor', label: '고용' },
        { value: 'production', label: '생산' },
        { value: 'realestate', label: '부동산' }
    ];

    const importances = [
        { value: 'all', label: '모든 중요도' },
        { value: 'critical', label: '매우 높음' },
        { value: 'high', label: '높음' },
        { value: 'medium', label: '보통' },
        { value: 'low', label: '낮음' }
    ];

    return (
        <div className="min-h-screen py-10 transition-all duration-500 bg-transparent text-foreground">
            <div className="max-w-6xl mx-auto px-4 space-y-12">
                {/* Header Section */}
                <header className="flex flex-col md:flex-row md:items-end justify-between gap-8 pl-1">
                    <div className="space-y-4">
                        <div className="flex items-center gap-5">
                            <div className="bg-yellow-400 p-4 rounded-[2rem] text-black shadow-[0_10px_30px_rgba(250,204,21,0.2)]">
                                <CalendarIcon className="w-10 h-10" />
                            </div>
                            <div>
                                <h1 className="text-5xl font-black tracking-tighter uppercase text-zinc-100 drop-shadow-sm">
                                    {t.cal_title || 'ECONOMIC CALENDAR'}
                                </h1>
                                <p className="text-zinc-500 font-black uppercase text-[10px] tracking-[0.4em] flex items-center gap-2 mt-2 opacity-60">
                                    <BarChart3 className="w-3.5 h-3.5 text-yellow-400" /> NEURAL_PRESET_SCENARIOS & AI_SIGNALS
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Tabs */}
                    <nav className="flex p-1.5 rounded-2xl bg-white/5 border border-white/10 shadow-inner">
                        {[
                            { id: 'upcoming', label: '차후 일정', icon: <CalendarDays className="w-4 h-4" /> },
                            { id: 'past', label: '히스토리', icon: <HistoryIcon className="w-4 h-4" /> }
                        ].map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center gap-2 px-8 py-3 rounded-xl text-sm font-black transition-all duration-300 ${activeTab === tab.id
                                    ? 'bg-yellow-400 text-black shadow-lg shadow-yellow-400/20'
                                    : 'text-zinc-500 opacity-60 hover:opacity-100 hover:bg-white/5'
                                    }`}
                            >
                                {tab.icon} {tab.label}
                            </button>
                        ))}
                    </nav>
                </header>

                {/* 에러/폴백 데이터 사용 중 알림 배너 */}
                {fetchError && (
                    <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center gap-3">
                        <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
                        <p className="text-xs font-bold text-amber-400/80">{fetchError}</p>
                    </div>
                )}

                {/* Main Filter Section */}
                <section className="p-8 rounded-[2.5rem] border bg-white/5 backdrop-blur-xl border-white/10 shadow-2xl space-y-8">
                    <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-end">
                        <div className="md:col-span-5 flex flex-col gap-1.5">
                            <label className="text-[10px] font-black uppercase tracking-widest text-zinc-500 ml-1 flex items-center gap-1.5">
                                <Search className="w-3 h-3" /> EVENT_SEARCH_NODE
                            </label>
                            <div className="relative group">
                                <Search className="absolute left-5 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-zinc-500 transition-colors group-focus-within:text-yellow-400" />
                                <input
                                    type="text"
                                    placeholder="지표명, 국가 또는 키워드 분석..."
                                    className="w-full pl-14 pr-6 py-4 rounded-2xl text-sm font-bold bg-white/5 border border-white/10 text-zinc-100 placeholder:text-zinc-600 outline-none focus:border-yellow-400 transition-all"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                />
                            </div>
                        </div>

                        <div className="md:col-span-3">
                            <StyledSelect
                                label="CATEGORY_FILTER"
                                value={selectedCategory}
                                options={categories}
                                onChange={setSelectedCategory}
                                icon={Filter}
                            />
                        </div>

                        <div className="md:col-span-3">
                            <StyledSelect
                                label="IMPORTANCE_THRESHOLD"
                                value={selectedImportance}
                                options={importances}
                                onChange={setSelectedImportance}
                                icon={TrendingUp}
                            />
                        </div>

                        <div className="md:col-span-1">
                            <button
                                onClick={fetchEvents}
                                className="w-full h-[52px] flex items-center justify-center bg-yellow-400 text-black rounded-2xl hover:bg-yellow-300 transition-all shadow-lg shadow-yellow-400/20 active:scale-95 group"
                            >
                                <BarChart3 className="w-6 h-6 group-hover:rotate-12 transition-transform" />
                            </button>
                        </div>
                    </div>
                </section>

                {/* Event Display Stack */}
                <motion.div variants={containerVariants} initial="hidden" animate="visible" className="space-y-12 pb-20">
                    {Object.entries(groupedEvents).length > 0 ? (
                        Object.entries(groupedEvents).map(([date, dateEvents]) => (
                            <div key={date} className="space-y-6">
                                <motion.div variants={itemVariants} className="sticky top-20 z-10 py-5 px-8 rounded-3xl backdrop-blur-2xl border bg-white/5 border-white/10 shadow-2xl flex items-center justify-between">
                                    <div className="flex items-center gap-4">
                                        <div className="w-1.5 h-8 bg-yellow-400 rounded-full shadow-[0_0_15px_rgba(250,204,21,0.5)]" />
                                        <h2 className="text-2xl font-black tracking-tight uppercase text-zinc-100 font-mono">
                                            {new Date(date).toLocaleDateString(t.locale || 'ko-KR', {
                                                weekday: 'long',
                                                year: 'numeric',
                                                month: 'long',
                                                day: 'numeric'
                                            })}
                                        </h2>
                                    </div>
                                    <div className="flex gap-2">
                                        <span className="text-[10px] font-black px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-yellow-400 uppercase tracking-widest">
                                            {dateEvents.length} SCENARIOS_DETECTED
                                        </span>
                                    </div>
                                </motion.div>

                                <div className="grid grid-cols-1 gap-4">
                                    {dateEvents.map((e, i) => (
                                        <motion.div
                                            variants={itemVariants}
                                            key={`${date}-${i}`}
                                            onClick={() => handleEventClick(e)}
                                            className="group relative p-8 rounded-[2.5rem] border cursor-pointer transition-all duration-500 bg-white/3 border-white/5 hover:bg-white/10 hover:border-yellow-400/30 hover:shadow-[0_20px_50px_rgba(0,0,0,0.5)]"
                                        >
                                            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-8">
                                                <div className="flex items-center gap-8 flex-1">
                                                    <div className={`w-3 h-3 rounded-full ${getImportanceColor(e.importance)}`} />
                                                    <div className="space-y-3 flex-1">
                                                        <div className="flex items-center gap-4">
                                                            <span className="px-4 py-1.5 rounded-xl text-[11px] font-black uppercase tracking-widest bg-yellow-400 text-black shadow-lg shadow-yellow-400/20">
                                                                {e.country}
                                                            </span>
                                                            <h3 className="text-2xl font-black tracking-tighter text-zinc-100 group-hover:text-yellow-400 transition-colors uppercase">
                                                                {e.title}
                                                            </h3>
                                                        </div>
                                                        <div className="flex items-center gap-6 text-[11px] font-black text-zinc-500 tracking-[0.2em] font-mono">
                                                            <span className="flex items-center gap-2 group-hover:text-zinc-300 transition-colors"><Clock className="w-4 h-4 text-yellow-400/50" /> {e.time}</span>
                                                            <span className="flex items-center gap-2 group-hover:text-zinc-300 transition-colors uppercase">{getCategoryIcon(e.category)} {e.category}</span>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="flex items-center justify-between lg:justify-end gap-12 lg:min-w-[450px]">
                                                    <div className="grid grid-cols-3 gap-12 text-center flex-1">
                                                        <div className="space-y-2">
                                                            <p className="text-[10px] font-black uppercase tracking-widest text-zinc-600 font-mono">PREV_INDEX</p>
                                                            <p className="font-mono text-lg font-bold text-zinc-400">{e.previous || '--'}</p>
                                                        </div>
                                                        <div className="space-y-2">
                                                            <p className="text-[10px] font-black uppercase tracking-widest text-yellow-500 font-mono opacity-60">AI_FORECAST</p>
                                                            <p className="font-mono text-lg font-black text-yellow-400">{e.forecast || '--'}</p>
                                                        </div>
                                                        <div className="space-y-2">
                                                            <p className="text-[10px] font-black uppercase tracking-widest text-zinc-600 font-mono">ACTUAL_DATA</p>
                                                            <p className={`font-mono text-lg font-black ${e.actual !== '-' ? 'text-emerald-400' : 'text-zinc-500'}`}>{e.actual || '--'}</p>
                                                        </div>
                                                    </div>
                                                    <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center group-hover:bg-yellow-400 transition-all duration-500 text-zinc-700 group-hover:text-black">
                                                        <ChevronRight className="w-6 h-6" />
                                                    </div>
                                                </div>
                                            </div>
                                        </motion.div>
                                    ))}
                                </div>
                            </div>
                        ))
                    ) : (
                        !loading && (
                            <div className="text-center py-40 rounded-[4rem] border-2 border-dashed bg-white/2 border-white/5 backdrop-blur-md">
                                <div className="w-24 h-24 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-8">
                                    <Info className="w-12 h-12 text-zinc-600" />
                                </div>
                                <h3 className="text-3xl font-black text-zinc-300 uppercase tracking-tighter mb-4">No match data detected</h3>
                                <p className="text-zinc-600 font-bold uppercase text-xs tracking-[0.3em]">Adjust your neural filters to view upcoming scenarios</p>
                            </div>
                        )
                    )}

                    {loading && (
                        <div className="flex flex-col items-center justify-center py-40 gap-8">
                            <div className="relative">
                                <div className="w-20 h-20 border-[6px] border-yellow-400/20 border-t-yellow-400 rounded-full animate-spin" />
                                <div className="absolute inset-0 w-20 h-20 border-[6px] border-transparent border-b-yellow-400/40 rounded-full animate-pulse" />
                            </div>
                            <div className="text-xs font-black text-yellow-400/40 animate-pulse tracking-[0.5em] uppercase font-mono">Syncing_Economic_Pulse...</div>
                        </div>
                    )}
                </motion.div>
            </div>

            <CalendarDetailModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                event={selectedEvent}
                isDark={true}
                t={t}
            />
        </div>
    );
};

export default CalendarPage;
