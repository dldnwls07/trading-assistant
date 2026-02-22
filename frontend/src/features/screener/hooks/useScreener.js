import { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { screenerApi } from '../api/screenerApi';

export function useScreener(initialStyle = 'balanced', initialMarket = 'US') {
    const navigate = useNavigate();
    const [style, setStyle] = useState(initialStyle);
    const [market, setMarket] = useState(initialMarket);
    const [recommendations, setRecommendations] = useState([]);
    const [topMovers, setTopMovers] = useState({ gainers: [], losers: [] });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const [recData, topData] = await Promise.all([
                    screenerApi.getRecommendations(style, market),
                    screenerApi.getTopMovers(market)
                ]);
                setRecommendations(recData);
                setTopMovers(topData);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [market, style]);

    const topGainers = useMemo(() => topMovers.gainers?.slice(0, 5) || [], [topMovers.gainers]);
    const topLosers = useMemo(() => topMovers.losers?.slice(0, 5) || [], [topMovers.losers]);

    const handleAnalyze = useCallback((ticker) => {
        navigate(`/analysis/${encodeURIComponent(ticker)}`);
    }, [navigate]);

    return {
        // State
        style,
        setStyle,
        market,
        setMarket,
        recommendations,
        topMovers,
        loading,

        // Computed
        topGainers,
        topLosers,

        // Actions
        handleAnalyze
    };
}
