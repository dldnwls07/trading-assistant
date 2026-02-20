import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    TrendingUp,
    Globe,
    Search,
    Filter,
    AlertCircle,
    Calendar,
    Clock,
    ChevronRight,
    ExternalLink,
    Info,
    LayoutDashboard
} from 'lucide-react';
import { useTranslation } from '../utils/translations';
import api from '../utils/api';

// 백엔드 연결 실패 시 표시할 데모 실적 데이터
const DEMO_EARNINGS = [
    { ticker: 'NVDA', title: 'NVIDIA Corporation', date: new Date(Date.now() + 86400000 * 3).toISOString().split('T')[0], time: 'AMC', importance: 'high', source: 'DEMO', forecast_eps: '5.59' },
    { ticker: 'AAPL', title: 'Apple Inc.', date: new Date(Date.now() + 86400000 * 7).toISOString().split('T')[0], time: 'AMC', importance: 'high', source: 'DEMO', forecast_eps: '2.35' },
    { ticker: 'MSFT', title: 'Microsoft Corporation', date: new Date(Date.now() + 86400000 * 10).toISOString().split('T')[0], time: 'AMC', importance: 'high', source: 'DEMO', forecast_eps: '3.10' },
    { ticker: '005930', title: '삼성전자', date: new Date(Date.now() + 86400000 * 5).toISOString().split('T')[0], time: 'BMO', importance: 'high', source: 'DEMO', forecast_eps: null },
    { ticker: 'TSLA', title: 'Tesla Inc.', date: new Date(Date.now() + 86400000 * 14).toISOString().split('T')[0], time: 'AMC', importance: 'medium', source: 'DEMO', forecast_eps: '0.68' },
    { ticker: 'META', title: 'Meta Platforms', date: new Date(Date.now() + 86400000 * 21).toISOString().split('T')[0], time: 'AMC', importance: 'high', source: 'DEMO', forecast_eps: '5.25' },
];

const EarningsPage = ({ settings }) => {
    const t = useTranslation(settings);

    const [loading, setLoading] = useState(false);
    const [events, setEvents] = useState([]);
    const [country, setCountry] = useState('US');
    const [searchQuery, setSearchQuery] = useState('');
    const [error, setError] = useState(null);
    const [fetchError, setFetchError] = useState(null); // 폴백 사용 중 알림

    const fetchEarnings = async () => {
        setLoading(true);
        setError(null);
        setFetchError(null);
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
            const fetched = res.data.events || [];
            if (fetched.length === 0) {
                // 빈 응답이면 데모 데이터로 폴백
                setEvents(DEMO_EARNINGS);
                setFetchError('API 응답이 비어있어 데모 데이터를 표시합니다.');
            } else {
                setEvents(fetched);
            }
        } catch (err) {
            console.error('Earnings fetch error:', err);
            // 백엔드 바로 연결 안 될 때 데모 데이터 표시
            setEvents(DEMO_EARNINGS);
            setFetchError('백엔드 연결 실패 - 데모 데이터를 표시 중입니다. 실제 서버 실행 후 새로고침하세요.');
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
            case 'high': return 'bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.4)]';
            case 'medium': return 'bg-yellow-400/60 shadow-[0_0_10px_rgba(250,204,21,0.2)]';
            default: return 'bg-yellow-400';
        }
    };

    return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-7xl mx-auto px-4 py-12 text-foreground bg-transparent">
            {/* Header section */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-8 mb-12">
                <div className="space-y-4">
                    <div className="flex items-center gap-4">
                        <div className="bg-yellow-400 p-3 rounded-2xl text-black shadow-xl shadow-yellow-400/20">
                            <TrendingUp className="w-8 h-8" />
                        </div>
                        <h1 className="text-4xl font-black tracking-tighter uppercase text-zinc-100 italic">
                            {t.nav_earnings || 'EARNINGS_RADAR'}
                        </h1>
                    </div>
                    <p className="text-zinc-500 font-bold uppercase text-[10px] tracking-[0.3em] font-mono flex items-center gap-2 max-w-xl">
                        <LayoutDashboard className="w-3.5 h-3.5 text-yellow-400" /> QUARTERLY_PERFORMANCE_METRICS & FISCAL_REPORTS
                    </p>
                </div>

                <div className="flex p-1.5 rounded-2xl bg-white/5 border border-white/10 shadow-inner">
                    <button
                        onClick={() => setCountry('US')}
                        className={`px-6 py-2.5 rounded-xl text-sm font-black transition-all flex items-center gap-2 ${country === 'US'
                            ? 'bg-yellow-400 text-black shadow-lg shadow-yellow-400/20'
                            : 'text-zinc-500 opacity-60 hover:opacity-100 hover:bg-white/5'}`}
                    >
                        <Globe className="w-4 h-4" /> Global (USA)
                    </button>
                    <button
                        onClick={() => setCountry('KR')}
                        className={`px-6 py-2.5 rounded-xl text-sm font-black transition-all flex items-center gap-2 ${country === 'KR'
                            ? 'bg-yellow-400 text-black shadow-lg shadow-yellow-400/20'
                            : 'text-zinc-500 opacity-60 hover:opacity-100 hover:bg-white/5'}`}
                    >
                        <span>🇰🇷</span> KOREA
                    </button>
                </div>
            </div>

            {/* Controls */}
            <div className="p-8 rounded-[2.5rem] mb-12 flex flex-col md:flex-row gap-8 items-center bg-white/5 border border-white/10 shadow-2xl backdrop-blur-xl">
                <div className="relative flex-1 w-full group">
                    <Search className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500 group-focus-within:text-yellow-400 transition-colors" />
                    <input
                        type="text"
                        placeholder="티커 분석 또는 기업명 검색..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-14 pr-6 py-4 rounded-2xl text-sm font-bold bg-white/5 border border-white/10 text-zinc-100 placeholder:text-zinc-600 outline-none focus:border-yellow-400 transition-all shadow-inner"
                    />
                </div>
                <div className="flex items-center gap-3 px-6 py-3 rounded-2xl bg-yellow-400/5 border border-yellow-400/10 shrink-0">
                    <Filter className="w-4 h-4 text-yellow-400" />
                    <span className="text-[11px] font-black text-zinc-400 uppercase tracking-widest font-mono">
                        {filteredEvents.length} DATA_POINTS_LOCATED
                    </span>
                </div>
            </div>

            {/* Error State */}
            {error && (
                <div className="p-6 rounded-3xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-start gap-4 mb-10 animate-shake">
                    <AlertCircle className="w-6 h-6 shrink-0 mt-0.5" />
                    <div className="space-y-1">
                        <p className="font-black uppercase text-xs tracking-widest">ERROR_CODE_FETCH_FAILURE</p>
                        <p className="text-sm font-bold opacity-80">{error}</p>
                    </div>
                </div>
            )}

            {/* 폴백 데이터 사용 중 알림 배너 */}
            {fetchError && !error && (
                <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center gap-3 mb-6">
                    <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
                    <p className="text-xs font-bold text-amber-400/80">{fetchError}</p>
                </div>
            )}

            {/* Events List */}
            <motion.div
                initial="hidden" animate="visible"
                variants={{
                    hidden: { opacity: 0 },
                    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
                }}
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
            >
                {loading ? (
                    Array(6).fill(0).map((_, i) => (
                        <div key={i} className="h-48 rounded-[2.5rem] animate-pulse bg-white/3 border border-white/5" />
                    ))
                ) : filteredEvents.length > 0 ? (
                    filteredEvents.map((event, idx) => (
                        <motion.div
                            variants={{ hidden: { opacity: 0, scale: 0.95 }, visible: { opacity: 1, scale: 1 } }}
                            key={idx}
                            className="group p-8 rounded-[2.5rem] border transition-all duration-500 bg-white/3 backdrop-blur-md border-white/5 hover:bg-white/10 hover:border-yellow-400/30 hover:shadow-2xl hover:scale-[1.03]"
                        >
                            <div className="flex justify-between items-start mb-6">
                                <div className="flex items-center gap-4">
                                    <div className="px-4 py-2 rounded-xl font-mono font-black text-sm bg-yellow-400 text-black shadow-lg shadow-yellow-400/20">
                                        {event.ticker}
                                    </div>
                                    <div className={`w-2 h-2 rounded-full animate-pulse ${getImpactColor(event.importance)}`} />
                                </div>
                                <div className="text-[10px] font-black px-3 py-1.5 rounded-lg bg-white/5 text-zinc-500 border border-white/10 uppercase tracking-widest font-mono">
                                    {event.source}
                                </div>
                            </div>

                            <h3 className="font-black text-xl mb-4 group-hover:text-yellow-400 transition-colors text-zinc-100 uppercase tracking-tighter">
                                {event.title}
                            </h3>

                            <div className="flex flex-wrap gap-4 mt-6">
                                <div className="flex items-center gap-2 text-[11px] font-black text-zinc-500 font-mono">
                                    <Calendar className="w-4 h-4 text-yellow-400/50" />
                                    <span>{event.date}</span>
                                </div>
                                <div className="flex items-center gap-2 text-[11px] font-black text-zinc-500 font-mono">
                                    <Clock className="w-4 h-4 text-yellow-400/50" />
                                    <span>{event.time}</span>
                                </div>
                            </div>

                            {event.forecast_eps && (
                                <div className="mt-8 pt-6 border-t border-white/5 flex justify-between items-center">
                                    <span className="text-[10px] text-zinc-600 font-black tracking-[0.2em] uppercase font-mono">EPS_ESTIMATE</span>
                                    <span className="font-mono font-black text-xl text-yellow-400 drop-shadow-[0_0_10px_rgba(250,204,21,0.3)]">
                                        ${event.forecast_eps}
                                    </span>
                                </div>
                            )}

                            <div className="mt-8 flex gap-3">
                                <button
                                    onClick={() => window.location.href = `/analysis/${event.ticker}`}
                                    className="flex-1 py-3.5 rounded-2xl text-[11px] font-black transition-all flex items-center justify-center gap-2 bg-yellow-400/10 text-yellow-400 hover:bg-yellow-400 text-black shadow-yellow-400/10 hover:shadow-lg uppercase tracking-widest"
                                >
                                    AI ANALYSIS <ChevronRight className="w-4 h-4" />
                                </button>
                                <a
                                    href={country === 'US' ? `https://finance.yahoo.com/quote/${event.ticker}` : `https://finance.naver.com/item/main.naver?code=${event.ticker}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="p-3.5 rounded-2xl transition-all bg-white/5 text-zinc-500 hover:text-zinc-100 border border-white/10 hover:border-white/20"
                                >
                                    <ExternalLink className="w-5 h-5" />
                                </a>
                            </div>
                        </motion.div>
                    ))
                ) : (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="col-span-full py-40 flex flex-col items-center justify-center gap-8">
                        <div className="w-24 h-24 rounded-full bg-white/2 flex items-center justify-center border border-white/5">
                            <Calendar className="w-12 h-12 text-zinc-700" />
                        </div>
                        <div className="text-center space-y-2">
                            <p className="text-3xl font-black text-zinc-300 uppercase tracking-tighter">NO_DATA_DETECTED</p>
                            <p className="text-zinc-600 font-bold uppercase text-[10px] tracking-[0.3em]">Modify your region or search node for more intel</p>
                        </div>
                    </motion.div>
                )}
            </motion.div>

            {/* Info Box */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="mt-20 p-8 rounded-[3rem] flex gap-6 items-start bg-yellow-400/5 backdrop-blur-xl border border-yellow-400/10 shadow-2xl relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-64 h-64 bg-yellow-400/5 blur-[100px] rounded-full -mr-32 -mt-32" />
                <Info className="w-6 h-6 shrink-0 mt-0.5 text-yellow-400" />
                <div className="relative z-10 space-y-3">
                    <p className="font-black text-yellow-400 uppercase tracking-[0.4em] text-[10px] font-mono">EARNINGS_CORE_INTELLIGENCE_LAYER</p>
                    <p className="text-zinc-500 leading-relaxed text-sm font-medium">
                        실적 발표 시간은 현지 시장 상황에 따라 변경될 수 있습니다. '장 시작 전(BMO)'은 보통 개장 1~2시간 전, '장 마감 후(AMC)'는 폐장 직후를 의미합니다.
                        한국 주식의 경우 공시 시스템(DART)의 실시간 공시 데이터가 최우선으로 적용됩니다.
                    </p>
                </div>
            </motion.div>
        </motion.div>
    );
};

export default EarningsPage;
