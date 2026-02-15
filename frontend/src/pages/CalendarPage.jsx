import React, { useState, useEffect } from 'react';
import { Calendar as CalendarIcon, Clock, Globe, Info, Filter, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { useTranslation } from '../utils/translations';
import api from '../utils/api';

const CalendarPage = ({ settings }) => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(false);
    const isDark = settings?.darkMode;
    const t = useTranslation(settings);

    useEffect(() => {
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
        fetchEvents();
    }, []);

    return (
        <div className={`min-h-screen py-10 transition-colors duration-300 ${isDark ? 'bg-slate-950 text-slate-100' : 'bg-gray-50 text-gray-900'}`}>
            <div className="max-w-7xl mx-auto px-4 space-y-10">
                <h1 className="text-3xl font-black flex items-center gap-3">
                    <div className="bg-blue-600 p-2 rounded-xl text-white"><CalendarIcon className="w-7 h-7" /></div>
                    {t.calendarTitle || 'Economic Calendar'}
                </h1>

                <div className="space-y-4">
                    {events.map((e, i) => (
                        <div key={i} className={`p-6 rounded-2xl border ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                            <div className="flex justify-between">
                                <span className="font-bold">{e.event}</span>
                                <span className="opacity-50 text-sm">{e.time}</span>
                            </div>
                        </div>
                    ))}
                    {loading && <div className="text-center opacity-50 italic">Syncing World Events...</div>}
                </div>
            </div>
        </div>
    );
};

export default CalendarPage;
