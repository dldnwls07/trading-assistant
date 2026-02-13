import React, { useEffect, useRef, useState } from 'react';
import { createChart, CandlestickSeries, LineSeries, HistogramSeries } from 'lightweight-charts';
import { Maximize2, Minimize2, Settings, X } from 'lucide-react';

export const StockChart = ({ data, interval, options = {}, analysis = null }) => {
    const chartContainerRef = useRef();
    const chartRef = useRef(null);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [showSettings, setShowSettings] = useState(false);

    // === 전문가급 지표 설정 (30개 이상) ===
    const [chartConfig, setChartConfig] = useState({
        // 상단 지표 (Overlay)
        showSMA5: true,
        showSMA10: false,
        showSMA20: true,
        showSMA50: false,
        showSMA60: false,
        showSMA100: false,
        showSMA120: false,
        showSMA200: false,
        showEMA9: false,
        showEMA12: false,
        showEMA20: false,
        showEMA26: false,
        showEMA50: false,
        showEMA200: false,
        showBB: true,
        showKC: false,
        showDC: false,
        showIchimoku: false,
        showVWAP: false,
        showPivot: false,
        showSAR: false,
        showAIQuotes: true,

        // 하단 지표 (Oscillators)
        showVolume: true,
        showRSI: false,
        showRSI9: false,
        showRSI25: false,
        showMACD: false,
        showStochastic: false,
        showCCI: false,
        showWilliamsR: false,
        showADX: false,
        showOBV: false,
        showMFI: false,
        showCMF: false,
        showROC: false,
        showMomentum: false,
        showAroon: false,
        showTSI: false,
        showUO: false,
        showATR: false,
    });

    const { upColor = '#ef4444', downColor = '#3b82f6', isDark = true } = options;

    const toggleFullscreen = () => {
        if (!document.fullscreenElement) {
            chartContainerRef.current?.requestFullscreen();
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
        if (!chartContainerRef.current || !data || data.length === 0) return;

        if (chartRef.current) {
            try { chartRef.current.remove(); } catch (e) { }
        }

        try {
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
                width: chartContainerRef.current.clientWidth,
                height: isFullscreen ? window.innerHeight : 500,
                layout: {
                    background: { color: isDark ? '#0f172a' : '#ffffff' },
                    textColor: isDark ? '#94a3b8' : '#334155',
                },
                grid: {
                    vertLines: { color: isDark ? '#1e293b' : '#e2e8f0' },
                    horzLines: { color: isDark ? '#1e293b' : '#e2e8f0' },
                },
                crosshair: { mode: 1 },
                timeScale: { borderColor: isDark ? '#334155' : '#cbd5e1' },
                rightPriceScale: { borderColor: isDark ? '#334155' : '#cbd5e1' },
            });

            chartRef.current = chart;

            const mainSeries = chart.addSeries(CandlestickSeries, {
                upColor, downColor, borderVisible: false, wickUpColor: upColor, wickDownColor: downColor,
            });
            mainSeries.setData(finalData);

            // === 상단 지표 (Overlay Indicators) ===
            const overlayColors = {
                sma_5: '#facc15', sma_10: '#fb923c', sma_20: '#ec4899', sma_50: '#a855f7',
                sma_60: '#3b82f6', sma_100: '#06b6d4', sma_120: '#8b5cf6', sma_200: '#10b981',
                ema_9: '#fbbf24', ema_12: '#f97316', ema_20: '#f43f5e', ema_26: '#c026d3',
                ema_50: '#8b5cf6', ema_200: '#059669'
            };

            Object.entries({
                showSMA5: 'sma_5', showSMA10: 'sma_10', showSMA20: 'sma_20', showSMA50: 'sma_50',
                showSMA60: 'sma_60', showSMA100: 'sma_100', showSMA120: 'sma_120', showSMA200: 'sma_200',
                showEMA9: 'ema_9', showEMA12: 'ema_12', showEMA20: 'ema_20', showEMA26: 'ema_26',
                showEMA50: 'ema_50', showEMA200: 'ema_200'
            }).forEach(([configKey, dataKey]) => {
                if (chartConfig[configKey]) {
                    const series = chart.addSeries(LineSeries, {
                        color: overlayColors[dataKey],
                        lineWidth: 1.5,
                        title: dataKey.toUpperCase().replace('_', ' ')
                    });
                    series.setData(finalData.filter(d => d[dataKey]).map(d => ({ time: d.time, value: d[dataKey] })));
                }
            });

            if (chartConfig.showBB) {
                const bbU = chart.addSeries(LineSeries, { color: 'rgba(148, 163, 184, 0.4)', lineWidth: 1, lineStyle: 2 });
                const bbL = chart.addSeries(LineSeries, { color: 'rgba(148, 163, 184, 0.4)', lineWidth: 1, lineStyle: 2 });
                bbU.setData(finalData.filter(d => d.bb_upper).map(d => ({ time: d.time, value: d.bb_upper })));
                bbL.setData(finalData.filter(d => d.bb_lower).map(d => ({ time: d.time, value: d.bb_lower })));
            }

            if (chartConfig.showKC) {
                const kcU = chart.addSeries(LineSeries, { color: 'rgba(251, 146, 60, 0.4)', lineWidth: 1, lineStyle: 2 });
                const kcL = chart.addSeries(LineSeries, { color: 'rgba(251, 146, 60, 0.4)', lineWidth: 1, lineStyle: 2 });
                kcU.setData(finalData.filter(d => d.kc_upper).map(d => ({ time: d.time, value: d.kc_upper })));
                kcL.setData(finalData.filter(d => d.kc_lower).map(d => ({ time: d.time, value: d.kc_lower })));
            }

            if (chartConfig.showDC) {
                const dcU = chart.addSeries(LineSeries, { color: 'rgba(34, 211, 238, 0.4)', lineWidth: 1, lineStyle: 2 });
                const dcL = chart.addSeries(LineSeries, { color: 'rgba(34, 211, 238, 0.4)', lineWidth: 1, lineStyle: 2 });
                dcU.setData(finalData.filter(d => d.dc_upper).map(d => ({ time: d.time, value: d.dc_upper })));
                dcL.setData(finalData.filter(d => d.dc_lower).map(d => ({ time: d.time, value: d.dc_lower })));
            }

            if (chartConfig.showIchimoku) {
                const tenkan = chart.addSeries(LineSeries, { color: '#f43f5e', lineWidth: 1 });
                const kijun = chart.addSeries(LineSeries, { color: '#3b82f6', lineWidth: 1 });
                tenkan.setData(finalData.filter(d => d.ichimoku_tenkan).map(d => ({ time: d.time, value: d.ichimoku_tenkan })));
                kijun.setData(finalData.filter(d => d.ichimoku_kijun).map(d => ({ time: d.time, value: d.ichimoku_kijun })));
            }

            if (chartConfig.showVWAP) {
                const vwap = chart.addSeries(LineSeries, { color: '#a855f7', lineWidth: 2 });
                vwap.setData(finalData.filter(d => d.vwap).map(d => ({ time: d.time, value: d.vwap })));
            }

            if (chartConfig.showAIQuotes && analysis) {
                const { buy, target, stop } = analysis.entry_points || {};
                if (buy) mainSeries.createPriceLine({ price: parseFloat(buy), color: '#fb7185', lineWidth: 2, title: 'AI ENTRY' });
                if (target) mainSeries.createPriceLine({ price: parseFloat(target), color: '#22d3ee', lineWidth: 2, lineStyle: 2, title: 'AI TARGET' });
                if (stop) mainSeries.createPriceLine({ price: parseFloat(stop), color: '#60a5fa', lineWidth: 2, lineStyle: 1, title: 'AI STOP' });
            }

            // === Pivot Points ===
            if (chartConfig.showPivot) {
                const pColor = isDark ? '#fbbf24' : '#eab308';
                const sColor = isDark ? '#ef4444' : '#dc2626';
                const rColor = isDark ? '#10b981' : '#059669';

                const pivot = chart.addSeries(LineSeries, { color: pColor, lineWidth: 1, lineStyle: 2, title: 'Pivot' });
                const r1 = chart.addSeries(LineSeries, { color: rColor, lineWidth: 1, lineStyle: 1, title: 'mR1' });
                const s1 = chart.addSeries(LineSeries, { color: sColor, lineWidth: 1, lineStyle: 1, title: 'mS1' });

                pivot.setData(finalData.filter(d => d.pivot_classic).map(d => ({ time: d.time, value: d.pivot_classic })));
                r1.setData(finalData.filter(d => d.pivot_r1).map(d => ({ time: d.time, value: d.pivot_r1 })));
                s1.setData(finalData.filter(d => d.pivot_s1).map(d => ({ time: d.time, value: d.pivot_s1 })));
            }

            // === Parabolic SAR ===
            if (chartConfig.showSAR) {
                // SAR은 점으로 표시해야 하므로 LineType을 활용하거나 marker 사용
                // Lightweight chart 3.8+ 에서는 markers 사용 권장, 여기서는 Scatter 스타일이 없으므로 Small Cross Series로 대체
                const sarSeries = chart.addSeries(LineSeries, {
                    color: isDark ? '#ffffff' : '#000000',
                    lineWidth: 0,
                    pointMarkerVisible: true,
                    pointMarkerRadius: 3,
                    pointMarkerBorderColor: isDark ? '#ffffff' : '#000000',
                    pointMarkerBackgroundColor: isDark ? '#ffffff' : '#000000',
                    title: 'SAR'
                });

                // lineVisible: false는 lightweigt-charts 버전 버전에 따라 옵션이 다름. 
                // 여기서는 lineWidth: 0으로 선을 숨기고 마커만 표시 시도

                sarSeries.setData(finalData.filter(d => d.parabolic_sar).map(d => ({ time: d.time, value: d.parabolic_sar })));

                // 만약 위 방법으로 선이 보인다면, markers API를 사용하는 것이 정석임.
                // 하지만 markers는 시계열 데이터(Series)가 아니라 '이벤트' 마커용임.
                // 따라서 LineSeries + lineWidth: 0 패턴을 사용.
            }

            // === 하단 지표 (Oscillators & Volume) ===
            let paneIndex = 0.7;

            if (chartConfig.showVolume) {
                const volumeSeries = chart.addSeries(HistogramSeries, { priceFormat: { type: 'volume' }, priceScaleId: '' });
                volumeSeries.priceScale().applyOptions({ scaleMargins: { top: 0.8, bottom: 0 } });
                volumeSeries.setData(finalData.map(d => ({
                    time: d.time, value: d.volume, color: d.close >= d.open ? upColor + '22' : downColor + '22'
                })));
            }

            if (chartConfig.showRSI || chartConfig.showRSI9 || chartConfig.showRSI25) {
                const rsiPane = `rsi-pane-${paneIndex}`;
                if (chartConfig.showRSI) {
                    const rsi = chart.addSeries(LineSeries, { color: '#a855f7', lineWidth: 1.5, priceScaleId: rsiPane });
                    rsi.setData(finalData.filter(d => d.rsi).map(d => ({ time: d.time, value: d.rsi })));
                }
                if (chartConfig.showRSI9) {
                    const rsi9 = chart.addSeries(LineSeries, { color: '#fbbf24', lineWidth: 1.5, priceScaleId: rsiPane });
                    rsi9.setData(finalData.filter(d => d.rsi_9).map(d => ({ time: d.time, value: d.rsi_9 })));
                }
                if (chartConfig.showRSI25) {
                    const rsi25 = chart.addSeries(LineSeries, { color: '#06b6d4', lineWidth: 1.5, priceScaleId: rsiPane });
                    rsi25.setData(finalData.filter(d => d.rsi_25).map(d => ({ time: d.time, value: d.rsi_25 })));
                }
                chart.priceScale(rsiPane).applyOptions({ scaleMargins: { top: paneIndex, bottom: 0.15 } });
                paneIndex += 0.15;
            }

            if (chartConfig.showMACD) {
                const macdPane = `macd-pane-${paneIndex}`;
                const macdHist = chart.addSeries(HistogramSeries, { priceScaleId: macdPane });
                macdHist.setData(finalData.filter(d => d.macd_hist !== undefined).map(d => ({
                    time: d.time, value: d.macd_hist, color: d.macd_hist >= 0 ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)'
                })));
                chart.priceScale(macdPane).applyOptions({ scaleMargins: { top: paneIndex, bottom: 0 } });
                paneIndex += 0.15;
            }

            if (chartConfig.showStochastic) {
                const stochPane = `stoch-pane-${paneIndex}`;
                const stochK = chart.addSeries(LineSeries, { color: '#3b82f6', lineWidth: 1.5, priceScaleId: stochPane });
                const stochD = chart.addSeries(LineSeries, { color: '#f43f5e', lineWidth: 1.5, priceScaleId: stochPane });
                stochK.setData(finalData.filter(d => d.stoch_k).map(d => ({ time: d.time, value: d.stoch_k })));
                stochD.setData(finalData.filter(d => d.stoch_d).map(d => ({ time: d.time, value: d.stoch_d })));
                chart.priceScale(stochPane).applyOptions({ scaleMargins: { top: paneIndex, bottom: 0.15 } });
                paneIndex += 0.15;
            }

            ['CCI', 'WilliamsR', 'ADX', 'OBV', 'MFI', 'CMF', 'ROC', 'Momentum', 'TSI', 'UO', 'ATR'].forEach((ind) => {
                const configKey = `show${ind}`;
                const dataKey = ind.toLowerCase().replace('williamsr', 'williams_r');
                if (chartConfig[configKey]) {
                    const pane = `${ind.toLowerCase()}-pane-${paneIndex}`;
                    const series = chart.addSeries(LineSeries, { color: '#10b981', lineWidth: 1.5, priceScaleId: pane });
                    series.setData(finalData.filter(d => d[dataKey]).map(d => ({ time: d.time, value: d[dataKey] })));
                    chart.priceScale(pane).applyOptions({ scaleMargins: { top: paneIndex, bottom: 0.15 } });
                    paneIndex += 0.15;
                }
            });

            if (chartConfig.showAroon) {
                const aroonPane = `aroon-pane-${paneIndex}`;
                const aroonUp = chart.addSeries(LineSeries, { color: '#10b981', lineWidth: 1.5, priceScaleId: aroonPane });
                const aroonDown = chart.addSeries(LineSeries, { color: '#ef4444', lineWidth: 1.5, priceScaleId: aroonPane });
                aroonUp.setData(finalData.filter(d => d.aroon_up).map(d => ({ time: d.time, value: d.aroon_up })));
                aroonDown.setData(finalData.filter(d => d.aroon_down).map(d => ({ time: d.time, value: d.aroon_down })));
                chart.priceScale(aroonPane).applyOptions({ scaleMargins: { top: paneIndex, bottom: 0.15 } });
            }

            chart.timeScale().fitContent();

            const handleResize = () => {
                chart.applyOptions({ width: chartContainerRef.current.clientWidth, height: isFullscreen ? window.innerHeight : 500 });
            };
            window.addEventListener('resize', handleResize);
            return () => window.removeEventListener('resize', handleResize);

        } catch (error) {
            console.error('Chart rendering error:', error);
        }
    }, [data, interval, chartConfig, analysis, isFullscreen, isDark, upColor, downColor]);

    return (
        <div className="relative w-full">
            <div className="absolute top-2 right-2 z-10 flex gap-2">
                <button onClick={() => setShowSettings(!showSettings)} className="p-2 bg-slate-800/90 hover:bg-slate-700 rounded-lg transition">
                    {showSettings ? <X size={18} className="text-slate-300" /> : <Settings size={18} className="text-slate-300" />}
                </button>
                <button onClick={toggleFullscreen} className="p-2 bg-slate-800/90 hover:bg-slate-700 rounded-lg transition">
                    {isFullscreen ? <Minimize2 size={18} className="text-slate-300" /> : <Maximize2 size={18} className="text-slate-300" />}
                </button>
            </div>

            {showSettings && (
                <div className="absolute top-14 right-2 z-20 bg-slate-800 border border-slate-700 rounded-xl p-4 shadow-2xl w-80 max-h-96 overflow-y-auto">
                    <h4 className="text-white font-bold mb-3 text-sm">차트 지표 설정</h4>

                    <div className="space-y-3">
                        <div>
                            <h5 className="text-slate-400 text-xs mb-2 font-semibold">📈 상단 지표 (Overlay)</h5>
                            <div className="space-y-1">
                                <Toggle label="SMA 5" value={chartConfig.showSMA5} onToggle={() => setChartConfig(c => ({ ...c, showSMA5: !c.showSMA5 }))} />
                                <Toggle label="SMA 10" value={chartConfig.showSMA10} onToggle={() => setChartConfig(c => ({ ...c, showSMA10: !c.showSMA10 }))} />
                                <Toggle label="SMA 20" value={chartConfig.showSMA20} onToggle={() => setChartConfig(c => ({ ...c, showSMA20: !c.showSMA20 }))} />
                                <Toggle label="SMA 50" value={chartConfig.showSMA50} onToggle={() => setChartConfig(c => ({ ...c, showSMA50: !c.showSMA50 }))} />
                                <Toggle label="SMA 60" value={chartConfig.showSMA60} onToggle={() => setChartConfig(c => ({ ...c, showSMA60: !c.showSMA60 }))} />
                                <Toggle label="SMA 100" value={chartConfig.showSMA100} onToggle={() => setChartConfig(c => ({ ...c, showSMA100: !c.showSMA100 }))} />
                                <Toggle label="SMA 120" value={chartConfig.showSMA120} onToggle={() => setChartConfig(c => ({ ...c, showSMA120: !c.showSMA120 }))} />
                                <Toggle label="SMA 200" value={chartConfig.showSMA200} onToggle={() => setChartConfig(c => ({ ...c, showSMA200: !c.showSMA200 }))} />
                                <Toggle label="EMA 9" value={chartConfig.showEMA9} onToggle={() => setChartConfig(c => ({ ...c, showEMA9: !c.showEMA9 }))} />
                                <Toggle label="EMA 12" value={chartConfig.showEMA12} onToggle={() => setChartConfig(c => ({ ...c, showEMA12: !c.showEMA12 }))} />
                                <Toggle label="EMA 20" value={chartConfig.showEMA20} onToggle={() => setChartConfig(c => ({ ...c, showEMA20: !c.showEMA20 }))} />
                                <Toggle label="EMA 26" value={chartConfig.showEMA26} onToggle={() => setChartConfig(c => ({ ...c, showEMA26: !c.showEMA26 }))} />
                                <Toggle label="EMA 50" value={chartConfig.showEMA50} onToggle={() => setChartConfig(c => ({ ...c, showEMA50: !c.showEMA50 }))} />
                                <Toggle label="EMA 200" value={chartConfig.showEMA200} onToggle={() => setChartConfig(c => ({ ...c, showEMA200: !c.showEMA200 }))} />
                                <Toggle label="볼린저 밴드" value={chartConfig.showBB} onToggle={() => setChartConfig(c => ({ ...c, showBB: !c.showBB }))} />
                                <Toggle label="켈트너 채널" value={chartConfig.showKC} onToggle={() => setChartConfig(c => ({ ...c, showKC: !c.showKC }))} />
                                <Toggle label="동코안 채널" value={chartConfig.showDC} onToggle={() => setChartConfig(c => ({ ...c, showDC: !c.showDC }))} />
                                <Toggle label="일목균형표" value={chartConfig.showIchimoku} onToggle={() => setChartConfig(c => ({ ...c, showIchimoku: !c.showIchimoku }))} />
                                <Toggle label="VWAP" value={chartConfig.showVWAP} onToggle={() => setChartConfig(c => ({ ...c, showVWAP: !c.showVWAP }))} />
                                <Toggle label="피벗 포인트" value={chartConfig.showPivot} onToggle={() => setChartConfig(c => ({ ...c, showPivot: !c.showPivot }))} />
                                <Toggle label="파라볼릭 SAR" value={chartConfig.showSAR} onToggle={() => setChartConfig(c => ({ ...c, showSAR: !c.showSAR }))} />
                                <Toggle label="AI 패턴/타점" value={chartConfig.showAIQuotes} onToggle={() => setChartConfig(c => ({ ...c, showAIQuotes: !c.showAIQuotes }))} />
                            </div>
                        </div>

                        <div className="pt-3 border-t border-slate-700">
                            <h5 className="text-slate-400 text-xs mb-2 font-semibold">📊 하단 지표 (Oscillators)</h5>
                            <div className="space-y-1">
                                <Toggle label="거래량" value={chartConfig.showVolume} onToggle={() => setChartConfig(c => ({ ...c, showVolume: !c.showVolume }))} />
                                <Toggle label="RSI (14)" value={chartConfig.showRSI} onToggle={() => setChartConfig(c => ({ ...c, showRSI: !c.showRSI }))} />
                                <Toggle label="RSI (9)" value={chartConfig.showRSI9} onToggle={() => setChartConfig(c => ({ ...c, showRSI9: !c.showRSI9 }))} />
                                <Toggle label="RSI (25)" value={chartConfig.showRSI25} onToggle={() => setChartConfig(c => ({ ...c, showRSI25: !c.showRSI25 }))} />
                                <Toggle label="MACD" value={chartConfig.showMACD} onToggle={() => setChartConfig(c => ({ ...c, showMACD: !c.showMACD }))} />
                                <Toggle label="Stochastic" value={chartConfig.showStochastic} onToggle={() => setChartConfig(c => ({ ...c, showStochastic: !c.showStochastic }))} />
                                <Toggle label="CCI" value={chartConfig.showCCI} onToggle={() => setChartConfig(c => ({ ...c, showCCI: !c.showCCI }))} />
                                <Toggle label="Williams %R" value={chartConfig.showWilliamsR} onToggle={() => setChartConfig(c => ({ ...c, showWilliamsR: !c.showWilliamsR }))} />
                                <Toggle label="ADX" value={chartConfig.showADX} onToggle={() => setChartConfig(c => ({ ...c, showADX: !c.showADX }))} />
                                <Toggle label="OBV" value={chartConfig.showOBV} onToggle={() => setChartConfig(c => ({ ...c, showOBV: !c.showOBV }))} />
                                <Toggle label="MFI" value={chartConfig.showMFI} onToggle={() => setChartConfig(c => ({ ...c, showMFI: !c.showMFI }))} />
                                <Toggle label="CMF" value={chartConfig.showCMF} onToggle={() => setChartConfig(c => ({ ...c, showCMF: !c.showCMF }))} />
                                <Toggle label="ROC" value={chartConfig.showROC} onToggle={() => setChartConfig(c => ({ ...c, showROC: !c.showROC }))} />
                                <Toggle label="Momentum" value={chartConfig.showMomentum} onToggle={() => setChartConfig(c => ({ ...c, showMomentum: !c.showMomentum }))} />
                                <Toggle label="Aroon" value={chartConfig.showAroon} onToggle={() => setChartConfig(c => ({ ...c, showAroon: !c.showAroon }))} />
                                <Toggle label="TSI" value={chartConfig.showTSI} onToggle={() => setChartConfig(c => ({ ...c, showTSI: !c.showTSI }))} />
                                <Toggle label="Ultimate Osc" value={chartConfig.showUO} onToggle={() => setChartConfig(c => ({ ...c, showUO: !c.showUO }))} />
                                <Toggle label="ATR" value={chartConfig.showATR} onToggle={() => setChartConfig(c => ({ ...c, showATR: !c.showATR }))} />
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <div ref={chartContainerRef} className="w-full" style={{ height: isFullscreen ? '100vh' : '500px' }} />
        </div>
    );
};

// Toggle 컴포넌트를 외부로 분리 (성능 최적화 및 린트 에러 해결)
const Toggle = ({ label, value, onToggle }) => (
    <div onClick={onToggle} className="flex items-center justify-between p-2 hover:bg-slate-700/50 rounded cursor-pointer">
        <span className="text-xs text-slate-300">{label}</span>
        <div className={`w-9 h-5 rounded-full transition ${value ? 'bg-blue-500' : 'bg-slate-600'} relative`}>
            <div className={`w-4 h-4 bg-white rounded-full absolute top-0.5 transition-all ${value ? 'left-4' : 'left-0.5'}`} />
        </div>
    </div>
);
