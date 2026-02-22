import { useState, useEffect, useCallback } from 'react';
import { portfolioApi } from '../api/portfolioApi';

export function usePortfolio() {
    const [activeTab, setActiveTab] = useState('manual');
    const [displayCurrency, setDisplayCurrency] = useState('KRW');

    const [account, setAccount] = useState(null);
    const [positions, setPositions] = useState([]);
    const [exchangeRate, setExchangeRate] = useState(1350);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const [accData, posData, rateData] = await Promise.all([
                portfolioApi.getAccount(),
                portfolioApi.getPositions(),
                portfolioApi.getExchangeRate()
            ]);
            setAccount(accData);
            setPositions(posData);
            setExchangeRate(rateData);
        } catch (err) {
            console.error("Data fetch error:", err);
            setError("Failed to load portfolio data. Please try again.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (activeTab === 'virtual') {
            fetchData();
        }
    }, [activeTab, fetchData]);

    const formatNumber = useCallback((num, decimals = 0) => {
        if (!num && num !== 0) return '0';
        return num.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
    }, []);

    const getSymbol = useCallback(() => displayCurrency === 'KRW' ? '₩' : '$', [displayCurrency]);

    const totalValue = activeTab === 'manual'
        ? 0
        : (positions.reduce((acc, p) => acc + p.total_value_krw, 0) + (account?.balance || 0));

    return {
        // State
        activeTab,
        setActiveTab,
        displayCurrency,
        setDisplayCurrency,
        account,
        positions,
        exchangeRate,
        loading,
        error,

        // Computed
        totalValue,

        // Actions
        fetchData,
        formatNumber,
        getSymbol
    };
}
