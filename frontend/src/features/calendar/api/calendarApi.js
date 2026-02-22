import api from '../../../utils/api';

export const calendarApi = {
    getCalendarEvents: async () => {
        const res = await api.get('/api/calendar');
        return res.data.events || [];
    },

    getEarnings: async (params) => {
        const res = await api.get('/api/calendar/earnings', { params });
        return res.data.events || [];
    }
};
