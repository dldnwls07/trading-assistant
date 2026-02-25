import api from '../../../utils/api';

export const portfolioApi = {
    getAccount: async (agentId) => {
        const url = agentId ? `/api/virtual/account?agent_id=${agentId}` : '/api/virtual/account';
        const res = await api.get(url);
        return res.data;
    },

    getPositions: async (agentId) => {
        const url = agentId ? `/api/virtual/positions?agent_id=${agentId}` : '/api/virtual/positions';
        const res = await api.get(url);
        return res.data.positions || [];
    },

    getExchangeRate: async () => {
        const res = await api.get('/api/exchange-rate');
        return res.data.rate;
    }
};
