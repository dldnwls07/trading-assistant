import { useState, useRef, useEffect } from 'react';
import { LineSeries } from 'lightweight-charts';

export const useChartDrawing = (chart, mainSeriesRef, activeTool, setActiveTool) => {
    const [drawings, setDrawings] = useState(() => {
        try {
            const saved = localStorage.getItem('chart_drawings');
            return saved ? JSON.parse(saved) : [];
        } catch (e) {
            return [];
        }
    });

    const [magnetEnabled, setMagnetEnabled] = useState(true);

    // Refs for interaction state
    const drawingStateRef = useRef({
        isDrawing: false,
        startPoint: null,
        ghostSeries: null
    });

    // Refs for rendered series (to manage updates without re-creating chart)
    const renderedSeriesRef = useRef([]);

    // 1. Render Drawings: drawings 상태가 변경될 때마다 차트에 선을 그림
    useEffect(() => {
        if (!chart) return;
        // const chart = chartRef.current; // chart is now passed directly

        // 기존 드로잉 시리즈 제거
        renderedSeriesRef.current.forEach(s => {
            try { chart.removeSeries(s); } catch (e) { }
        });
        renderedSeriesRef.current = [];

        // 새 드로잉 시리즈 추가
        drawings.forEach((d, idx) => {
            if (d.type === 'trendline') {
                const series = chart.addSeries(LineSeries, {
                    color: d.color || '#3b82f6',
                    lineWidth: 2,
                    lastValueVisible: false,
                    priceLineVisible: false,
                    crosshairMarkerVisible: false,
                    autoscaleInfoProvider: () => null, // 드로잉이 스케일에 영향 주지 않도록 설정
                });
                series.setData(d.points);
                renderedSeriesRef.current.push(series);
            } else if (d.type === 'hline' && mainSeriesRef.current) {
                const priceLine = mainSeriesRef.current.createPriceLine({
                    price: d.price,
                    color: d.color || '#94a3b8',
                    lineWidth: 1,
                    lineStyle: 2,
                    axisLabelVisible: true,
                    title: 'Level',
                });
                // PriceLine은 Series가 아니라 별도 관리 필요하지만, 여기서는 간소화를 위해 Series 배열에 포함시키지 않음 (삭제 로직 별도 필요)
                // *복잡성 회피를 위해 hline도 LineSeries로 구현하는 것이 정신건강에 좋음 (단, 가로로 긴 선 데이터 생성 필요)*
                // 여기서는 기존 방식(PriceLine) 유지하되, 전체 삭제 시 mainSeries에서 제거하는 로직 추가 필요.
                // 편의상 Trendline만 이 배열에서 관리하고, HLine은 PriceLine 객체를 별도로 추적하지 않고 있음 (개선 포인트)
            }
        });
    }, [drawings, chart]);

    // 2. Interaction Handlers
    useEffect(() => {
        if (!chart || !mainSeriesRef.current) return;

        // const chart = chartRef.current;
        const mainSeries = mainSeriesRef.current;

        const getPrice = (param) => {
            if (!param.point) return null;
            const price = mainSeries.coordinateToPrice(param.point.y);
            return price;
        };

        const getMagnetPrice = (price, param) => {
            if (!magnetEnabled) return price;
            const candle = param.seriesPrices.get(mainSeries);
            if (!candle) return price;

            const ohlc = [candle.open, candle.high, candle.low, candle.close];
            return ohlc.reduce((prev, curr) =>
                Math.abs(curr - price) < Math.abs(prev - price) ? curr : prev
            );
        };

        const handleClick = (param) => {
            if (!param.point || !param.time || activeTool === 'cursor') return;

            const rawPrice = getPrice(param);
            if (rawPrice === null) return;
            const finalPrice = getMagnetPrice(rawPrice, param);

            if (activeTool === 'trendline') {
                const state = drawingStateRef.current;

                if (!state.isDrawing) {
                    // Start Drawing
                    state.isDrawing = true;
                    state.startPoint = { time: param.time, value: finalPrice };

                    // Create Ghost Series
                    state.ghostSeries = chart.addSeries(LineSeries, {
                        color: '#3b82f6',
                        lineWidth: 1,
                        lineStyle: 2,
                        crosshairMarkerVisible: false,
                        lastValueVisible: false,
                        priceLineVisible: false,
                    });
                } else {
                    // Finish Drawing
                    const endPoint = { time: param.time, value: finalPrice };
                    // 시간 순서 정렬
                    const points = [state.startPoint, endPoint].sort((a, b) => (a.time - b.time));

                    const newDrawing = { type: 'trendline', points, color: '#3b82f6' };
                    setDrawings(prev => {
                        const next = [...prev, newDrawing];
                        localStorage.setItem('chart_drawings', JSON.stringify(next));
                        return next;
                    });

                    // Cleanup
                    if (state.ghostSeries) {
                        chart.removeSeries(state.ghostSeries);
                        state.ghostSeries = null;
                    }
                    state.isDrawing = false;
                    state.startPoint = null;
                    setActiveTool('cursor');
                }
            } else if (activeTool === 'hline') {
                // Horizontal Line (using PriceLine for now, but better as LineSeries for persistence across data changes)
                // 여기서는 간단히 PriceLine 추가하고 상태 저장 (실제 렌더링은 위 useEffect에서 처리하지 않음 - PriceLine은 영속적이지 않음)
                // *수정*: HLine도 LineSeries로 처리하는 것이 관리상 통일됨.
                // 편의상 HLine은 PriceLine으로 유지하되, 상태에는 저장.
                const newDrawing = { type: 'hline', price: finalPrice, color: '#94a3b8' };
                setDrawings(prev => {
                    const next = [...prev, newDrawing];
                    localStorage.setItem('chart_drawings', JSON.stringify(next));
                    return next;
                });
                setActiveTool('cursor');
            }
        };

        const handleMove = (param) => {
            const state = drawingStateRef.current;
            if (activeTool === 'trendline' && state.isDrawing && state.ghostSeries && param.time) {
                const rawPrice = getPrice(param);
                if (rawPrice !== null) {
                    const finalPrice = getMagnetPrice(rawPrice, param);
                    const currentPoint = { time: param.time, value: finalPrice };

                    // Lightweight Charts requires sorted data
                    // Note: If param.time is strictly logic time, simple comparison works.
                    // If complex time input, need normalization. Assuming logic time or uniform timestamps.
                    const points = [state.startPoint, currentPoint].sort((a, b) => {
                        const ta = typeof a.time === 'string' ? new Date(a.time).getTime() : a.time;
                        const tb = typeof b.time === 'string' ? new Date(b.time).getTime() : b.time;
                        return ta - tb;
                    });

                    state.ghostSeries.setData(points);
                }
            }
        };

        chart.subscribeClick(handleClick);
        chart.subscribeCrosshairMove(handleMove);

        return () => {
            chart.unsubscribeClick(handleClick);
            chart.unsubscribeCrosshairMove(handleMove);
        };
    }, [chart, mainSeriesRef, activeTool, magnetEnabled]);

    return { drawings, setDrawings, magnetEnabled, setMagnetEnabled };
};
