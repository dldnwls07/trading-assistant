import React, { useEffect, useRef, useState, useMemo } from 'react';
import { createChart, CandlestickSeries, LineSeries, ColorType, HistogramSeries } from 'lightweight-charts';
import { Maximize2, Minimize2, MousePointer2, Pencil, Trash2, LineChart, LayoutGrid, ArrowUpRight } from 'lucide-react';

/**
 * QuantCore Ultra Chart System
 * Supports AI Patterns, Multiple Indicator Panes, Drawing Tools, and Fullscreen.
 */
export const StockChart = ({ data, interval, options = {}, analysis = null }) => {
    const chartContainerRef = useRef();
    const chartRef = useRef(null);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [drawingMode, setDrawingMode] = useState(null); // 'line', 'text', null
    const [drawings, setDrawings] = useState([]);
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

    const [hLines, setHLines] = useState([]); // Manual Horizontal Lines
    const [tLines, setTLines] = useState([]); // Manual Trend Lines (pairs of {t, p})
    const [drawingState, setDrawingState] = useState(null); // { startPoint: {time, price} }

    // Fullscreen Toggle
    const toggleFullscreen = () => {
        if (!document.fullscreenElement) {
            chartContainerRef.current.requestFullscreen();
            setIsFullscreen(true);
        } else {
            document.exitFullscreen();
            setIsFullscreen(false);
        }
    };

    useEffect(() => {
        const handleFsChange = () => setIsFullscreen(!!document.fullscreenElement);
        document.addEventListener('fullscreenchange', handleFsChange);
        return () => document.removeEventListener('fullscreenchange', handleFsChange);
    }, []);

    useEffect(() => {
        if (!chartContainerRef.current) return;

        if (chartRef.current) {
            try { chartRef.current.remove(); } catch (e) { }
        }

        const buildChart = () => {
            try {
                if (!data || data.length === 0) return;

                const formatTime = (raw) => {
                    const dateObj = new Date(raw);
                    const ts = dateObj.getTime();
                    if (isNaN(ts)) return null;
                    if (["1d", "1wk", "1mo", "1y"].includes(interval)) {
                        const Y = dateObj.getFullYear();
                        const M = String(dateObj.getMonth() + 1).padStart(2, '0');
                        const D = String(dateObj.getDate()).padStart(2, '0');
                        return `${Y}-${M}-${D}`;
                    }
                    return Math.floor(ts / 1000);
                };

                // (1) Prepare and Sort Data with Extreme Precision
                const processed = data
                    .map(d => ({ ...d, _ts: new Date(d.time || d.Date).getTime() }))
                    .filter(d =>
                        !isNaN(d._ts) &&
                        typeof d.open === 'number' &&
                        typeof d.high === 'number' &&
                        typeof d.low === 'number' &&
                        typeof d.close === 'number'
                    )
                    .sort((a, b) => a._ts - b._ts);

                const finalData = [];
                const seenTimes = new Set();

                for (const d of processed) {
                    const timeVal = formatTime(d.time || d.Date);
                    if (timeVal && !seenTimes.has(timeVal)) {
                        finalData.push({ ...d, time: timeVal });
                        seenTimes.add(timeVal);
                    }
                }

                if (finalData.length === 0) return;

                const chart = createChart(chartContainerRef.current, {
                    layout: {
                        background: { type: ColorType.Solid, color: '#020617' },
                        textColor: '#94a3b8',
                        fontSize: 11,
                        fontFamily: 'Outfit, sans-serif',
                    },
                    grid: {
                        vertLines: { color: showGrid ? 'rgba(30, 41, 59, 0.3)' : 'transparent' },
                        horzLines: { color: showGrid ? 'rgba(30, 41, 59, 0.3)' : 'transparent' },
                    },
                    width: chartContainerRef.current.clientWidth,
                    height: chartContainerRef.current.clientHeight,
                    timeScale: {
                        borderColor: 'rgba(51, 65, 85, 0.4)',
                        timeVisible: true,
                        fixLeftEdge: true,
                    },
                    rightPriceScale: {
                        borderColor: 'rgba(51, 65, 85, 0.4)',
                        scaleMargins: {
                            top: 0.1,
                            bottom: (showRSI && showMACD) ? 0.45 : (showRSI || showMACD) ? 0.3 : 0.2
                        },
                    }
                });

                // Main Candlestick - Revert to standard v5 API
                const mainSeries = chart.addSeries(CandlestickSeries, {
                    upColor, downColor, borderVisible: false, wickUpColor: upColor, wickDownColor: downColor,
                });
                mainSeries.setData(finalData);

                // --- Manual Horizontal Lines ---
                hLines.forEach((price, idx) => {
                    mainSeries.createPriceLine({
                        price: price,
                        color: options.themeColor || '#22d3ee',
                        lineWidth: 1,
                        lineStyle: 1,
                        title: `HLINE ${idx + 1}`,
                    });
                });

                // --- Manual Trend Lines ---
                tLines.forEach((tl, idx) => {
                    const tlSeries = chart.addSeries(LineSeries, {
                        color: options.themeColor || '#22d3ee',
                        lineWidth: 2,
                        lastValueVisible: false,
                        priceLineVisible: false,
                        crosshairMarkerVisible: false,
                    });
                    tlSeries.setData([
                        { time: tl.start.time, value: tl.start.price },
                        { time: tl.end.time, value: tl.end.price }
                    ]);
                });

                // --- Drawing Preview Series ---
                const previewSeries = chart.addSeries(LineSeries, {
                    color: (options.themeColor || '#22d3ee') + '88',
                    lineWidth: 1,
                    lineStyle: 2,
                    lastValueVisible: false,
                    priceLineVisible: false,
                    crosshairMarkerVisible: false,
                });

                // --- AI Pattern Drawing (Enhanced) ---
                if (showAIQuotes && analysis) {
                    // entry points
                    const { buy, target, stop } = analysis.entry_points || {};
                    if (buy) mainSeries.createPriceLine({ price: parseFloat(buy), color: '#fb7185', lineWidth: 2, title: 'AI ENTRY' });
                    if (target) mainSeries.createPriceLine({ price: parseFloat(target), color: '#22d3ee', lineWidth: 2, lineStyle: 2, title: 'AI TARGET' });
                    if (stop) mainSeries.createPriceLine({ price: parseFloat(stop), color: '#60a5fa', lineWidth: 2, lineStyle: 1, title: 'AI STOP' });

                    // complex patterns
                    const patterns = analysis.patterns || (analysis.daily_analysis && analysis.daily_analysis.patterns) || [];
                    const allMarkers = [];

                    patterns.forEach((pattern) => {
                        if (pattern.points && pattern.points.length >= 2) {
                            const isBullish = pattern.type.includes('bullish') || pattern.name.includes('Support');
                            const isBearish = pattern.type.includes('bearish') || pattern.name.includes('Resistance');

                            const patternSeries = chart.addSeries(LineSeries, {
                                color: isBullish ? '#10b981' : isBearish ? '#f43f5e' : '#facc15',
                                lineWidth: 2,
                                lineStyle: pattern.type.includes('line') ? 0 : 2,
                                title: pattern.name,
                                crosshairMarkerVisible: true,
                                lastValueVisible: false,
                                priceLineVisible: false,
                            });

                            const pts = pattern.points
                                .map(p => ({ time: formatTime(p.time), _ts: new Date(p.time).getTime(), value: p.price }))
                                .filter(p => p.time && !isNaN(p._ts))
                                .sort((a, b) => a._ts - b._ts);

                            const uniquePts = [];
                            const seenPatternTimes = new Set();
                            for (const pt of pts) {
                                if (!seenPatternTimes.has(pt.time)) {
                                    uniquePts.push({ time: pt.time, value: pt.value });
                                    seenPatternTimes.add(pt.time);
                                }
                            }

                            if (uniquePts.length >= 2) {
                                patternSeries.setData(uniquePts);
                                // Collect markers
                                uniquePts.forEach((p, i) => {
                                    allMarkers.push({
                                        time: p.time,
                                        position: i === 0 ? 'aboveBar' : 'belowBar',
                                        color: isBullish ? '#10b981' : isBearish ? '#f43f5e' : '#facc15',
                                        shape: i === 0 ? 'arrowDown' : 'circle',
                                        text: i === 0 ? pattern.name : '',
                                    });
                                });
                            }
                        }
                    });

                    // VERY Safe Marker Injection
                    if (allMarkers.length > 0 && mainSeries && typeof mainSeries.setMarkers === 'function') {
                        try {
                            const validMarkers = allMarkers
                                .filter(m => m.time != null)
                                .sort((a, b) => {
                                    const getTs = (t) => (typeof t === 'number' ? t : new Date(t).getTime() / 1000);
                                    return getTs(a.time) - getTs(b.time);
                                });
                            mainSeries.setMarkers(validMarkers);
                        } catch (mErr) {
                            console.warn("Marker apply failed safely:", mErr);
                        }
                    }
                }

                // Indicators
                // RSI Pane (Independent Scale)
                if (showRSI) {
                    const rsiSeries = chart.addSeries(LineSeries, {
                        color: '#a855f7', lineWidth: 1.5, priceScaleId: 'rsi-pane', title: 'RSI'
                    });
                    rsiSeries.setData(finalData.filter(d => d.rsi).map(d => ({ time: d.time, value: d.rsi })));
                    chart.priceScale('rsi-pane').applyOptions({
                        scaleMargins: { top: 0.7, bottom: 0.15 },
                        borderColor: 'rgba(51, 65, 85, 0.4)',
                    });
                }

                // MACD Pane
                if (showMACD) {
                    const macdHist = chart.addSeries(HistogramSeries, {
                        priceScaleId: 'macd-pane', title: 'MACD Hist'
                    });
                    macdHist.setData(finalData.filter(d => d.macd_hist !== undefined).map(d => ({
                        time: d.time, value: d.macd_hist,
                        color: d.macd_hist >= 0 ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)'
                    })));
                    chart.priceScale('macd-pane').applyOptions({
                        scaleMargins: { top: 0.85, bottom: 0 },
                        borderColor: 'rgba(51, 65, 85, 0.4)',
                    });
                }

                // Volume
                if (showVolume) {
                    const volumeSeries = chart.addSeries(HistogramSeries, {
                        priceFormat: { type: 'volume' }, priceScaleId: ''
                    });
                    volumeSeries.priceScale().applyOptions({ scaleMargins: { top: 0.8, bottom: 0 } });
                    volumeSeries.setData(finalData.map(d => ({
                        time: d.time, value: d.volume, color: d.close >= d.open ? upColor + '22' : downColor + '22'
                    })));
                }

                // Handle Clicks for Drawing
                chart.subscribeClick((param) => {
                    if (!param.time || !param.point) return;
                    const price = mainSeries.coordinateToPrice(param.point.y);

                    if (drawingMode === 'hline') {
                        setHLines(prev => [...prev, price]);
                        setDrawingMode(null);
                    } else if (drawingMode === 'trend') {
                        if (!drawingState) {
                            setDrawingState({ start: { time: param.time, price } });
                        } else {
                            setTLines(prev => [...prev, { start: drawingState.start, end: { time: param.time, price } }]);
                            setDrawingState(null);
                            setDrawingMode(null);
                        }
                    }
                });

                chart.subscribeCrosshairMove((param) => {
                    if (drawingMode === 'trend' && drawingState && param.time && param.point) {
                        const price = mainSeries.coordinateToPrice(param.point.y);
                        previewSeries.setData([
                            { time: drawingState.start.time, value: drawingState.start.price },
                            { time: param.time, value: price }
                        ]);
                    } else {
                        previewSeries.setData([]);
                    }
                });

                chartRef.current = chart;
                requestAnimationFrame(() => {
                    chart.timeScale().fitContent();
                });
            } catch (err) {
                console.error(err);
                setLocalError(err.message);
            }
        };

        const timer = setTimeout(buildChart, 100);
        const resizer = () => { if (chartRef.current) chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth, height: chartContainerRef.current.clientHeight }); };
        window.addEventListener('resize', resizer);
        return () => {
            clearTimeout(timer);
            window.removeEventListener('resize', resizer);
            if (chartRef.current) {
                chartRef.current.remove();
                chartRef.current = null;
            }
        };
    }, [data, interval, options, analysis, isFullscreen, hLines, tLines, drawingMode, drawingState]);

    return (
        <div ref={chartContainerRef} className={`w-full h-full relative group bg-[#020617] ${drawingMode ? 'cursor-crosshair' : ''}`}>
            {/* Ultra Toolbar */}
            <div className="absolute top-4 left-4 z-20 flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="flex bg-slate-900/90 backdrop-blur-xl border border-slate-800 p-1.5 rounded-2xl shadow-2xl items-center gap-1">
                    <button onClick={toggleFullscreen} title="전체화면" className="p-2 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-white transition-all">
                        {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
                    </button>
                    <div className="w-[1px] h-4 bg-slate-800 mx-1"></div>
                    <button onClick={() => { setDrawingMode(drawingMode === 'hline' ? null : 'hline'); setDrawingState(null); }} title="수평선 (H)" className={`p-2 rounded-xl transition-all ${drawingMode === 'hline' ? 'bg-cyan-500 text-slate-900' : 'text-slate-400 hover:bg-slate-800'}`}>
                        <div className="w-4 h-[2px] bg-current"></div>
                    </button>
                    <button onClick={() => { setDrawingMode(drawingMode === 'trend' ? null : 'trend'); setDrawingState(null); }} title="추세선 (T)" className={`p-2 rounded-xl transition-all ${drawingMode === 'trend' ? 'bg-cyan-500 text-slate-900' : 'text-slate-400 hover:bg-slate-800'}`}>
                        <ArrowUpRight size={16} />
                    </button>
                    <button onClick={() => { setHLines([]); setTLines([]); setDrawingState(null); }} title="작도 지우기" className="p-2 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 rounded-xl transition-all">
                        <Trash2 size={16} />
                    </button>
                </div>
            </div>

            {/* Pane Labels */}
            {showRSI && <div className="absolute bottom-[25%] left-4 z-10 text-[9px] font-black text-slate-500 uppercase tracking-widest bg-slate-900/50 px-2 py-0.5 rounded">RSI (14)</div>}
            {showMACD && <div className="absolute bottom-[5%] left-4 z-10 text-[9px] font-black text-slate-500 uppercase tracking-widest bg-slate-900/50 px-2 py-0.5 rounded">MACD</div>}

            {localError && <div className="absolute inset-0 flex items-center justify-center text-rose-500 text-[10px] font-black uppercase tracking-widest bg-slate-950/80 z-50 text-center p-10">{localError}</div>}
        </div>
    );
};
