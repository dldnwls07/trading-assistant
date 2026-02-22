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

        // 한국 종목 확인 (.KS, .KQ 또는 6자리 숫자)
        const isKR = ticker.endsWith('.KS') || ticker.endsWith('.KQ') || (/^\d{6}$/.test(ticker));
        if (!isKR) {
            alert("하이브리드 분석은 현재 한국 종목(KOSPI/KOSDAQ)만 지원합니다.");
            return;
        }

        setHybridLoading(true);
        try {
            // 샘플 뉴스 또는 실제 뉴스 가져오기 logic (여기는 간단히 기존 분석 데이터의 뉴스를 활용하거나 빈 목록 전달)
            const news = ["최신 주요 경영 공시 및 시장 수급 동향", "업황 전망 및 주요 경쟁사 실적 분석"];
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
