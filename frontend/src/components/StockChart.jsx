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
        // 1. 추세 지표 (Trend)
        showSMA5: true,
        showSMA20: true,
        showSMA50: false,
        showSMA200: false,
        showEMA9: false,
        showEMA20: false,
        showEMA50: false,
        showSupertrend: true,
        showTrendCloud: true, // NEW: 시각적 추세 구름
        showIchimoku: false,
        showSAR: false,
        showVWAP: false,

        // 2. 변동성 지표 (Volatility)
        showBB: true,
        showKC: false,
        showDC: false,

        // 3. 모멘텀 지표 (Momentum)
        showRSI: false,
        showMACD: false,
        showStochastic: false,
        showCCI: false,
        showWilliamsR: false,

        // 4. 거래량 및 기타 (Volume & Others)
        showVolume: true,
        showOBV: false,
        showMFI: false,
        showCMF: false,
        showVWAP_Vol: false, // VWAP is technically trend but often grouped with volume

        // AI 전용
        showAIQuotes: true,
        showPivot: false,
        showADX: false,
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
                sma_5: '#facc15', sma_20: '#ec4899', sma_50: '#a855f7', sma_200: '#10b981',
                ema_9: '#fbbf24', ema_20: '#f43f5e', ema_50: '#8b5cf6', supertrend: '#10b981'
            };

            // SMA/EMA 처리
            Object.entries({
                showSMA5: 'sma_5', showSMA20: 'sma_20', showSMA50: 'sma_50', showSMA200: 'sma_200',
                showEMA9: 'ema_9', showEMA20: 'ema_20', showEMA50: 'ema_50'
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

            // Supertrend (NEW)
            if (chartConfig.showSupertrend) {
                const stSeries = chart.addSeries(LineSeries, {
                    lineWidth: 2,
                    title: 'Supertrend'
                });

                // direction에 따라 색상 분리 처리 (그라데이션이나 영역 채우기는 lightweight-charts 사양상 직접 지원이 까다로워 선 색상 변경 위주)
                stSeries.setData(finalData.filter(d => d.supertrend).map(d => ({
                    time: d.time,
                    value: d.supertrend,
                    color: d.supertrend_direction === 1 ? '#10b981' : '#f43f5e'
                })));
            }

            // Trend Cloud (NEW: EMA20 & SMA50 사이의 구름 효과)
            if (chartConfig.showTrendCloud) {
                const cloudSeries = chart.addSeries(LineSeries, {
                    color: 'rgba(59, 130, 246, 0.1)',
                    lineWidth: 0,
                    title: 'Trend Cloud'
                });

                // 추세 구름은 EMA20과 SMA50 사이를 채우는 효과 (여기서는 단순 상단선으로 표시하거나 여러 선으로 면적 효과)
                // 정석은 AreaSeries이나 두 지표 사이를 가변적으로 채우기는 어려우므로 EMA20을 기준으로 색상 변화
                const ema20 = chart.addSeries(LineSeries, { color: 'rgba(16, 185, 129, 0.2)', lineWidth: 1 });
                const sma50 = chart.addSeries(LineSeries, { color: 'rgba(244, 63, 94, 0.2)', lineWidth: 1 });

                ema20.setData(finalData.filter(d => d.ema_20).map(d => ({ time: d.time, value: d.ema_20 })));
                sma50.setData(finalData.filter(d => d.sma_50).map(d => ({ time: d.time, value: d.sma_50 })));
            }

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
                const sarSeries = chart.addSeries(LineSeries, {
                    color: isDark ? '#ffffff' : '#000000',
                    lineWidth: 0,
                    pointMarkerVisible: true,
                    pointMarkerRadius: 3,
                    pointMarkerBorderColor: isDark ? '#ffffff' : '#000000',
                    pointMarkerBackgroundColor: isDark ? '#ffffff' : '#000000',
                    title: 'SAR'
                });
                sarSeries.setData(finalData.filter(d => d.parabolic_sar).map(d => ({ time: d.time, value: d.parabolic_sar })));
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

            if (chartConfig.showRSI) {
                const rsiPane = `rsi-pane-${paneIndex}`;
                const rsi = chart.addSeries(LineSeries, { color: '#a855f7', lineWidth: 1.5, priceScaleId: rsiPane });
                rsi.setData(finalData.filter(d => d.rsi).map(d => ({ time: d.time, value: d.rsi })));
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

            ['CCI', 'WilliamsR', 'ADX', 'OBV', 'MFI', 'CMF', 'ATR'].forEach((ind) => {
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
                <div className="absolute top-14 right-2 z-20 bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-2xl w-80 max-h-[450px] overflow-y-auto custom-scrollbar">
                    <h4 className="text-white font-black mb-4 text-sm flex items-center gap-2">
                        <Settings size={14} />
                        차트 및 보조지표 개인화
                    </h4>

                    <div className="space-y-5">
                        {/* 1. 추세 지표 */}
                        <div>
                            <h5 className="text-blue-400 text-[10px] mb-2 font-black uppercase tracking-widest flex items-center gap-1.5">
                                <div className="w-1.5 h-1.5 rounded-full bg-blue-500"></div>
                                Trend (추세)
                            </h5>
                            <div className="space-y-0.5">
                                <Toggle label="Supertrend (추천)" value={chartConfig.showSupertrend} onToggle={() => setChartConfig(c => ({ ...c, showSupertrend: !c.showSupertrend }))} />
                                <Toggle label="Trend Cloud (시각화)" value={chartConfig.showTrendCloud} onToggle={() => setChartConfig(c => ({ ...c, showTrendCloud: !c.showTrendCloud }))} />
                                <Toggle label="SMA 5 / 20 / 50 / 200" value={chartConfig.showSMA20} onToggle={() => setChartConfig(c => ({ ...c, showSMA20: !c.showSMA20, showSMA5: !c.showSMA5 }))} />
                                <Toggle label="일목균형표" value={chartConfig.showIchimoku} onToggle={() => setChartConfig(c => ({ ...c, showIchimoku: !c.showIchimoku }))} />
                                <Toggle label="Parabolic SAR" value={chartConfig.showSAR} onToggle={() => setChartConfig(c => ({ ...c, showSAR: !c.showSAR }))} />
                                <Toggle label="VWAP" value={chartConfig.showVWAP} onToggle={() => setChartConfig(c => ({ ...c, showVWAP: !c.showVWAP }))} />
                            </div>
                        </div>

                        {/* 2. 변동성 지표 */}
                        <div>
                            <h5 className="text-emerald-400 text-[10px] mb-2 font-black uppercase tracking-widest flex items-center gap-1.5">
                                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
                                Volatility (변동성)
                            </h5>
                            <div className="space-y-0.5">
                                <Toggle label="볼린저 밴드" value={chartConfig.showBB} onToggle={() => setChartConfig(c => ({ ...c, showBB: !c.showBB }))} />
                                <Toggle label="켈트너 채널" value={chartConfig.showKC} onToggle={() => setChartConfig(c => ({ ...c, showKC: !c.showKC }))} />
                                <Toggle label="동코안 채널" value={chartConfig.showDC} onToggle={() => setChartConfig(c => ({ ...c, showDC: !c.showDC }))} />
                            </div>
                        </div>

                        {/* 3. 모멘텀 지표 */}
                        <div>
                            <h5 className="text-orange-400 text-[10px] mb-2 font-black uppercase tracking-widest flex items-center gap-1.5">
                                <div className="w-1.5 h-1.5 rounded-full bg-orange-500"></div>
                                Momentum (에너지)
                            </h5>
                            <div className="space-y-0.5">
                                <Toggle label="RSI" value={chartConfig.showRSI} onToggle={() => setChartConfig(c => ({ ...c, showRSI: !c.showRSI }))} />
                                <Toggle label="MACD" value={chartConfig.showMACD} onToggle={() => setChartConfig(c => ({ ...c, showMACD: !c.showMACD }))} />
                                <Toggle label="Stochastic" value={chartConfig.showStochastic} onToggle={() => setChartConfig(c => ({ ...c, showStochastic: !c.showStochastic }))} />
                            </div>
                        </div>

                        {/* 4. 거래량 지표 */}
                        <div>
                            <h5 className="text-slate-400 text-[10px] mb-2 font-black uppercase tracking-widest flex items-center gap-1.5">
                                <div className="w-1.5 h-1.5 rounded-full bg-slate-500"></div>
                                Volume (거래량)
                            </h5>
                            <div className="space-y-0.5">
                                <Toggle label="거래 히스토리" value={chartConfig.showVolume} onToggle={() => setChartConfig(c => ({ ...c, showVolume: !c.showVolume }))} />
                                <Toggle label="OBV / MFI / CMF" value={chartConfig.showOBV} onToggle={() => setChartConfig(c => ({ ...c, showOBV: !c.showOBV, showMFI: !c.showMFI, showCMF: !c.showCMF }))} />
                            </div>
                        </div>

                        {/* 5. 시스템 설정 */}
                        <div className="pt-3 border-t border-slate-700">
                            <Toggle label="AI 타점 자동 표시" value={chartConfig.showAIQuotes} onToggle={() => setChartConfig(c => ({ ...c, showAIQuotes: !c.showAIQuotes }))} />
                            <Toggle label="당일 피벗 라인" value={chartConfig.showPivot} onToggle={() => setChartConfig(c => ({ ...c, showPivot: !c.showPivot }))} />
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
