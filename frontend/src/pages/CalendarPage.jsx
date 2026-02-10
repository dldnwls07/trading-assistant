import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Calendar as CalendarIcon, Filter, Clock, Globe } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

const CalendarPage = () => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all'); // all, high, medium, low

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
        if (impact === 'High') return 'text-red-600 bg-red-50 border-red-100';
        if (impact === 'Medium') return 'text-orange-600 bg-orange-50 border-orange-100';
        return 'text-blue-600 bg-blue-50 border-blue-100';
    };

    const filteredEvents = filter === 'all'
        ? events
        : events.filter(e => e.importance?.toLowerCase() === filter);

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <CalendarIcon className="w-6 h-6 text-blue-600" />
                        Economic Calendar
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">Key market-moving events and data releases.</p>
                </div>

                <div className="flex items-center gap-2 bg-white p-1 rounded-lg border border-gray-200 shadow-sm">
                    <Filter className="w-4 h-4 text-gray-400 ml-2" />
                    {['all', 'high', 'medium', 'low'].map(f => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={`px-3 py-1.5 text-xs font-medium rounded-md capitalize transition-colors ${filter === f
                                    ? 'bg-blue-600 text-white shadow-sm'
                                    : 'text-gray-600 hover:bg-gray-100'
                                }`}
                        >
                            {f}
                        </button>
                    ))}
                </div>
            </div>

            <div className="bg-white shadow overflow-hidden sm:rounded-lg border border-gray-200">
                {loading ? (
                    <div className="p-12 text-center text-gray-500">Loading events...</div>
                ) : filteredEvents.length === 0 ? (
                    <div className="p-12 text-center text-gray-500">No events found for this period.</div>
                ) : (
                    <ul className="divide-y divide-gray-200">
                        {filteredEvents.map((event, idx) => (
                            <li key={idx} className="hover:bg-gray-50 transition-colors">
                                <div className="px-4 py-4 sm:px-6 flex items-center justify-between">
                                    <div className="flex items-center gap-4 min-w-0 flex-1">
                                        <div className="flex flex-col items-center justify-center w-12 h-12 bg-gray-100 rounded-lg text-gray-500 border border-gray-200">
                                            <span className="text-xs font-bold uppercase">{new Date(event.date).toLocaleString('en-US', { month: 'short' })}</span>
                                            <span className="text-lg font-bold text-gray-900">{new Date(event.date).getDate()}</span>
                                        </div>
                                        <div className="min-w-0 flex-1">
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${getImportanceColor(event.importance)}`}>
                                                    {event.importance || 'Low'}
                                                </span>
                                                <span className="text-xs text-gray-500 flex items-center gap-1">
                                                    <Clock className="w-3 h-3" />
                                                    {event.time || 'All Day'}
                                                </span>
                                                <span className="text-xs text-gray-500 flex items-center gap-1">
                                                    <Globe className="w-3 h-3" />
                                                    {event.country || 'Global'}
                                                </span>
                                            </div>
                                            <p className="text-sm font-medium text-blue-600 truncate">{event.title}</p>
                                        </div>
                                    </div>
                                    <div className="ml-4 flex-shrink-0 flex flex-col items-end text-sm text-gray-500 space-y-1">
                                        <div>
                                            <span className="text-xs text-gray-400 mr-2">Actual</span>
                                            <span className="font-bold text-gray-900">{event.actual || '--'}</span>
                                        </div>
                                        <div>
                                            <span className="text-xs text-gray-400 mr-2">Forecast</span>
                                            <span className="">{event.forecast || '--'}</span>
                                        </div>
                                    </div>
                                </div>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
};

export default CalendarPage;
