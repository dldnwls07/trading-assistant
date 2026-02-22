import api from '../../../utils/api';

export const portfolioApi = {
    getAccount: async () => {
        const res = await api.get('/api/virtual/account');
        return res.data;
    },

    getPositions: async () => {
        const res = await api.get('/api/virtual/positions');
        return res.data.positions || [];
    },

    getExchangeRate: async () => {
        const res = await api.get('/api/exchange-rate');
        return res.data.rate;
    }
};
