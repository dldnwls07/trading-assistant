import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Calendar as CalendarIcon, Filter, Clock, Globe } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

const CalendarPage = ({ settings }) => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all'); // all, high, medium, low

    const isDark = settings?.darkMode;

    useEffect(() => {
        const fetchEvents = async () => {
            try {
                const res = await axios.get(`${API_BASE}/api/calendar`);
                setEvents(res.data.events || []);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchEvents();
    }, []);

    const getImportanceColor = (impact) => {
        if (impact === 'High' || impact === 'Critical') return isDark ? 'text-rose-400 bg-rose-500/10 border-rose-500/20' : 'text-red-600 bg-red-50 border-red-100';
        if (impact === 'Medium') return isDark ? 'text-orange-400 bg-orange-500/10 border-orange-500/20' : 'text-orange-600 bg-orange-50 border-orange-100';
        return isDark ? 'text-blue-400 bg-blue-500/10 border-blue-500/20' : 'text-blue-600 bg-blue-50 border-blue-100';
    };

    const filteredEvents = filter === 'all'
        ? events
        : events.filter(e => e.importance?.toLowerCase() === filter);

    return (
        <div className={`min-h-screen py-10 transition-colors duration-300 ${isDark ? 'bg-slate-950 text-slate-100' : 'bg-gray-50 text-gray-900'}`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div>
                        <h1 className="text-3xl font-black flex items-center gap-3">
                            <div className="bg-blue-600 p-2 rounded-xl text-white shadow-lg shadow-blue-500/20">
                                <CalendarIcon className="w-7 h-7" />
                            </div>
                            Economic Calendar
                        </h1>
                        <p className={`text-sm font-medium mt-2 opacity-50 ${isDark ? 'text-slate-400' : 'text-gray-500'}`}>
                            Key market-moving events and macro data releases.
                        </p>
                    </div>

                    <div className={`flex items-center gap-1 p-1.5 rounded-2xl border shadow-sm ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-200'}`}>
                        <Filter className="w-4 h-4 text-gray-400 ml-2 mr-1" />
                        {['all', 'high', 'medium', 'low'].map(f => (
                            <button
                                key={f}
                                onClick={() => setFilter(f)}
                                className={`px-4 py-1.5 text-[10px] font-black uppercase tracking-widest rounded-xl transition-all ${filter === f
                                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20'
                                    : (isDark ? 'text-slate-400 hover:bg-slate-800' : 'text-gray-600 hover:bg-gray-100')
                                    }`}
                            >
                                {f}
                            </button>
                        ))}
                    </div>
                </div>

                <div className={`shadow-2xl rounded-[2.5rem] border overflow-hidden transition-all duration-300 ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                    {loading ? (
                        <div className="p-24 text-center">
                            <div className="inline-block h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4"></div>
                            <p className="text-sm font-black uppercase tracking-widest opacity-30">Synchronizing Global Pulse...</p>
                        </div>
                    ) : filteredEvents.length === 0 ? (
                        <div className="p-24 text-center opacity-30">
                            <Globe className="w-16 h-16 mx-auto mb-4 opacity-20" />
                            <p className="text-sm font-black uppercase tracking-widest">No major events identified for this period</p>
                        </div>
                    ) : (
                        <ul className={`divide-y ${isDark ? 'divide-slate-800/50' : 'divide-gray-50'}`}>
                            {filteredEvents.map((event, idx) => (
                                <li key={idx} className={`transition-all duration-200 group ${isDark ? 'hover:bg-blue-500/5' : 'hover:bg-blue-50/30'}`}>
                                    <div className="px-8 py-6 flex flex-col sm:flex-row sm:items-center justify-between gap-6">
                                        <div className="flex items-center gap-6 min-w-0 flex-1">
                                            <div className={`flex flex-col items-center justify-center w-16 h-16 rounded-2xl border transition-transform group-hover:scale-105 ${isDark ? 'bg-slate-800 border-slate-700 shadow-inner' : 'bg-gray-100 border-gray-200'}`}>
                                                <span className={`text-[10px] font-black uppercase tracking-tighter ${isDark ? 'text-blue-400' : 'text-blue-600'}`}>{new Date(event.date).toLocaleString('en-US', { month: 'short' })}</span>
                                                <span className="text-2xl font-black">{new Date(event.date).getDate()}</span>
                                            </div>
                                            <div className="min-w-0 flex-1 space-y-2">
                                                <div className="flex flex-wrap items-center gap-2">
                                                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border shadow-sm ${getImportanceColor(event.importance)}`}>
                                                        {event.importance || 'Low'}
                                                    </span>
                                                    <span className="text-[10px] font-bold opacity-40 flex items-center gap-1 uppercase tracking-wider">
                                                        <Clock className="w-3.5 h-3.5" />
                                                        {event.time || 'All Day'}
                                                    </span>
                                                    <span className="text-[10px] font-bold opacity-40 flex items-center gap-1 uppercase tracking-wider">
                                                        <Globe className="w-3.5 h-3.5" />
                                                        {event.country || 'Global'}
                                                    </span>
                                                </div>
                                                <p className={`text-base font-black tracking-tight leading-tight ${isDark ? 'group-hover:text-blue-400' : 'group-hover:text-blue-600'} transition-colors`}>{event.title}</p>
                                            </div>
                                        </div>
                                        <div className="flex flex-row sm:flex-col items-center sm:items-end gap-6 sm:gap-2 text-sm whitespace-nowrap pt-2 sm:pt-0">
                                            <div className="flex flex-col items-end">
                                                <span className="text-[9px] font-black uppercase tracking-widest opacity-30">Actual</span>
                                                <span className={`font-black ${isDark ? 'text-white' : 'text-gray-900'}`}>{event.actual || '--'}</span>
                                            </div>
                                            <div className="flex flex-col items-end">
                                                <span className="text-[9px] font-black uppercase tracking-widest opacity-30">Forecast</span>
                                                <span className="font-bold opacity-60">{event.forecast || '--'}</span>
                                            </div>
                                        </div>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CalendarPage;
