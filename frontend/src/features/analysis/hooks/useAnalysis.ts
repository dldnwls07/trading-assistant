import { useState, useEffect, useCallback } from 'react';
import { analysisApi } from '../api/analysisApi';
import { OhlcvData, AnalysisResult } from '../../../types/api';

interface UseAnalysisProps {
    initialTicker?: string;
    language?: string;
}

export function useAnalysis({ initialTicker = '', language = 'ko' }: UseAnalysisProps) {
    const [ticker, setTicker] = useState<string>(initialTicker);
    const [suggestions, setSuggestions] = useState<any[]>([]);
    const [showSuggestions, setShowSuggestions] = useState(false);

    const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
    const [hybridAnalysis, setHybridAnalysis] = useState<any | null>(null);
    const [history, setHistory] = useState<OhlcvData[]>([]);
    const [loading, setLoading] = useState(false);
    const [hybridLoading, setHybridLoading] = useState(false);
    const [error, setError] = useState<{ message: string; suggestion: string } | null>(null);
    const [selectedInterval, setSelectedInterval] = useState('1d');

    // Autocomplete effect
    useEffect(() => {
        const fetchSuggestions = async () => {
            if (ticker.length < 1) {
                setSuggestions([]);
                return;
            }
            try {
                const candidates = await analysisApi.searchSuggestions(ticker);
                setSuggestions(candidates);
            } catch (err) {
                console.error(err);
            }
        };
        const tid = setTimeout(fetchSuggestions, 300);
        return () => clearTimeout(tid);
    }, [ticker]);

    // Interval change effect
    useEffect(() => {
        if (ticker && selectedInterval && analysis && !loading) {
            handleUpdateHistory(selectedInterval);
        }
    }, [selectedInterval]);

    const handleSearch = useCallback(async (s?: string) => {
        const sym = s || ticker;
        if (!sym) return;

        setLoading(true);
        setShowSuggestions(false);
        setError(null);
        setAnalysis(null);
        setHistory([]);

        try {
            const [analReq, histReq] = await Promise.allSettled([
                analysisApi.getAnalysis(sym, language),
                analysisApi.getHistory(sym, selectedInterval)
            ]);

            let hasError = false;
            let errorMessage = '';
            let suggestion = '';

            if (analReq.status === 'fulfilled') {
                setAnalysis(analReq.value);
                setTicker(analReq.value.ticker);
            } else {
                hasError = true;
                errorMessage = `분석 데이터를 가져오지 못했습니다 (${sym})`;
                suggestion = analReq.reason?.response?.data?.detail || "올바르지 않은 티커이거나 지원하지 않는 자산일 수 있습니다.";
            }

            if (histReq.status === 'fulfilled') {
                setHistory(histReq.value);
            } else {
                hasError = true;
                if (!errorMessage) {
                    errorMessage = `차트 데이터를 가져오지 못했습니다 (${sym})`;
                    suggestion = histReq.reason?.response?.data?.detail || "해당 심볼의 시장 데이터를 수집할 수 없습니다.";
                }
                setAnalysis(null);
            }

            if (hasError) {
                setError({ message: errorMessage, suggestion });
            }

        } catch (err: any) {
            console.error(err);
            setError({
                message: "서버 통신 중 치명적인 오류가 발생했습니다.",
                suggestion: "네트워크 연결이나 API 서버 상태를 확인하고 다시 시도하세요."
            });
        } finally {
            setLoading(false);
        }
    }, [ticker, selectedInterval, language]);

    const handleUpdateHistory = useCallback(async (interval: string) => {
        if (!ticker) return;
        try {
            const data = await analysisApi.getHistory(ticker, interval);
            setHistory(data);
            setError(null);
        } catch (err: any) {
            console.error(err);
            setError({
                message: `${interval} 간격의 차트 데이터 갱신에 실패했습니다.`,
                suggestion: "네트워크 문제나 서버 응답 지연일 수 있습니다. 잠시 후 재시도하세요."
            });
            setHistory([]);
            setAnalysis(null);
        }
    }, [ticker]);

    const handleThemeSelect = useCallback((theme: any) => {
        if (theme.relatedStocks && theme.relatedStocks.length > 0) {
            const stock = theme.relatedStocks[0];
            setTicker(stock);
            handleSearch(stock);
            return stock; // returns the selected stock to parent if needed
        }
        return null;
    }, [handleSearch]);

    const handleHybridSearch = useCallback(async () => {
        if (!ticker) return;

        // 전역 지원 (US/KR 모두 허용)
        setHybridLoading(true);
        try {
            // 해당 티커에 대한 최신 주요 뉴스 및 시장 지표 컨텍스트
            const news = [
                `${ticker} 기업의 최근 재무 건전성 및 분기 실적 발표 내용`,
                `현재 ${ticker}가 속한 산업 섹터의 글로벌 공급망 및 수요 동향`,
                "국내외 매크로 경제 지표(금리, 환율)가 해당 종목에 미치는 영향"
            ];
            const result = await analysisApi.getHybridKRAnalysis(ticker, news);
            setHybridAnalysis(result);
        } catch (err) {
            console.error(err);
        } finally {
            setHybridLoading(false);
        }
    }, [ticker]);

    return {
        // State
        ticker,
        setTicker,
        suggestions,
        showSuggestions,
        setShowSuggestions,
        analysis,
        hybridAnalysis,
        history,
        loading,
        hybridLoading,
        error,
        selectedInterval,
        setSelectedInterval,

        // Actions
        handleSearch,
        handleHybridSearch,
        handleUpdateHistory,
        handleThemeSelect
    };
}
