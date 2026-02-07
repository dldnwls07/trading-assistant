import React, { useEffect, useRef, useState } from 'react';
import { createChart, CandlestickSeries, LineSeries, ColorType, HistogramSeries } from 'lightweight-charts';

/**
 * StockChart Component with AI Smart Drawing (Trendlines, Patterns, etc.)
 */
export const StockChart = ({ data, interval, options = {}, analysis = null }) => {
    const chartContainerRef = useRef();
    const chartRef = useRef(null);
    const [localError, setLocalError] = useState(null);

    const {
        showVolume = true,
        showGrid = true,
        showSMA = true,
        showBB = true,
        showRSI = false,
        showMACD = false,
        showAIQuotes = true,
        upColor = '#ef4444',
        downColor = '#3b82f6'
    } = options;

    useEffect(() => {
        if (!chartContainerRef.current) return;

        if (chartRef.current) {
            try { chartRef.current.remove(); } catch (e) { }
            chartRef.current = null;
        }

        const buildChart = () => {
            try {
                if (!data || data.length === 0) return;

                // 1. Data Cleaning
                const sortedData = [...data]
                    .map(item => ({ ...item, time: item.time || item.Date }))
                    .filter(item => item.time)
                    .sort((a, b) => new Date(a.time).getTime() - new Date(b.time).getTime());

                const finalData = [];
                const seen = new Set();
                for (const d of sortedData) {
                    let timeVal = d.time;
                    if (["1d", "1wk", "1mo", "1y"].includes(interval) && typeof timeVal === 'string') {
                        timeVal = timeVal.split(' ')[0];
                    } else if (typeof timeVal === 'string') {
                        const ts = Math.floor(new Date(timeVal).getTime() / 1000);
                        if (!isNaN(ts)) timeVal = ts;
                    }
                    if (!seen.has(timeVal)) {
                        finalData.push({ ...d, time: timeVal });
                        seen.add(timeVal);
                    }
                }

                if (finalData.length === 0) return;

                // 2. Init Chart
                const chart = createChart(chartContainerRef.current, {
                    layout: {
                        background: { type: ColorType.Solid, color: 'transparent' },
                        textColor: '#94a3b8',
                        fontSize: 11,
                        fontFamily: 'Outfit, sans-serif',
                    },
                    grid: {
                        vertLines: { color: showGrid ? 'rgba(30, 41, 59, 0.2)' : 'transparent' },
                        horzLines: { color: showGrid ? 'rgba(30, 41, 59, 0.2)' : 'transparent' },
                    },
                    width: chartContainerRef.current.clientWidth,
                    height: chartContainerRef.current.clientHeight,
                    timeScale: {
                        borderColor: 'rgba(51, 65, 85, 0.4)',
                        timeVisible: !["1d", "1wk", "1mo", "1y"].includes(interval),
                        fixLeftEdge: true,
                        barSpacing: 10,
                    },
                    rightPriceScale: {
                        borderColor: 'rgba(51, 65, 85, 0.4)',
                        scaleMargins: { top: 0.1, bottom: showRSI || showMACD ? 0.35 : 0.2 },
                    }
                });

                // 3. Main Series
                const mainSeries = chart.addSeries(CandlestickSeries, {
                    upColor, downColor, borderVisible: false, wickUpColor: upColor, wickDownColor: downColor,
                });
                mainSeries.setData(finalData);

                // --- AI SMART DRAWING CORE (NEW) ---
                if (showAIQuotes && analysis) {
                    // (1) Entry/Target/Stop Price Lines
                    if (analysis.entry_points) {
                        const { buy, target, stop } = analysis.entry_points;
                        if (buy) mainSeries.createPriceLine({ price: parseFloat(buy), color: '#fb7185', lineWidth: 2, title: 'AI ENTRY' });
                        if (target) mainSeries.createPriceLine({ price: parseFloat(target), color: '#22d3ee', lineWidth: 2, lineStyle: 2, title: 'AI TARGET' });
                        if (stop) mainSeries.createPriceLine({ price: parseFloat(stop), color: '#60a5fa', lineWidth: 2, lineStyle: 1, title: 'AI STOP' });
                    }

                    // (2) Geometric Patterns (Trendlines, ABC, Triangles)
                    // analysis.daily_analysis.patterns 또는 analysis.patterns 형태 대응
                    const patterns = analysis.patterns || (analysis.daily_analysis && analysis.daily_analysis.patterns) || [];

                    patterns.forEach((pattern, pIdx) => {
                        if (pattern.points && pattern.points.length >= 2) {
                            const patternSeries = chart.addSeries(LineSeries, {
                                color: pattern.type === 'bullish_reversal' ? '#facc15' :
                                    pattern.type === 'trend_line' ? '#10b981' :
                                        pattern.type === 'resistance_line' ? '#f43f5e' : '#94a3b8',
                                lineWidth: 2,
                                lineStyle: pattern.type.includes('line') ? 0 : 2,
                                title: pattern.name,
                                lastValueVisible: false,
                                priceLineVisible: false,
                            });

                            // 포인트 시간 전처리 (차트 시간 형식에 맞게)
                            const patternPoints = pattern.points.map(p => {
                                let t = p.time;
                                if (["1d", "1wk", "1mo", "1y"].includes(interval) && typeof t === 'string') {
                                    t = t.split(' ')[0];
                                } else if (typeof t === 'string') {
                                    const ts = Math.floor(new Date(t).getTime() / 1000);
                                    if (!isNaN(ts)) t = ts;
                                }
                                return { time: t, value: p.price };
                            }).filter(p => p.time);

                            patternSeries.setData(patternPoints);

                            // 패턴 시작점에 마커 추가
                            if (patternPoints.length > 0) {
                                mainSeries.setMarkers([
                                    ...(mainSeries.markers() || []),
                                    {
                                        time: patternPoints[0].time,
                                        position: 'aboveBar',
                                        color: '#facc15',
                                        shape: 'arrowDown',
                                        text: pattern.name,
                                    }
                                ]);
                            }
                        }
                    });
                }
                // ------------------------------------

                // 4. SMA Overlays
                if (showSMA) {
                    const sma20 = chart.addSeries(LineSeries, { color: '#fbbf24', lineWidth: 1, priceLineVisible: false, lastValueVisible: false });
                    sma20.setData(finalData.filter(d => d.sma20).map(d => ({ time: d.time, value: d.sma20 })));
                }

                // 5. Volume
                if (showVolume) {
                    const volumeSeries = chart.addSeries(HistogramSeries, { priceFormat: { type: 'volume' }, priceScaleId: '' });
                    volumeSeries.priceScale().applyOptions({ scaleMargins: { top: 0.8, bottom: 0 } });
                    volumeSeries.setData(finalData.map(d => ({
                        time: d.time, value: d.volume, color: d.close >= d.open ? upColor + '22' : downColor + '22'
                    })));
                }

                requestAnimationFrame(() => {
                    chart.timeScale().fitContent();
                    if (finalData.length > 60) {
                        chart.timeScale().setVisibleLogicalRange({ from: finalData.length - 60, to: finalData.length - 1 });
                    }
                });

                chartRef.current = chart;
            } catch (err) {
                console.error("[CHART_BUILD_ERROR]", err);
                setLocalError(err.message);
            }
        };

        const timer = setTimeout(buildChart, 100);
        const handleResize = () => { if (chartRef.current && chartContainerRef.current) chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth, height: chartContainerRef.current.clientHeight }); };
        window.addEventListener('resize', handleResize);
        return () => { clearTimeout(timer); window.removeEventListener('resize', handleResize); if (chartRef.current) chartRef.current.remove(); };
    }, [data, interval, options, analysis]);

    if (localError) return <div className="h-full flex items-center justify-center text-rose-400 text-xs font-black uppercase text-center p-4">{localError}</div>;
    return <div ref={chartContainerRef} className="w-full h-full relative" />;
};
