import { InvestmentTheme } from '../types';

export const MOCK_THEMES: InvestmentTheme[] = [
    {
        id: 'ai-semicon',
        name: 'AI & 반도체',
        description: '차세대 AI 혁명을 주도하는 고성능 반도체 및 데이터센터 인프라 기업. GPU 수요 폭발로 구조적 성장 지속',
        icon: 'cpu',
        tickers: ['NVDA', 'AMD', 'TSM', 'AVGO', 'MU'],
        avgPerformance: 2.5,
        momentumScore: 92,
        tags: ['High Growth', 'Tech', 'AI'],
        recommendedEtfs: [
            { ticker: 'SOXX', name: 'iShares Semiconductor ETF', description: '반도체 대형주 집중' },
            { ticker: 'SMH', name: 'VanEck Semiconductor ETF', description: '글로벌 반도체 추적' },
            { ticker: 'BOTZ', name: 'Global X Robotics & AI ETF', description: 'AI+로봇 융합' }
        ]
    },
    {
        id: 'k-battery',
        name: 'K-배터리 밸류체인',
        description: '전기차 시장 확대를 이끄는 2차전지 셀·소재·장비 기업. 한국 EV 배터리 생태계의 핵심',
        icon: 'battery-charging',
        tickers: ['373220.KS', '006400.KS', '051910.KS', '247540.KQ'],
        avgPerformance: -0.8,
        momentumScore: 45,
        tags: ['EV', 'Energy', 'Cyclical'],
        recommendedEtfs: [
            { ticker: 'LIT', name: 'Global X Lithium & Battery Tech ETF', description: '리튬·배터리 글로벌' },
            { ticker: 'BATT', name: 'Amplify Lithium & Battery Technology ETF', description: '배터리 기술 전반' },
            { ticker: 'DRIV', name: 'Global X Autonomous & EV ETF', description: '자율주행+EV 융합' }
        ]
    },
    {
        id: 'defense-aero',
        name: '방산 & 우주항공',
        description: '지정학적 리스크 증가와 우주 산업 성장의 수혜주. NATO 방산 예산 확대 수혜',
        icon: 'rocket',
        tickers: ['LMT', 'RTX', 'NOC', '012450.KS', '042660.KS'],
        avgPerformance: 1.2,
        momentumScore: 78,
        tags: ['Defense', 'Stable', 'Geopolitics'],
        recommendedEtfs: [
            { ticker: 'ITA', name: 'iShares U.S. Aerospace & Defense ETF', description: '미국 방산 대표' },
            { ticker: 'XAR', name: 'SPDR S&P Aerospace & Defense ETF', description: '항공우주+방산' },
            { ticker: 'ARKVX', name: 'ARK Space Exploration ETF', description: '우주 탐사 특화' }
        ]
    },
    {
        id: 'bio-health',
        name: '혁신 바이오 & 헬스케어',
        description: 'GLP-1 비만 치료제·알츠하이머 신약 개발 선두 기업. 고령화 사회 구조적 수혜 섹터',
        icon: 'activity',
        tickers: ['LLY', 'NVO', 'ABBV', '207940.KS', '068270.KS'],
        avgPerformance: 0.5,
        momentumScore: 65,
        tags: ['Bio', 'Pharma', 'Defensive'],
        recommendedEtfs: [
            { ticker: 'XBI', name: 'SPDR S&P Biotech ETF', description: '바이오텍 소형주 포함' },
            { ticker: 'IBB', name: 'iShares Biotechnology ETF', description: '바이오텍 대형주 중심' },
            { ticker: 'XLV', name: 'Health Care Select Sector SPDR', description: '헬스케어 전체 섹터' }
        ]
    },
    {
        id: 'cloud-saas',
        name: '클라우드 & SaaS',
        description: '기업용 클라우드 전환 가속화로 구독 매출이 폭발적으로 성장 중인 소프트웨어 기업',
        icon: 'cloud',
        tickers: ['MSFT', 'CRM', 'SNOW', 'DDOG', 'NOW'],
        avgPerformance: 1.8,
        momentumScore: 80,
        tags: ['Cloud', 'SaaS', 'Tech'],
        recommendedEtfs: [
            { ticker: 'WCLD', name: 'WisdomTree Cloud Computing Fund', description: '클라우드 컴퓨팅 특화' },
            { ticker: 'CLOU', name: 'Global X Cloud Computing ETF', description: 'SaaS·PaaS 기업 집중' },
            { ticker: 'IGV', name: 'iShares Expanded Tech-Software ETF', description: '소프트웨어 대형주' }
        ]
    },
    {
        id: 'clean-energy',
        name: '클린에너지 & 태양광',
        description: '탄소중립 정책과 전력 수요 급증에 따른 태양광·풍력·수소 에너지 기업의 성장',
        icon: 'zap',
        tickers: ['ENPH', 'FSLR', 'NEE', '091990.KS', '263920.KQ'],
        avgPerformance: -0.3,
        momentumScore: 55,
        tags: ['Green', 'ESG', 'Energy'],
        recommendedEtfs: [
            { ticker: 'ICLN', name: 'iShares Global Clean Energy ETF', description: '글로벌 클린에너지 대표' },
            { ticker: 'QCLN', name: 'First Trust NASDAQ Clean Edge Green ETF', description: '청정에너지 기술' },
            { ticker: 'TAN', name: 'Invesco Solar ETF', description: '태양광 특화' }
        ]
    },
    {
        id: 'fintech',
        name: '핀테크 & 디지털금융',
        description: '전통 금융의 디지털 전환과 결제 인프라 혁신을 이끄는 기업. 블록체인 포함',
        icon: 'trending-up',
        tickers: ['V', 'MA', 'PYPL', 'SQ', 'COIN'],
        avgPerformance: 1.1,
        momentumScore: 70,
        tags: ['Fintech', 'Payments', 'Crypto'],
        recommendedEtfs: [
            { ticker: 'FINX', name: 'Global X FinTech ETF', description: '핀테크 글로벌 대표' },
            { ticker: 'ARKF', name: 'ARK Fintech Innovation ETF', description: '혁신 핀테크 집중' },
            { ticker: 'IPAY', name: 'ETFMG Prime Mobile Payments ETF', description: '모바일 결제 특화' }
        ]
    },
    {
        id: 'robotics-auto',
        name: '로보틱스 & 자율주행',
        description: '제조 자동화·물류 로봇·자율주행 소프트웨어로 인건비 대체 시장을 선도하는 기업',
        icon: 'cpu',
        tickers: ['TSLA', 'ABB', 'ISRG', '277810.KS', '090430.KS'],
        avgPerformance: 0.9,
        momentumScore: 72,
        tags: ['Robotics', 'Auto', 'Deep Tech'],
        recommendedEtfs: [
            { ticker: 'ROBO', name: 'ROBO Global Robotics & Automation ETF', description: '로보틱스 글로벌 대표' },
            { ticker: 'ARKG', name: 'ARK Autonomous Technology & Robotics ETF', description: '자율화 기술 집중' },
            { ticker: 'KROP', name: 'Global X AgTech & Food Innovation ETF', description: '농업 자동화 포함' }
        ]
    },
    {
        id: 'cybersecurity',
        name: '사이버보안',
        description: 'AI 기반 사이버 위협 급증으로 보안 솔루션 수요가 폭발적으로 증가 중인 방어적 성장주',
        icon: 'shield',
        tickers: ['CRWD', 'PANW', 'ZS', 'FTNT', 'S'],
        avgPerformance: 1.6,
        momentumScore: 82,
        tags: ['Security', 'Defensive', 'AI'],
        recommendedEtfs: [
            { ticker: 'CIBR', name: 'First Trust NASDAQ Cybersecurity ETF', description: '사이버보안 대표 ETF' },
            { ticker: 'HACK', name: 'ETFMG Prime Cyber Security ETF', description: '글로벌 사이버보안' },
            { ticker: 'BUG', name: 'Global X Cybersecurity ETF', description: '보안 기술 집중' }
        ]
    },
    {
        id: 'reit-infra',
        name: '데이터센터 리츠',
        description: 'AI 컴퓨팅 수요 폭발로 데이터센터·인프라 리츠가 구조적 성장세 유지 중',
        icon: 'server',
        tickers: ['EQIX', 'AMT', 'SBAC', 'DLR', 'CCI'],
        avgPerformance: 0.7,
        momentumScore: 68,
        tags: ['REIT', 'Infrastructure', 'Income'],
        recommendedEtfs: [
            { ticker: 'VNQ', name: 'Vanguard Real Estate ETF', description: '미국 리츠 전체' },
            { ticker: 'XLRE', name: 'Real Estate Select Sector SPDR ETF', description: 'S&P500 리츠 섹터' },
            { ticker: 'SRVR', name: 'Pacer Benchmark Data & Infrastructure ETF', description: '데이터센터 특화' }
        ]
    },
    {
        id: 'commodities',
        name: '원자재 & 에너지',
        description: '인플레이션 헷지와 지정학적 리스크에 강한 원유·천연가스·금속 관련 기업',
        icon: 'bar-chart',
        tickers: ['XOM', 'CVX', 'COP', 'FCX', 'NEM'],
        avgPerformance: 0.4,
        momentumScore: 58,
        tags: ['Commodities', 'Inflation Hedge', 'Cyclical'],
        recommendedEtfs: [
            { ticker: 'XLE', name: 'Energy Select Sector SPDR ETF', description: '미국 에너지 섹터' },
            { ticker: 'GLD', name: 'SPDR Gold Shares ETF', description: '금 직접 추종' },
            { ticker: 'DJP', name: 'iPath Bloomberg Commodity Index ETN', description: '원자재 다각화' }
        ]
    },
    {
        id: 'consumer-brand',
        name: '소비재 & 프리미엄 브랜드',
        description: '경기 회복기에 강한 명품·소비재 기업. 중국 소비 반등의 주요 수혜 섹터',
        icon: 'shopping-bag',
        tickers: ['LVMHF', 'NKE', 'LULU', '000660.KS', 'MC.PA'],
        avgPerformance: 0.3,
        momentumScore: 52,
        tags: ['Consumer', 'Luxury', 'Recovery'],
        recommendedEtfs: [
            { ticker: 'XLY', name: 'Consumer Discretionary Select Sector SPDR', description: '소비재 섹터 전체' },
            { ticker: 'LUXE', name: 'Global X MSCI SuperDividend Consumer Discretionary ETF', description: '고배당 소비재' },
            { ticker: 'FDIS', name: 'Fidelity MSCI Consumer Discretionary Index ETF', description: '저비용 소비재' }
        ]
    }
];
