import { useEffect, useRef } from 'react';
import React from 'react';
import { LineSeries, HistogramSeries, IChartApi, ISeriesApi, SeriesOptionsCommon, LineData, HistogramData, Time } from 'lightweight-charts';

// Helper for time conversion (Consistent with StockChart.tsx)
const processTime = (time: string | number | Date): Time => {
    if (typeof time === 'string' && time.includes(':')) {
        return (new Date(time).getTime() / 1000) as Time;
    }
    return time as Time;
};

import { OhlcvData, AnalysisResult } from '../../../types/api';

interface ChartConfig {
    [key: string]: boolean;
}

interface ChartOptions {
    upColor?: string;
    downColor?: string;
    isDark?: boolean;
}

export const useChartIndicators = (
    chart: IChartApi | null,
    mainSeriesRef: React.MutableRefObject<ISeriesApi<"Candlestick"> | null>,
    data: OhlcvData[],
    chartConfig: ChartConfig,
    analysis: AnalysisResult | null,
    options: ChartOptions = {}
) => {
    const { upColor = '#ef4444', downColor = '#3b82f6', isDark = true } = options;
    const indicatorsRef = useRef<{ [key: string]: ISeriesApi<any> | any }>({});

    useEffect(() => {
        if (!chart || !data || data.length === 0) return;

        if (!indicatorsRef.current) {
            indicatorsRef.current = {};
        }
        const indicators = indicatorsRef.current;

        // Helper to add/remove series
        const updateSeries = (key: string, SeriesClass: any, seriesOptions: any, dataMapper: (d: any) => any) => {
            const shouldShow = chartConfig[key];

            if (shouldShow && !indicators[key]) {
                // Add Series
                const series = chart.addSeries(SeriesClass, seriesOptions);
                const seriesData = data.map(dataMapper)
                    .filter(item => item.value !== undefined && item.value !== null)
                    .map(item => ({ ...item, time: processTime(item.time) })); // Apply time fix

                series.setData(seriesData);
                indicators[key] = series;
            } else if (!shouldShow && indicators[key]) {
                // Remove Series
                try { chart.removeSeries(indicators[key]); } catch (e) { }
                delete indicators[key];
            } else if (shouldShow && indicators[key]) {
                // Update Data (Optional: if data changes)
                const seriesData = data.map(dataMapper)
                    .filter(item => item.value !== undefined && item.value !== null)
                    .map(item => ({ ...item, time: processTime(item.time) }));
                indicators[key].setData(seriesData);
            }
        };

        // --- 1. Overlay Indicators (SMA, EMA, Supertrend, etc.) ---
        const overlayColors: { [key: string]: string } = {
            showSMA5: '#facc15', showSMA20: '#ec4899', showSMA50: '#a855f7', showSMA200: '#10b981',
            showEMA9: '#fbbf24', showEMA20: '#f43f5e', showEMA50: '#8b5cf6', showSupertrend: '#10b981'
        };

        Object.keys(overlayColors).forEach(key => {
            const dataKey = key.replace('show', '').toLowerCase().replace('sma', 'sma_').replace('ema', 'ema_').replace('supertrend', 'supertrend');
            updateSeries(key, LineSeries, {
                color: overlayColors[key],
                lineWidth: 2,
                title: key.replace('show', ''),
                priceLineVisible: false,
                lastValueVisible: false,
            }, (d: any) => ({ time: d.time, value: d[dataKey] }));
        });

        // --- 2. Bands (BB, KC, DC) ---
        // Bollinger Bands
        ['Upper', 'Lower'].forEach(pos => {
            const key = `showBB${pos}`;
            const realConfigKey = 'showBB';
            if (chartConfig[realConfigKey] && !indicators[key]) {
                const series = chart.addSeries(LineSeries, { color: 'rgba(148, 163, 184, 0.4)', lineWidth: 1, lineStyle: 2, title: `BB ${pos}` });
                const seriesData = data.map((d: any) => ({ time: processTime(d.time), value: d[`bb_${pos.toLowerCase()}`] })).filter((d: any) => d.value);
                series.setData(seriesData);
                indicators[key] = series;
            } else if (!chartConfig[realConfigKey] && indicators[key]) {
                try { chart.removeSeries(indicators[key]); } catch (e) { }
                delete indicators[key];
            }
        });

        // --- 3. Oscillators (RSI, MACD, etc.) ---
        // RSI (Separate Pane)
        const rsiKey = 'showRSI';
        if (chartConfig[rsiKey] && !indicators[rsiKey]) {
            const rsiPaneId = 'rsi_pane'; // Note: strings as pane IDs might need layout config support or distinct chart instance sharing
            // Actually, in default lightweight-charts, separate panes require separate chart instances or 'priceScaleId'.
            // Using 'priceScaleId' creates an overlay sharing time axis but with separate Y-scale.
            // But strict visual separation is tricky. We'll use priceScaleId for now.
            const series = chart.addSeries(LineSeries, {
                color: '#a855f7',
                lineWidth: 2,
                priceScaleId: 'rsi', // Custom scale
                title: 'RSI'
            });
            chart.priceScale('rsi').applyOptions({
                scaleMargins: { top: 0.7, bottom: 0.05 },
                // visible: true 
            });
            const seriesData = data.map((d: any) => ({ time: processTime(d.time), value: d.rsi })).filter((d: any) => d.value);
            series.setData(seriesData);
            indicators[rsiKey] = series;
        } else if (!chartConfig[rsiKey] && indicators[rsiKey]) {
            try { chart.removeSeries(indicators[rsiKey]); } catch (e) { }
            delete indicators[rsiKey];
        }

        // --- 4. Volume (Bottom Pane) ---
        const volKey = 'showVolume';
        if (chartConfig[volKey] && !indicators[volKey]) {
            const series = chart.addSeries(HistogramSeries, {
                priceFormat: { type: 'volume' },
                priceScaleId: '', // Overlay on main? No, usually separate scale with margin
                title: 'Volume'
            });
            series.priceScale().applyOptions({ scaleMargins: { top: 0.8, bottom: 0 } });

            const seriesData = data.map((d: any) => ({
                time: processTime(d.time),
                value: d.volume,
                color: d.close >= d.open ? `${upColor}44` : `${downColor}44`
            }));
            series.setData(seriesData);
            indicators[volKey] = series;
        } else if (!chartConfig[volKey] && indicators[volKey]) {
            try { chart.removeSeries(indicators[volKey]); } catch (e) { }
            delete indicators[volKey];
        }

        // --- 4.5. Volume Profile (VPVR) ---
        const vpKey = 'showVolumeProfile';
        if (chartConfig[vpKey] && !indicators[vpKey] && data.length > 20) {
            // ... (Logic from before) ...
            // Simplified for brevity in this rewrite, assuming logic is sound, just typing needed.
            // Actually, I should keep the logic.
            const prices = data.map((d: any) => d.close);
            const minP = Math.min(...prices);
            const maxP = Math.max(...prices);
            const range = maxP - minP;
            const buckets = 24;
            const step = range / buckets;

            const profile = Array(buckets).fill(0).map((_, i) => ({
                midPrice: minP + (step * i) + (step / 2),
                volume: 0
            }));

            data.forEach((d: any) => {
                const idx = Math.min(buckets - 1, Math.floor((d.close - minP) / step));
                profile[idx].volume += d.volume;
            });

            const maxVol = Math.max(...profile.map(p => p.volume));

            // 3. Render as Wide Price Lines (Zones)
            indicators[vpKey] = []; // Array of PriceLines
            if (mainSeriesRef.current) {
                const peaks = profile
                    .map((p, i) => ({ ...p, idx: i }))
                    .sort((a, b) => b.volume - a.volume)
                    .slice(0, 3);

                peaks.forEach((p, i) => {
                    const line = mainSeriesRef.current!.createPriceLine({
                        price: p.midPrice,
                        color: isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)',
                        lineWidth: 1,
                        lineStyle: 3, // Dotted
                        axisLabelVisible: false,
                        title: `VP Node ${i + 1}`,
                    });
                    (indicators[vpKey] as any[]).push(line);
                });
            }
        } else if (!chartConfig[vpKey] && indicators[vpKey]) {
            if (Array.isArray(indicators[vpKey]) && mainSeriesRef.current) {
                indicators[vpKey].forEach((line: any) => {
                    try { mainSeriesRef.current!.removePriceLine(line); } catch (e) { }
                });
            }
            delete indicators[vpKey];
        }

        // --- 5. AI Analysis Visuals ---
        const srKey = 'showSupportResistance';
        // Cleanup existing PriceLines
        if (indicators['priceLines']) {
            if (Array.isArray(indicators['priceLines']) && mainSeriesRef.current) {
                indicators['priceLines'].forEach((line: any) => {
                    try { mainSeriesRef.current!.removePriceLine(line); } catch (e) { }
                });
            }
            delete indicators['priceLines'];
        }

        if (chartConfig[srKey] && analysis && analysis.key_levels && mainSeriesRef.current) {
            indicators['priceLines'] = [];
            const { levels, current_price } = analysis.key_levels;
            levels.forEach(price => {
                const isResistance = price > current_price;
                const line = mainSeriesRef.current!.createPriceLine({
                    price: price,
                    color: isResistance ? '#ef4444' : '#22c55e',
                    lineWidth: 1,
                    lineStyle: 2,
                    axisLabelVisible: true,
                    title: isResistance ? 'Res' : 'Sup',
                });
                (indicators['priceLines'] as any[]).push(line);
            });
        }

        // 5-2. Auto Trendlines
        const trendKey = 'showAutoTrendlines';
        if (indicators['trendSeries']) {
            if (Array.isArray(indicators['trendSeries'])) {
                indicators['trendSeries'].forEach((s: any) => {
                    try { chart.removeSeries(s); } catch (e) { }
                });
            }
            delete indicators['trendSeries'];
        }

        if (chartConfig[trendKey] && analysis && analysis.trendlines) {
            indicators['trendSeries'] = [];
            analysis.trendlines.forEach((trend, idx) => {
                const color = trend.type === 'uptrend' ? '#22c55e' : '#ef4444';
                const series = chart.addSeries(LineSeries, {
                    color: color,
                    lineWidth: 2,
                    lineStyle: 0,
                    lastValueVisible: false,
                    priceLineVisible: false,
                    crosshairMarkerVisible: false,
                    title: `AI Trend ${idx + 1}`
                });

                // Apply processTime for trendlines too
                const startTime = processTime(trend.start_time);
                const endTime = processTime(trend.end_time);

                // Note: lightweight-charts 4.x+ supports time sorting automatically strictly, but we must provide sorted data.
                // Assuming trend.start_time < trend.end_time usually.

                const dataPoints: LineData[] = [
                    { time: startTime, value: trend.start_price },
                    { time: endTime, value: trend.end_price }
                ].sort((a, b) => {
                    // Sorting needed if times are numbers
                    const tA = typeof a.time === 'number' ? a.time : new Date(a.time as string).getTime();
                    const tB = typeof b.time === 'number' ? b.time : new Date(b.time as string).getTime();
                    return tA - tB;
                });

                series.setData(dataPoints);
                (indicators['trendSeries'] as any[]).push(series);
            });
        }

    }, [chart, data, chartConfig, analysis, options]);

    useEffect(() => {
        return () => {
            indicatorsRef.current = {};
        };
    }, [chart]);

    return indicatorsRef;
};
