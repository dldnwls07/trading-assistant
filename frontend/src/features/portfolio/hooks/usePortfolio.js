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
    const [agents, setAgents] = useState([]);
    const [selectedAgentId, setSelectedAgentId] = useState('');

    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            // First fetch agents if not loaded
            let currentAgents = agents;
            if (currentAgents.length === 0) {
                const agentsRes = await fetch('http://localhost:8000/api/agents');
                const agentsData = await agentsRes.json();
                if (agentsData.status === 'success') {
                    currentAgents = agentsData.agents;
                    setAgents(currentAgents);
                }
            }

            // Allow fetching the main virtual account or a specific agent's virtual account
            const agentIdParam = selectedAgentId === '' ? null : Number(selectedAgentId);

            const [accData, posData, rateData] = await Promise.all([
                portfolioApi.getAccount(agentIdParam),
                portfolioApi.getPositions(agentIdParam),
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
    }, [selectedAgentId, agents]);

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
        agents,
        selectedAgentId,
        setSelectedAgentId,

        // Computed
        totalValue,

        // Actions
        fetchData,
        formatNumber,
        getSymbol
    };
}
