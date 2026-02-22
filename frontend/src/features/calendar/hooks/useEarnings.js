import { useState, useEffect, useCallback } from 'react';
import { calendarApi } from '../api/calendarApi';

const DEMO_EARNINGS = [
    { ticker: 'NVDA', title: 'NVIDIA Corporation', date: new Date(Date.now() + 86400000 * 3).toISOString().split('T')[0], time: 'AMC', importance: 'high', source: 'DEMO', forecast_eps: '5.59' },
    { ticker: 'AAPL', title: 'Apple Inc.', date: new Date(Date.now() + 86400000 * 7).toISOString().split('T')[0], time: 'AMC', importance: 'high', source: 'DEMO', forecast_eps: '2.35' },
    { ticker: 'MSFT', title: 'Microsoft Corporation', date: new Date(Date.now() + 86400000 * 10).toISOString().split('T')[0], time: 'AMC', importance: 'high', source: 'DEMO', forecast_eps: '3.10' },
    { ticker: '005930', title: '삼성전자', date: new Date(Date.now() + 86400000 * 5).toISOString().split('T')[0], time: 'BMO', importance: 'high', source: 'DEMO', forecast_eps: null },
    { ticker: 'TSLA', title: 'Tesla Inc.', date: new Date(Date.now() + 86400000 * 14).toISOString().split('T')[0], time: 'AMC', importance: 'medium', source: 'DEMO', forecast_eps: '0.68' },
    { ticker: 'META', title: 'Meta Platforms', date: new Date(Date.now() + 86400000 * 21).toISOString().split('T')[0], time: 'AMC', importance: 'high', source: 'DEMO', forecast_eps: '5.25' },
];

export function useEarnings({ initialCountry = 'US', language = 'ko' } = {}) {
    const [loading, setLoading] = useState(false);
    const [events, setEvents] = useState([]);
    const [country, setCountry] = useState(initialCountry);
    const [searchQuery, setSearchQuery] = useState('');
    const [error, setError] = useState(null);
    const [fetchError, setFetchError] = useState(null);

    const fetchEarnings = useCallback(async () => {
        setLoading(true);
        setError(null);
        setFetchError(null);
        try {
            const today = new Date();
            const startStr = today.toISOString().split('T')[0];
            const end = new Date();
            end.setDate(today.getDate() + 30);
            const endStr = end.toISOString().split('T')[0];

            const fetched = await calendarApi.getEarnings({
                start_date: startStr,
                end_date: endStr,
                country: country,
                lang: language
            });

            if (fetched.length === 0) {
                setEvents(DEMO_EARNINGS);
                setFetchError('API 응답이 비어있어 데모 데이터를 표시합니다.');
            } else {
                setEvents(fetched);
            }
        } catch (err) {
            console.error('Earnings fetch error:', err);
            setEvents(DEMO_EARNINGS);
            setFetchError('백엔드 연결 실패 - 데모 데이터를 표시 중입니다. 실제 서버 실행 후 새로고침하세요.');
        } finally {
            setLoading(false);
        }
    }, [country, language]);

    useEffect(() => {
        fetchEarnings();
    }, [fetchEarnings]);

    const filteredEvents = events.filter(event =>
        event.ticker?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        event.title?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return {
        // State
        loading,
        country,
        setCountry,
        searchQuery,
        setSearchQuery,
        error,
        fetchError,

        // Computed
        filteredEvents,

        // Actions
        fetchEarnings
    };
}
