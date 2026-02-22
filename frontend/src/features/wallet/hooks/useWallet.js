import { useCallback } from 'react';

export function useWallet() {
    // Placeholder for future KIS API logic

    const handleConfigureApi = useCallback(() => {
        alert('설정 메뉴에서 API 키를 입력해주세요.');
    }, []);

    const mockStats = {
        totalBalance: 125480000,
        dailyProfit: 2450000,
        totalReturn: 12.4
    };

    return {
        // State & Data
        stats: mockStats,

        // Actions
        handleConfigureApi
    };
}
