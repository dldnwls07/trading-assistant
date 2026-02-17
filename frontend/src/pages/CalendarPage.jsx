import React, { useState, useEffect, useMemo } from 'react';
import { Calendar as CalendarIcon, Clock, Globe, Info, Filter, TrendingUp, TrendingDown, Minus, Search, CalendarDays, History as HistoryIcon, BarChart3, ChevronRight } from 'lucide-react';
import { useTranslation } from '../utils/translations';
import api from '../utils/api';
import CalendarDetailModal from '../components/CalendarDetailModal';

const CalendarPage = ({ settings }) => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('upcoming');
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [selectedImportance, setSelectedImportance] = useState('all');
    const [selectedEvent, setSelectedEvent] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const isDark = settings?.darkMode;
    const t = useTranslation(settings);

    useEffect(() => {
        fetchEvents();
    }, []);

    const fetchEvents = async () => {
        setLoading(true);
        try {
            const res = await api.get('/api/calendar');
            setEvents(res.data.events || []);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const filteredEvents = useMemo(() => {
        const now = new Date();
        const startOfToday = new Date(now.setHours(0, 0, 0, 0));

        return events.filter(e => {
            const eDate = new Date(e.date);
            const matchesSearch = e.title.toLowerCase().includes(searchQuery.toLowerCase());
            // Filter by category if selected, otherwise show all
            const matchesCategory = selectedCategory && selectedCategory !== 'all'
                ? e.category === selectedCategory
                : true;
            // Filter by importance if selected, otherwise show all
            const matchesImportance = selectedImportance && selectedImportance !== 'all'
                ? e.importance === selectedImportance
                : true;

            const isUpcoming = eDate >= startOfToday;
            const matchesTab = activeTab === 'upcoming' ? isUpcoming : !isUpcoming;

            return matchesSearch && matchesCategory && matchesImportance && matchesTab;
        }).sort((a, b) => {
            // Sort ascending for upcoming, descending for past
            const dateA = new Date(`${a.date}T${a.time}`);
            const dateB = new Date(`${b.date}T${b.time}`);
            return activeTab === 'upcoming' ? dateA - dateB : dateB - dateA;
        });
    }, [events, searchQuery, selectedCategory, selectedImportance, activeTab]);

    // Group events by date for sticky headers
    const groupedEvents = useMemo(() => {
        return filteredEvents.reduce((acc, event) => {
            const date = event.date;
            if (!acc[date]) {
                acc[date] = [];
            }
            acc[date].push(event);
            return acc;
        }, {});
    }, [filteredEvents]);

    const getImportanceColor = (imp) => {
        switch (imp) {
            case 'critical': return 'bg-red-500 shadow-red-500/50';
            case 'high': return 'bg-orange-500 shadow-orange-500/50';
            case 'medium': return 'bg-yellow-500 shadow-yellow-500/50';
            default: return 'bg-slate-400';
        }
    };

    const getCategoryIcon = (cat) => {
        switch (cat) {
            case 'macro': return <Globe className="w-4 h-4" />;
            case 'stock': return <TrendingUp className="w-4 h-4" />;
            case 'inflation': return <TrendingDown className="w-4 h-4" />;
            case 'policy': return <Info className="w-4 h-4" />;
            case 'production': return <TrendingUp className="w-4 h-4 text-blue-400" />;
            case 'realestate': return <Globe className="w-4 h-4 text-emerald-400" />;
            default: return <Minus className="w-4 h-4" />;
        }
    };

    const categories = ['all', 'macro', 'stock', 'inflation', 'policy', 'consumption', 'labor', 'production', 'realestate'];
    const importances = ['all', 'critical', 'high', 'medium', 'low'];

    const handleEventClick = (event) => {
        setSelectedEvent(event);
        setIsModalOpen(true);
    };

    return (
        <div className={`min-h-screen py-10 transition-all duration-500 ${isDark ? 'bg-slate-950 text-slate-100' : 'bg-gray-50 text-gray-900'}`}>
            <div className="max-w-6xl mx-auto px-4 space-y-10">
                {/* Header Section */}
                <header className="flex flex-col md:flex-row md:items-end justify-between gap-8 border-l-4 border-blue-600 pl-8">
                    <div className="space-y-2">
                        <div className="flex items-center gap-3">
                            <div className="bg-blue-600 p-3 rounded-2xl text-white shadow-2xl shadow-blue-600/30">
                                <CalendarIcon className="w-8 h-8" />
                            </div>
                            <h1 className="text-4xl font-black tracking-tighter uppercase whitespace-nowrap">
                                {t.cal_title || 'Economic Calendar'}
                            </h1>
                        </div>
                        <p className="text-slate-500 font-bold uppercase text-xs tracking-widest flex items-center gap-2">
                            <BarChart3 className="w-4 h-4" /> Market-Moving Data & AI Impact Analysis
                        </p>
                    </div>

                    {/* Tabs */}
                    <nav className={`flex p-1.5 rounded-2xl ${isDark ? 'bg-slate-900' : 'bg-slate-200/50'}`}>
                        {[
                            { id: 'upcoming', label: '차후 일정', icon: <CalendarDays className="w-4 h-4" /> },
                            { id: 'past', label: '히스토리', icon: <HistoryIcon className="w-4 h-4" /> }
                        ].map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-black transition-all duration-300 ${activeTab === tab.id
                                    ? 'bg-white text-blue-600 shadow-xl shadow-blue-600/10'
                                    : 'opacity-40 hover:opacity-100'
                                    }`}
                            >
                                {tab.icon} {tab.label}
                            </button>
                        ))}
                    </nav>
                </header>

                {/* Filter Bar */}
                <div className={`grid grid-cols-1 md:grid-cols-4 gap-4 p-6 rounded-3xl border ${isDark ? 'bg-slate-900/40 border-slate-800' : 'bg-white border-slate-200'}`}>
                    <div className="relative group">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 opacity-40 group-focus-within:text-blue-500 transition-colors" />
                        <input
                            type="text"
                            placeholder="이벤트 검색..."
                            className={`w-full pl-11 pr-4 py-3 rounded-2xl text-sm font-bold border outline-none transition-all ${isDark ? 'bg-slate-950 border-slate-800 focus:border-blue-600' : 'bg-slate-50 border-slate-200 focus:border-blue-500'
                                }`}
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>

                    <div className="flex items-center gap-2">
                        <Filter className="w-4 h-4 opacity-40 ml-2" />
                        <select
                            className={`flex-1 p-3 rounded-2xl text-sm font-bold border outline-none appearance-none cursor-pointer ${isDark ? 'bg-slate-950 border-slate-800' : 'bg-slate-50 border-slate-200'
                                }`}
                            value={selectedCategory}
                            onChange={(e) => setSelectedCategory(e.target.value)}
                        >
                            {categories.map(c => <option key={c} value={c}>Category: {c.toUpperCase()}</option>)}
                        </select>
                    </div>

                    <div className="flex items-center gap-2 md:col-span-2">
                        <select
                            className={`flex-1 p-3 rounded-2xl text-sm font-bold border outline-none appearance-none cursor-pointer ${isDark ? 'bg-slate-950 border-slate-800' : 'bg-slate-50 border-slate-200'
                                }`}
                            value={selectedImportance}
                            onChange={(e) => setSelectedImportance(e.target.value)}
                        >
                            {importances.map(i => <option key={i} value={i}>Importance: {i.toUpperCase()}</option>)}
                        </select>
                        <button className="bg-blue-600 text-white p-3 rounded-2xl hover:bg-blue-700 transition-colors shadow-lg shadow-blue-600/20">
                            <BarChart3 className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Event List (Grouped by Date) */}
                <div className="space-y-8">
                    {Object.keys(groupedEvents).length > 0 ? (
                        Object.entries(groupedEvents).map(([date, dateEvents]) => (
                            <div key={date} className="space-y-4">
                                {/* Sticky Date Header */}
                                <div className={`sticky top-0 z-10 py-3 px-4 rounded-xl backdrop-blur-md border ${isDark ? 'bg-slate-900/80 border-slate-700 text-blue-400' : 'bg-white/80 border-blue-100 text-blue-600'
                                    } shadow-lg flex items-center gap-3`}>
                                    <CalendarDays className="w-5 h-5" />
                                    <h2 className="text-lg font-black tracking-tight uppercase">
                                        {new Date(date).toLocaleDateString(t.locale || 'ko-KR', {
                                            weekday: 'long',
                                            year: 'numeric',
                                            month: 'long',
                                            day: 'numeric'
                                        })}
                                    </h2>
                                    <span className="text-xs font-bold opacity-50 ml-auto bg-slate-500/10 px-2 py-1 rounded">
                                        {dateEvents.length} Events
                                    </span>
                                </div>

                                <div className="space-y-3">
                                    {dateEvents.map((e, i) => (
                                        <div
                                            key={`${date}-${i}`}
                                            onClick={() => handleEventClick(e)}
                                            className={`group relative p-5 rounded-3xl border cursor-pointer transition-all duration-300 hover:scale-[1.01] hover:shadow-2xl active:scale-[0.99] ${isDark ? 'bg-slate-900 border-slate-800 hover:bg-slate-800/80 hover:border-slate-700' : 'bg-white border-slate-200 hover:border-blue-200'
                                                }`}
                                        >
                                            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                                                <div className="flex items-center gap-5">
                                                    <div className={`w-3.5 h-3.5 rounded-full animate-pulse ${getImportanceColor(e.importance)}`} />
                                                    <div className="space-y-1.5">
                                                        <div className="flex items-center gap-2.5">
                                                            <span className={`px-2.5 py-0.5 rounded-lg text-[10px] font-black uppercase tracking-widest ${isDark ? 'bg-slate-950 text-slate-400' : 'bg-slate-100 text-slate-500'
                                                                }`}>
                                                                {e.country}
                                                            </span>
                                                            <h3 className="text-lg font-black tracking-tight group-hover:text-blue-500 transition-colors uppercase">{e.title}</h3>
                                                        </div>
                                                        <div className="flex items-center gap-4 text-xs font-bold opacity-40 tracking-wider">
                                                            {/* Date removed from here since it's in header */}
                                                            <span className="flex items-center gap-1.5"><Clock className="w-4 h-4" /> {e.time}</span>
                                                            <span className="flex items-center gap-1.5 capitalize">{getCategoryIcon(e.category)} {e.category}</span>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="flex items-center justify-between md:justify-end gap-10">
                                                    <div className="grid grid-cols-3 gap-8 text-center min-w-[200px]">
                                                        <div className="space-y-0.5">
                                                            <p className="text-[10px] font-black uppercase opacity-30 tracking-widest">Prev</p>
                                                            <p className="font-mono text-base font-bold">{e.previous || '--'}</p>
                                                        </div>
                                                        <div className="space-y-0.5">
                                                            <p className="text-[10px] font-black uppercase opacity-30 text-blue-500 tracking-widest">Fore</p>
                                                            <p className="font-mono text-base font-black text-blue-600">{e.forecast || '--'}</p>
                                                        </div>
                                                        <div className="space-y-0.5">
                                                            <p className="text-[10px] font-black uppercase opacity-30 tracking-widest">Act</p>
                                                            <p className={`font-mono text-base font-black ${e.actual !== '-' ? 'text-green-500' : ''}`}>{e.actual || '--'}</p>
                                                        </div>
                                                    </div>
                                                    <ChevronRight className="hidden md:block w-6 h-6 opacity-0 group-hover:opacity-100 group-hover:translate-x-2 transition-all text-blue-600" />
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))
                    ) : (
                        !loading && (
                            <div className={`text-center py-32 rounded-[3rem] border-4 border-dashed ${isDark ? 'bg-slate-900/20 border-slate-800/40' : 'bg-slate-50 border-slate-200'}`}>
                                <Info className="w-16 h-16 mx-auto mb-6 opacity-20 text-blue-600" />
                                <p className="text-2xl font-black opacity-30 uppercase tracking-tighter">No events found matching current criteria</p>
                            </div>
                        )
                    )}

                    {loading && (
                        <div className="flex flex-col items-center justify-center py-32 gap-6 scale-125">
                            <div className="w-16 s:w-20 h-16 s:h-20 border-8 border-blue-600 border-t-transparent rounded-full animate-spin" />
                            <div className="text-sm font-black opacity-30 animate-pulse tracking-[0.3em] uppercase">Quant Oracle Syncing...</div>
                        </div>
                    )}
                </div>
            </div>

            <CalendarDetailModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                event={selectedEvent}
                isDark={isDark}
                t={t}
            />
        </div>
    );
};

export default CalendarPage;
