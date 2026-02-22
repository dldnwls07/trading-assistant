import api from '../../../utils/api';

export const screenerApi = {
    getRecommendations: async (style, market) => {
        const res = await api.get(`/api/screener/recommendations?style=${style}&market=${market}`);
        return res.data.recommendations || [];
    },

    getTopMovers: async (market) => {
        const res = await api.get(`/api/screener/top-movers?market=${market}`);
        return res.data || { gainers: [], losers: [] };
    }
};
