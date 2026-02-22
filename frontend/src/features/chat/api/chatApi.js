import api from '../../../utils/api';

export const chatApi = {
    getSuggestions: async () => {
        const res = await api.get('/api/chat/suggestions');
        return res.data.suggestions || [];
    },

    sendMessage: async (message) => {
        const res = await api.post('/api/chat', { message });
        return res.data.response;
    }
};
