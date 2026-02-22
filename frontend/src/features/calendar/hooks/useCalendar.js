import { useState, useEffect, useMemo, useCallback } from 'react';
import { calendarApi } from '../api/calendarApi';

const DEMO_EVENTS = [
    { date: new Date().toISOString().split('T')[0], time: '08:30', title: '미국 CPI 물가지수', category: 'inflation', country: 'US', importance: 'critical', previous: '3.1%', forecast: '3.0%', actual: '-' },
    { date: new Date().toISOString().split('T')[0], time: '14:00', title: 'FOMC 금리 결정', category: 'policy', country: 'US', importance: 'critical', previous: '5.25%', forecast: '5.25%', actual: '-' },
    { date: new Date(Date.now() + 86400000).toISOString().split('T')[0], time: '08:30', title: '미국 실업수당 청구건수', category: 'labor', country: 'US', importance: 'high', previous: '212K', forecast: '215K', actual: '-' },
    { date: new Date(Date.now() + 86400000).toISOString().split('T')[0], time: '10:00', title: '미국 소매판매', category: 'consumption', country: 'US', importance: 'high', previous: '0.4%', forecast: '0.2%', actual: '-' },
    { date: new Date(Date.now() + 172800000).toISOString().split('T')[0], time: '09:00', title: '한국 수출입통계', category: 'macro', country: 'KR', importance: 'medium', previous: '+6.2%', forecast: '+5.8%', actual: '-' },
    { date: new Date(Date.now() + 172800000).toISOString().split('T')[0], time: '21:30', title: '미국 PCE 물가지수', category: 'inflation', country: 'US', importance: 'critical', previous: '2.6%', forecast: '2.5%', actual: '-' },
];

export function useCalendar() {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('upcoming');
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [selectedImportance, setSelectedImportance] = useState('all');
    const [selectedEvent, setSelectedEvent] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [fetchError, setFetchError] = useState(null);

    const fetchEvents = useCallback(async () => {
        setLoading(true);
        setFetchError(null);
        try {
            const fetchedEvents = await calendarApi.getCalendarEvents();
            if (fetchedEvents.length === 0) {
                setEvents(DEMO_EVENTS);
                setFetchError('API 응답이 비어있어 데모 데이터를 표시합니다.');
            } else {
                setEvents(fetchedEvents);
            }
        } catch (err) {
            console.error("Failed to fetch calendar events:", err);
            setEvents(DEMO_EVENTS);
            setFetchError('백엔드 연결 실패 - 데모 데이터를 표시 중입니다. 실제 서버 실행 후 새로고침하세요.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchEvents();
    }, [fetchEvents]);

    const filteredEvents = useMemo(() => {
        const now = new Date();
        const startOfToday = new Date(now.setHours(0, 0, 0, 0));

        return events.filter(e => {
            const eDate = new Date(e.date);
            const matchesSearch = e.title.toLowerCase().includes(searchQuery.toLowerCase());
            const matchesCategory = selectedCategory && selectedCategory !== 'all' ? e.category === selectedCategory : true;
            const matchesImportance = selectedImportance && selectedImportance !== 'all' ? e.importance === selectedImportance : true;

            const isUpcoming = eDate >= startOfToday;
            const matchesTab = activeTab === 'upcoming' ? isUpcoming : !isUpcoming;

            return matchesSearch && matchesCategory && matchesImportance && matchesTab;
        }).sort((a, b) => {
            const dateA = new Date(a.date);
            const dateB = new Date(b.date);
            if (dateA - dateB !== 0) {
                return activeTab === 'upcoming' ? dateA - dateB : dateB - dateA;
            }
            const timeA = a.time === 'TBA' ? '00:00' : a.time;
            const timeB = b.time === 'TBA' ? '00:00' : b.time;
            return activeTab === 'upcoming' ? timeA.localeCompare(timeB) : timeB.localeCompare(timeA);
        });
    }, [events, searchQuery, selectedCategory, selectedImportance, activeTab]);

    const groupedEvents = useMemo(() => {
        return filteredEvents.reduce((acc, event) => {
            const date = event.date;
            if (!acc[date]) acc[date] = [];
            acc[date].push(event);
            return acc;
        }, {});
    }, [filteredEvents]);

    const handleEventClick = useCallback((event) => {
        setSelectedEvent(event);
        setIsModalOpen(true);
    }, []);

    return {
        // State
        loading,
        fetchError,
        activeTab,
        setActiveTab,
        searchQuery,
        setSearchQuery,
        selectedCategory,
        setSelectedCategory,
        selectedImportance,
        setSelectedImportance,
        selectedEvent,
        isModalOpen,
        setIsModalOpen,

        // Computed
        filteredEvents,
        groupedEvents,

        // Actions
        fetchEvents,
        handleEventClick
    };
}
