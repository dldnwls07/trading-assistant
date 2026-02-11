import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Calendar as CalendarIcon, ChevronDown, ChevronUp, Star } from 'lucide-react';
import { useTranslation } from '../utils/translations';

const API_BASE = 'http://127.0.0.1:8000';

const CalendarPage = ({ settings }) => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all'); // all, high, medium, low
    const [countryFilter, setCountryFilter] = useState('all');
    const [typeFilter, setTypeFilter] = useState('all');
    const [expandedEvent, setExpandedEvent] = useState(null);

    const isDark = settings?.darkMode;
    const t = useTranslation(settings);
    const lang = settings?.language || 'ko';

    useEffect(() => {
        const fetchEvents = async () => {
            setLoading(true);
            try {
                const res = await axios.get(`${API_BASE}/api/calendar`, {
                    params: { lang: lang }
                });
                setEvents(res.data.events || []);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchEvents();
    }, [lang]); // Refetch when language changes

    const getImportanceColor = (impact) => {
        const imp = impact?.toLowerCase();
        if (imp === 'critical' || imp === 'high') return 'text-red-500 bg-red-500/10 border-red-500/20';
        if (imp === 'medium') return 'text-orange-500 bg-orange-500/10 border-orange-500/20';
        return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
    };

    const getImportanceIconColor = (impact) => {
        const imp = impact?.toLowerCase();
        if (imp === 'critical' || imp === 'high') return 'text-red-500';
        if (imp === 'medium') return 'text-orange-500';
        return 'text-yellow-500';
    };

    const getImportanceLabel = (imp) => {
        const i = imp?.toLowerCase();
        if (i === 'critical' || i === 'high') return t.cal_imp_high;
        if (i === 'medium') return t.cal_imp_med;
        return t.cal_imp_low;
    };

    const getImportanceStars = (impact) => {
        const imp = impact?.toLowerCase();
        if (imp === 'critical') return 5;
        if (imp === 'high') return 4;
        if (imp === 'medium') return 3;
        if (imp === 'low') return 2;
        return 1;
    };

    // Group events by Date
    const groupEventsByDate = (eventList) => {
        const groups = {};
        eventList.forEach(event => {
            // Apply Filters
            if (filter !== 'all' && event.importance?.toLowerCase() !== filter) return;
            if (countryFilter !== 'all' && event.country !== countryFilter) return;

            // Category Mapping/Filtering
            if (typeFilter !== 'all') {
                const type = event.type?.toUpperCase();
                if (typeFilter === 'CPI' && !['CPI', 'PPI', 'PMI', 'SENTIMENT', 'RETAIL SALES'].includes(type)) return;
                if (typeFilter === 'FOMC' && !['FOMC', 'ECB', 'BOJ', 'BOK'].includes(type)) return;
                if (typeFilter === 'Speech' && type !== 'SPEECH') return;
                if (typeFilter === 'Auction' && type !== 'AUCTION') return;
                if (typeFilter === 'Earnings' && type !== 'EARNINGS') return;
            }

            const dateStr = event.date;
            if (!groups[dateStr]) groups[dateStr] = [];
            groups[dateStr].push(event);
        });
        return Object.entries(groups).sort((a, b) => new Date(a[0]) - new Date(b[0]));
    };

    const formatDateHeader = (dateStr) => {
        // Parse "YYYY-MM-DD" as local date to avoid timezone shifts
        const [y, m, d] = dateStr.split('-').map(Number);
        const date = new Date(y, m - 1, d);

        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);

        // Compare using local strings to ignore time components
        const isToday = date.toDateString() === today.toDateString();
        const isTomorrow = date.toDateString() === tomorrow.toDateString();

        const options = { weekday: 'long', month: 'long', day: 'numeric' };
        // Use the current language for date formatting
        const formatted = date.toLocaleDateString(lang === 'ko' ? 'ko-KR' : (lang === 'zh' ? 'zh-CN' : (lang === 'ja' ? 'ja-JP' : 'en-US')), options);

        if (isToday) return `${t.cal_today}, ${formatted}`;
        if (isTomorrow) return `${t.cal_tomorrow}, ${formatted}`;
        return formatted;
    };

    const toggleExpand = (id) => {
        if (expandedEvent === id) setExpandedEvent(null);
        else setExpandedEvent(id);
    };

    const groupedEvents = groupEventsByDate(events);

    return (
        <div className={`min-h-screen py-8 transition-colors duration-300 ${isDark ? 'bg-[#0B0E14] text-slate-200' : 'bg-gray-50 text-gray-900'}`}>
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div>
                        <h1 className="text-2xl font-bold flex items-center gap-3">
                            <CalendarIcon className="w-6 h-6 text-blue-500" />
                            {t.cal_title}
                        </h1>
                        <p className={`text-sm mt-1 ${isDark ? 'text-slate-500' : 'text-gray-500'}`}>
                            {t.cal_desc}
                        </p>
                    </div>

                    <div className="flex flex-wrap items-center gap-3">
                        {/* Importance Filter */}
                        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900/40 border border-slate-800">
                            {['all', 'high', 'medium', 'low'].map(f => (
                                <button
                                    key={f}
                                    onClick={() => setFilter(f)}
                                    className={`px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded-lg transition-all ${filter === f
                                        ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                                        : (isDark ? 'text-slate-500 hover:bg-slate-800' : 'text-gray-500 hover:bg-gray-200')
                                        }`}
                                >
                                    {f === 'all' ? t.cal_filter_imp : getImportanceLabel(f)}
                                </button>
                            ))}
                        </div>

                        {/* Country Filter */}
                        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900/40 border border-slate-800">
                            {[
                                { id: 'all', label: t.cal_country_all, flag: '🌍' },
                                { id: 'US', label: 'US', flag: '🇺🇸' },
                                { id: 'KR', label: 'KR', flag: '🇰🇷' },
                                { id: 'EU', label: 'EU', flag: '🇪🇺' },
                                { id: 'JP', label: 'JP', flag: '🇯🇵' }
                            ].map(c => (
                                <button
                                    key={c.id}
                                    onClick={() => setCountryFilter(c.id)}
                                    className={`flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded-lg transition-all ${countryFilter === c.id
                                        ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                                        : (isDark ? 'text-slate-500 hover:bg-slate-800' : 'text-gray-500 hover:bg-gray-200')
                                        }`}
                                >
                                    <span>{c.flag}</span>
                                    {c.id === countryFilter && <span>{c.label}</span>}
                                </button>
                            ))}
                        </div>

                        {/* Type Filter */}
                        <select
                            value={typeFilter}
                            onChange={(e) => setTypeFilter(e.target.value)}
                            className={`px-3 py-2 text-[10px] font-bold uppercase tracking-wider rounded-xl border focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all ${isDark ? 'bg-slate-900/40 border-slate-800 text-slate-300' : 'bg-white border-gray-200 text-gray-700'
                                }`}
                        >
                            <option value="all">{t.cal_filter_cat}</option>
                            <option value="CPI">{t.cal_cat_macro}</option>
                            <option value="FOMC">{t.cal_cat_policy}</option>
                            <option value="Speech">{t.cal_cat_speech}</option>
                            <option value="Auction">{t.cal_cat_auction}</option>
                            <option value="Earnings">{t.cal_cat_earnings}</option>
                        </select>
                    </div>
                </div>

                {/* Calendar List */}
                <div className="space-y-6">
                    {loading ? (
                        <div className="p-24 text-center">
                            <div className="inline-block h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4"></div>
                            <p className="text-xs font-bold uppercase tracking-widest opacity-50">{t.cal_loading}</p>
                        </div>
                    ) : groupedEvents.length === 0 ? (
                        <div className="p-16 text-center border border-dashed rounded-2xl opacity-50">
                            <p>{t.cal_no_events}</p>
                        </div>
                    ) : (
                        groupedEvents.map(([date, dayEvents]) => (
                            <div key={date} className="animate-fade-in-up">
                                <div className={`sticky top-0 z-10 py-3 px-1 backdrop-blur-md border-b mb-2 flex items-center gap-3 ${isDark ? 'bg-[#0B0E14]/80 border-slate-800' : 'bg-gray-50/80 border-gray-200'}`}>
                                    <div className={`w-1.5 h-1.5 rounded-full ${date === new Date().toISOString().split('T')[0] ? 'bg-blue-500' : 'bg-slate-400'}`}></div>
                                    <h3 className={`text-sm font-bold uppercase tracking-wider ${isDark ? 'text-slate-100' : 'text-gray-800'}`}>
                                        {formatDateHeader(date)}
                                    </h3>
                                </div>

                                <div className={`rounded-xl border overflow-hidden ${isDark ? 'bg-[#151921] border-slate-800' : 'bg-white border-gray-200 shadow-sm'}`}>
                                    {/* Table Header (Desktop) */}
                                    <div className={`hidden md:grid grid-cols-12 gap-4 px-6 py-3 text-[10px] font-black uppercase tracking-widest border-b ${isDark ? 'border-slate-800 text-slate-500' : 'border-gray-100 text-gray-400'}`}>
                                        <div className="col-span-1 text-center">{t.cal_time}</div>
                                        <div className="col-span-1 text-center">{t.cal_country}</div>
                                        <div className="col-span-2 text-center">{t.cal_imp}</div>
                                        <div className="col-span-3">{t.cal_event}</div>
                                        <div className="col-span-1 text-right">{t.cal_actual}</div>
                                        <div className="col-span-1 text-right">{t.cal_forecast}</div>
                                        <div className="col-span-1 text-right">{t.cal_prev}</div>
                                        <div className="col-span-2 text-right"></div>
                                    </div>

                                    <div className={`divide-y ${isDark ? 'divide-slate-800/50' : 'divide-gray-100'}`}>
                                        {dayEvents.map((event, idx) => {
                                            const eventId = `${date}-${idx}`;
                                            const isExpanded = expandedEvent === eventId;

                                            return (
                                                <div key={idx} className={`group transition-colors ${isDark ? 'hover:bg-slate-800/20' : 'hover:bg-gray-50'}`}>
                                                    {/* Row Content */}
                                                    <div
                                                        className="py-4 px-6 cursor-pointer md:grid md:grid-cols-12 md:gap-4 md:items-center flex flex-col gap-3 relative"
                                                        onClick={() => toggleExpand(eventId)}
                                                    >
                                                        {/* Mobile: Top Row (Time, Country, Imp) */}
                                                        <div className="flex md:hidden items-center gap-3 text-xs mb-1">
                                                            <span className={`font-mono ${isDark ? 'text-slate-400' : 'text-gray-500'}`}>{event.time || '--:--'}</span>
                                                            <span className="text-base">
                                                                {event.country === 'US' ? '🇺🇸' :
                                                                    event.country === 'KR' ? '🇰🇷' :
                                                                        event.country === 'EU' ? '🇪🇺' :
                                                                            event.country === 'JP' ? '🇯🇵' : '🌍'}
                                                            </span>
                                                            <div className="flex items-center gap-0.5">
                                                                {[...Array(5)].map((_, i) => (
                                                                    <span key={i} className={`text-xs ${i < getImportanceStars(event.importance) ? 'text-yellow-500' : 'text-gray-300'}`}>★</span>
                                                                ))}
                                                            </div>
                                                        </div>

                                                        {/* Desktop Columns */}
                                                        <div className={`col-span-1 hidden md:block text-center text-xs font-mono ${isDark ? 'text-slate-400' : 'text-gray-500'}`}>
                                                            {event.time || '--:--'}
                                                        </div>
                                                        <div className="col-span-1 hidden md:block text-center text-lg">
                                                            {event.country === 'US' ? '🇺🇸' :
                                                                event.country === 'KR' ? '🇰🇷' :
                                                                    event.country === 'EU' ? '🇪🇺' :
                                                                        event.country === 'JP' ? '🇯🇵' : '🌍'}
                                                        </div>
                                                        <div className="col-span-2 hidden md:flex justify-center items-center gap-0.5">
                                                            {[...Array(5)].map((_, i) => (
                                                                <Star key={i} className={`w-3.5 h-3.5 ${i < getImportanceStars(event.importance) ? 'text-yellow-500 fill-yellow-500' : (isDark ? 'text-slate-700' : 'text-gray-200')}`} />
                                                            ))}
                                                        </div>

                                                        {/* Title */}
                                                        <div className="col-span-3">
                                                            <div className={`font-medium text-sm flex items-center gap-2 ${isDark ? 'text-slate-200' : 'text-gray-900'}`}>
                                                                {event.title}
                                                                {event.actual && event.actual !== '-' && (
                                                                    <span className="animate-pulse flex items-center gap-1.5 px-1.5 py-0.5 rounded-full bg-red-500/10 border border-red-500/20 text-[8px] font-black text-red-500">
                                                                        <span className="w-1 h-1 rounded-full bg-red-500"></span>
                                                                        LIVE
                                                                    </span>
                                                                )}
                                                            </div>
                                                            {/* Mobile only forecast/actual preview */}
                                                            <div className="md:hidden flex items-center gap-4 mt-2 text-xs opacity-60">
                                                                <span>{t.cal_actual}: {event.actual || '-'}</span>
                                                                <span>{t.cal_forecast}: {event.forecast || '-'}</span>
                                                            </div>
                                                        </div>

                                                        {/* Data Columns */}
                                                        <div className={`col-span-1 hidden md:block text-right font-mono text-sm font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                                                            {event.actual || '-'}
                                                        </div>
                                                        <div className={`col-span-1 hidden md:block text-right font-mono text-xs ${isDark ? 'text-slate-500' : 'text-gray-500'}`}>
                                                            {event.forecast || '-'}
                                                        </div>
                                                        <div className={`col-span-1 hidden md:block text-right font-mono text-xs ${isDark ? 'text-slate-500' : 'text-gray-400'}`}>
                                                            {event.previous || '-'}
                                                        </div>

                                                        {/* Expand Icon */}
                                                        <div className="col-span-2 hidden md:flex justify-end">
                                                            {isExpanded ? <ChevronUp className="w-4 h-4 opacity-30" /> : <ChevronDown className="w-4 h-4 opacity-30" />}
                                                        </div>
                                                    </div>

                                                    {/* Expanded Details */}
                                                    {isExpanded && (
                                                        <div className={`px-6 pb-6 pt-0 text-sm ${isDark ? 'text-slate-400' : 'text-gray-600'}`}>
                                                            <div className={`p-4 rounded-lg border flex flex-col gap-4 ${isDark ? 'bg-slate-900/50 border-slate-800' : 'bg-gray-50 border-gray-200'}`}>

                                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                                    <div>
                                                                        <div className="text-[10px] font-black uppercase tracking-widest opacity-50 mb-2">{t.cal_description}</div>
                                                                        <p className="leading-relaxed">{event.description}</p>
                                                                        <div className="mt-4 flex items-center gap-2 text-xs">
                                                                            <span className={`px-2 py-0.5 rounded border ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-300'}`}>
                                                                                {t.cal_category}: {
                                                                                    event.category === 'macro' ? t.cal_cat_macro :
                                                                                        event.category === 'policy' ? t.cal_cat_policy :
                                                                                            event.category === 'inflation' ? '인플레이션' :
                                                                                                event.category === 'consumption' ? '소비 지표' :
                                                                                                    event.category === 'earnings' ? t.cal_cat_earnings : event.category
                                                                                }
                                                                            </span>
                                                                            <span className={`px-2 py-0.5 rounded border ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-300'}`}>
                                                                                {t.cal_impact}: {event.impact}
                                                                            </span>
                                                                        </div>
                                                                    </div>

                                                                    {event.scenarios && (
                                                                        <div>
                                                                            <div className="text-[10px] font-black uppercase tracking-widest opacity-50 mb-2 flex items-center gap-2">
                                                                                {t.cal_scenario}
                                                                            </div>
                                                                            <div className="space-y-2">
                                                                                {Object.entries(event.scenarios).map(([key, val]) => (
                                                                                    <div key={key} className="flex gap-3 text-xs">
                                                                                        <span className={`shrink-0 w-16 px-1.5 py-0.5 rounded text-[10px] font-bold uppercase text-center border ${key.includes('high') || key.includes('beat') ? 'text-red-500 border-red-500/20 bg-red-500/5' :
                                                                                            key.includes('low') || key.includes('miss') ? 'text-green-500 border-green-500/20 bg-green-500/5' :
                                                                                                'text-blue-500 border-blue-500/20 bg-blue-500/5'
                                                                                            }`}>
                                                                                            {
                                                                                                key.includes('high') || key.includes('beat') ? t.cal_sce_high :
                                                                                                    key.includes('low') || key.includes('miss') ? t.cal_sce_low :
                                                                                                        key.includes('consensus') ? t.cal_sce_con :
                                                                                                            key.includes('bull') ? t.cal_sce_bull :
                                                                                                                key.includes('bear') ? t.cal_sce_bear : key
                                                                                            }
                                                                                        </span>
                                                                                        <span className={isDark ? 'text-slate-300' : 'text-gray-700'}>{val}</span>
                                                                                    </div>
                                                                                ))}
                                                                            </div>
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>

                <div className={`mt-10 p-6 rounded-2xl border text-center ${isDark ? 'bg-[#151921] border-slate-800 text-slate-500' : 'bg-white border-gray-200 text-gray-500'}`}>
                    <p className="text-xs">
                        {t.cal_footer}
                    </p>
                </div>
            </div>
        </div>
    );
};

export default CalendarPage;
