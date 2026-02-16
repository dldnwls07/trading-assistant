import { InvestmentTheme } from '../types';

export const MOCK_THEMES: InvestmentTheme[] = [
    {
        id: 'ai-semicon',
        name: 'AI & 반도체',
        description: '차세대 AI 혁명을 주도하는 고성능 반도체 및 인프라 기업',
        icon: 'cpu',
        tickers: ['NVDA', 'AMD', 'TSM', 'AVGO', 'MU'],
        avgPerformance: 2.5,
        momentumScore: 92,
        tags: ['High Growth', 'Tech', 'AI']
    },
    {
        id: 'k-battery',
        name: 'K-배터리 밸류체인',
        description: '전기차 시장 확대를 이끄는 2차전지 소재 및 제조 기업',
        icon: 'battery-charging',
        tickers: ['373220.KS', '006400.KS', '051910.KS', '247540.KQ'],
        avgPerformance: -0.8,
        momentumScore: 45,
        tags: ['EV', 'Energy', 'Cyclical']
    },
    {
        id: 'defense-aero',
        name: '방산 & 우주항공',
        description: '지정학적 리스크 증가와 우주 산업 성장의 수혜주',
        icon: 'rocket',
        tickers: ['LMT', 'RTX', '012450.KS', '042660.KS'],
        avgPerformance: 1.2,
        momentumScore: 78,
        tags: ['Defense', 'Stable', 'Geopolitics']
    },
    {
        id: 'bio-health',
        name: '혁신 바이오 & 헬스케어',
        description: 'GLP-1 비만 치료제 및 알츠하이머 신약 개발 기업',
        icon: 'activity',
        tickers: ['LLY', 'NVO', '207940.KS'],
        avgPerformance: 0.5,
        momentumScore: 65,
        tags: ['Bio', 'Pharma', 'Defensive']
    }
];
