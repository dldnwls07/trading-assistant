import axios from 'axios';
import { OhlcvData, AnalysisResult } from '../../../types/api';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const API_KEY = import.meta.env.VITE_API_KEY || "trading-assistant-secret-2024";

const AXIOS_CONFIG = {
    headers: { 'X-API-Key': API_KEY }
};

export const analysisApi = {
    searchSuggestions: async (query: string) => {
        if (!query) return [];
        const res = await axios.get(`${API_BASE}/search?query=${encodeURIComponent(query)}`, AXIOS_CONFIG);
        return res.data.candidates || [];
    },

    getAnalysis: async (ticker: string, language: string) => {
        const res = await axios.get(`${API_BASE}/analyze/${encodeURIComponent(ticker)}?lang=${language}`, AXIOS_CONFIG);
        return res.data;
    },

    getHistory: async (ticker: string, interval: string) => {
        const res = await axios.get(`${API_BASE}/history/${encodeURIComponent(ticker)}?interval=${interval}`, AXIOS_CONFIG);
        return res.data.data;
    }
};
