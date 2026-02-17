import React, { useState, useEffect } from 'react';
import {
    TrendingUp,
    Calendar,
    Clock,
    Globe,
    ChevronRight,
    Search,
    AlertCircle,
    Info,
    ExternalLink,
    Filter
} from 'lucide-react';
import { useTranslation } from '../utils/translations';
import api from '../utils/api';

const EarningsPage = ({ settings }) => {
    const t = useTranslation(settings);
    const isDark = settings?.darkMode;

    const [loading, setLoading] = useState(false);
    const [events, setEvents] = useState([]);
    const [country, setCountry] = useState('US');
    const [searchQuery, setSearchQuery] = useState('');
    const [error, setError] = useState(null);

    const fetchEarnings = async () => {
        setLoading(true);
        setError(null);
        try {
            const today = new Date();
            const startStr = today.toISOString().split('T')[0];
            const end = new Date();
            end.setDate(today.getDate() + 30);
            const endStr = end.toISOString().split('T')[0];

            const res = await api.get(`/api/calendar/earnings`, {
                params: {
                    start_date: startStr,
                    end_date: endStr,
                    country: country,
                    lang: settings?.language || 'ko'
                }
            });
            setEvents(res.data.events || []);
        } catch (err) {
            console.error('Earnings fetch error:', err);
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchEarnings();
    }, [country, settings?.language]);

    const filteredEvents = events.filter(event =>
        event.ticker?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        event.title?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const getImpactColor = (imp) => {
        switch (imp) {
            case 'high': return 'bg-red-500';
            case 'medium': return 'bg-amber-500';
            default: return 'bg-blue-500';
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 py-8">
            {/* Header section */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
                <div>
                    <h1 className={`text-3xl font-bold flex items-center gap-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                        <TrendingUp className="text-blue-500 w-8 h-8" />
                        {t.nav_earnings || '실적 캘린더'}
                    </h1>
                    <p className={`mt-2 ${isDark ? 'text-slate-400' : 'text-gray-500'}`}>
                        주요 기업의 분기별 실적 발표 일정 및 예상치를 확인하세요.
                    </p>
                </div>

                <div className="flex gap-2">
                    <button
                        onClick={() => setCountry('US')}
                        className={`px-4 py-2 rounded-xl border transition-all flex items-center gap-2 ${country === 'US'
                            ? 'bg-blue-600 border-blue-600 text-white shadow-lg shadow-blue-500/20'
                            : (isDark ? 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-750' : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50')}`}
                    >
                        <Globe className="w-4 h-4" /> Global (USA)
                    </button>
                    <button
                        onClick={() => setCountry('KR')}
                        className={`px-4 py-2 rounded-xl border transition-all flex items-center gap-2 ${country === 'KR'
                            ? 'bg-blue-600 border-blue-600 text-white shadow-lg shadow-blue-500/20'
                            : (isDark ? 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-750' : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50')}`}
                    >
                        🇰🇷 Korea
                    </button>
                </div>
            </div>

            {/* Controls */}
            <div className={`p-4 rounded-2xl mb-6 flex flex-col md:flex-row gap-4 items-center ${isDark ? 'bg-slate-900/50 border border-slate-800' : 'bg-white border border-gray-100 shadow-sm'}`}>
                <div className="relative flex-1 w-full">
                    <Search className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 ${isDark ? 'text-slate-500' : 'text-gray-400'}`} />
                    <input
                        type="text"
                        placeholder="티커 또는 회사명 검색..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className={`w-full pl-10 pr-4 py-2.5 rounded-xl border outline-none transition-all ${isDark
                            ? 'bg-slate-800 border-slate-700 text-white focus:border-blue-500'
                            : 'bg-white border-gray-200 text-gray-900 focus:border-blue-500'}`}
                    />
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-500 shrink-0">
                    <Filter className="w-4 h-4" />
                    <span>최근 30일 이내 상장사 실적 발표 {filteredEvents.length}건</span>
                </div>
            </div>

            {/* Error State */}
            {error && (
                <div className="p-4 rounded-xl bg-red-50 border border-red-100 text-red-600 flex items-start gap-3 mb-6">
                    <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                    <div>
                        <p className="font-semibold">데이터를 불러오는 중 오류가 발생했습니다.</p>
                        <p className="text-sm opacity-80">{error}</p>
                    </div>
                </div>
            )}

            {/* Events List */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {loading ? (
                    Array(6).fill(0).map((_, i) => (
                        <div key={i} className={`h-40 rounded-2xl animate-pulse ${isDark ? 'bg-slate-900' : 'bg-gray-100'}`} />
                    ))
                ) : filteredEvents.length > 0 ? (
                    filteredEvents.map((event, idx) => (
                        <div
                            key={idx}
                            className={`group p-5 rounded-2xl border transition-all hover:shadow-xl ${isDark
                                ? 'bg-slate-900 border-slate-800 hover:border-slate-700 shadow-slate-950/20'
                                : 'bg-white border-gray-100 hover:border-gray-200 shadow-gray-200/50'}`}
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex items-center gap-3">
                                    <div className={`p-2 rounded-xl font-bold text-sm tracking-tight ${isDark ? 'bg-slate-800 text-white' : 'bg-gray-50 text-gray-900 border border-gray-100'}`}>
                                        {event.ticker}
                                    </div>
                                    <div className={`w-1.5 h-1.5 rounded-full ${getImpactColor(event.importance)}`} />
                                </div>
                                <div className={`text-xs font-medium px-2 py-1 rounded-lg ${isDark ? 'bg-slate-800 text-slate-400' : 'bg-gray-100 text-gray-500'}`}>
                                    {event.source}
                                </div>
                            </div>

                            <h3 className={`font-bold text-lg mb-2 group-hover:text-blue-500 transition-colors ${isDark ? 'text-white' : 'text-gray-900'}`}>
                                {event.title}
                            </h3>

                            <div className="space-y-2 mt-4">
                                <div className="flex items-center gap-2 text-sm text-gray-500">
                                    <Calendar className="w-4 h-4 shrink-0" />
                                    <span>{event.date}</span>
                                </div>
                                <div className="flex items-center gap-2 text-sm text-gray-500">
                                    <Clock className="w-4 h-4 shrink-0" />
                                    <span>{event.time}</span>
                                </div>
                            </div>

                            {event.forecast_eps && (
                                <div className={`mt-4 pt-4 border-t flex justify-between items-center ${isDark ? 'border-slate-800' : 'border-gray-50'}`}>
                                    <span className="text-xs text-gray-500 font-medium">EPS 예상치</span>
                                    <span className={`font-mono font-bold ${isDark ? 'text-blue-400' : 'text-blue-600'}`}>
                                        ${event.forecast_eps}
                                    </span>
                                </div>
                            )}

                            <div className="mt-4 flex gap-2">
                                <button
                                    onClick={() => window.location.href = `/analysis/${event.ticker}`}
                                    className={`flex-1 py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1 ${isDark
                                        ? 'bg-blue-600/10 text-blue-400 hover:bg-blue-600/20'
                                        : 'bg-blue-50 text-blue-600 hover:bg-blue-100'}`}
                                >
                                    AI 분석 <ChevronRight className="w-3 h-3" />
                                </button>
                                <a
                                    href={country === 'US' ? `https://finance.yahoo.com/quote/${event.ticker}` : `https://finance.naver.com/item/main.naver?code=${event.ticker}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className={`p-2 rounded-xl transition-all ${isDark ? 'bg-slate-800 text-slate-400 hover:text-white' : 'bg-gray-50 text-gray-400 hover:text-gray-600'}`}
                                >
                                    <ExternalLink className="w-4 h-4" />
                                </a>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="col-span-full py-20 flex flex-col items-center justify-center gap-4">
                        <div className={`p-4 rounded-full ${isDark ? 'bg-slate-900 text-slate-700' : 'bg-gray-50 text-gray-200'}`}>
                            <Calendar className="w-12 h-12" />
                        </div>
                        <div className="text-center">
                            <p className={`font-bold ${isDark ? 'text-slate-400' : 'text-gray-500'}`}>검색 결과가 없습니다.</p>
                            <p className="text-sm text-gray-400">다른 국가를 선택하거나 검색어를 변경해보세요.</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Info Box */}
            <div className={`mt-12 p-6 rounded-2xl flex gap-4 items-start ${isDark ? 'bg-blue-900/10 border border-blue-900/20' : 'bg-blue-50 border border-blue-100'}`}>
                <Info className={`w-5 h-5 shrink-0 mt-0.5 ${isDark ? 'text-blue-400' : 'text-blue-500'}`} />
                <div className="text-sm">
                    <p className={`font-bold mb-1 ${isDark ? 'text-blue-300' : 'text-blue-800'}`}>실적 발표 참고 사항</p>
                    <p className={isDark ? 'text-blue-200/60' : 'text-blue-700/70'}>
                        실적 발표 시간은 현지 시장 상황에 따라 변경될 수 있습니다. '장 시작 전'은 보통 개장 1~2시간 전, '장 마감 후'는 폐장 직후를 의미합니다.
                        한국 주식의 경우 공시 시스템(DART)의 실시간 공시를 우선 확인하시기 바랍니다.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default EarningsPage;
