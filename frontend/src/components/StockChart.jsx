import React, { useEffect, useRef, useState } from 'react';
import { createChart, CandlestickSeries, ColorType } from 'lightweight-charts';

export const StockChart = ({ data, interval }) => {
    const chartContainerRef = useRef();
    const chartRef = useRef(null);
    const seriesRef = useRef(null);
    const [localError, setLocalError] = useState(null);

    useEffect(() => {
        if (!chartContainerRef.current) return;

        // 1. 기존 차트 정리 (React StrictMode 대응)
        if (chartRef.current) {
            try { chartRef.current.remove(); } catch (e) { }
            chartRef.current = null;
            seriesRef.current = null;
        }

        const buildChart = () => {
            try {
                console.log("[CHART] Initializing v5 Chart...");

                // 2. 차트 생성
                const chart = createChart(chartContainerRef.current, {
                    layout: {
                        background: { type: ColorType.Solid, color: '#0f172a' },
                        textColor: '#94a3b8',
                    },
                    grid: {
                        vertLines: { color: '#1e293b' },
                        horzLines: { color: '#1e293b' },
                    },
                    width: chartContainerRef.current.clientWidth,
                    height: 400,
                    timeScale: {
                        borderColor: '#1e293b',
                        timeVisible: true,
                        fixLeftEdge: true,
                    },
                });

                // 3. v5 표준 API 적용: addSeries(CandlestickSeries)
                // v5에서는 addCandlestickSeries() 함수가 direct로 존재하지 않을 수 있습니다.
                console.log("[CHART] Creating series with CandlestickSeries definition");

                // 안전장치: addCandlestickSeries가 있으면 쓰고, 없으면 addSeries(CandlestickSeries) 사용
                const series = typeof chart.addCandlestickSeries === 'function'
                    ? chart.addCandlestickSeries({
                        upColor: '#ef4444',
                        downColor: '#3b82f6',
                        borderVisible: false,
                        wickUpColor: '#ef4444',
                        wickDownColor: '#3b82f6',
                    })
                    : chart.addSeries(CandlestickSeries, {
                        upColor: '#ef4444',
                        downColor: '#3b82f6',
                        borderVisible: false,
                        wickUpColor: '#ef4444',
                        wickDownColor: '#3b82f6',
                    });

                // 4. 데이터 주입
                if (data && data.length > 0) {
                    console.log(`[CHART] Mapping ${data.length} data points to timestamps`);
                    const seenTimes = new Set();
                    const processed = data
                        .map(d => ({
                            ...d,
                            // 타임스탬프를 초 단위(UNIX)로 변환
                            time: typeof d.time === 'string' ? Math.floor(new Date(d.time).getTime() / 1000) : d.time
                        }))
                        .filter(d => {
                            if (!d.time || seenTimes.has(d.time)) return false;
                            seenTimes.add(d.time);
                            return true;
                        })
                        .sort((a, b) => a.time - b.time);

                    series.setData(processed);
                    chart.timeScale().fitContent();
                }

                chartRef.current = chart;
                seriesRef.current = series;

            } catch (err) {
                console.error("[CHART_CORE_ERROR]", err);
                setLocalError(err.message);
            }
        };

        // DOM 렌더링을 기다리기 위해 아주 짧은 지연시간 부여
        const timer = setTimeout(buildChart, 50);

        const handleResize = () => {
            if (chartRef.current && chartContainerRef.current) {
                chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
            }
        };
        window.addEventListener('resize', handleResize);

        return () => {
            clearTimeout(timer);
            window.removeEventListener('resize', handleResize);
            if (chartRef.current) {
                try { chartRef.current.remove(); } catch (e) { }
            }
        };
    }, [data]);

    if (localError) {
        return (
            <div style={{ padding: '30px', textAlign: 'center', color: '#f87171', border: '1px solid #451a1a', borderRadius: '12px', background: '#0f172a' }}>
                <p style={{ fontWeight: 'bold' }}>Chart Engine Compatibility Error</p>
                <code style={{ fontSize: '11px', display: 'block', marginTop: '10px', color: '#94a3b8' }}>{localError}</code>
            </div>
        );
    }

    return (
        <div
            ref={chartContainerRef}
            style={{ width: '100%', height: '400px', backgroundColor: '#0f172a' }}
        />
    );
};
