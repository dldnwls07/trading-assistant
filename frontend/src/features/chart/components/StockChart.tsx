import React, { useEffect, useRef, useState } from 'react';
import { createChart, CandlestickSeries, IChartApi, ISeriesApi, ColorType, CrosshairMode } from 'lightweight-charts';
import { Maximize2, Minimize2, Settings, X, Activity } from 'lucide-react';
import DrawingToolbar from './chart/DrawingToolbar';
import { useChartResize } from '../hooks/useChartResize';
import { useChartDrawing } from '../hooks/useChartDrawing';
import { useChartIndicators } from '../hooks/useChartIndicators.ts';

interface ToggleProps {
    label: string;
    value: boolean;
    onToggle: () => void;
}

const Toggle: React.FC<ToggleProps> = ({ label, value, onToggle }) => (
    <div onClick={onToggle} className="flex items-center justify-between p-3.5 hover:bg-white/[0.03] rounded-xl cursor-pointer transition-[background-color] duration-200 group border border-transparent hover:border-white/5">
        <span className="text-[11px] text-muted-foreground group-hover:text-foreground font-black uppercase tracking-widest transition-colors font-mono">{label}</span>
        <div className={`w-10 h-5.5 rounded-full transition-[background-color] duration-300 ${value ? 'bg-yellow-400 shadow-[0_0_10px_#FACC1550]' : 'bg-white/10'} relative border border-white/5`}>
            <div className={`w-3.5 h-3.5 bg-white rounded-full absolute top-0.5 transition-[left,box-shadow] duration-300 shadow-xl ${value ? 'left-5.5' : 'left-0.5'}`} />
        </div>
    </div>
);

import { OhlcvData, AnalysisResult } from '../../../types/api';

export interface ChartOptions {
    upColor?: string;
    downColor?: string;
    isDark?: boolean;
}

export interface StockChartProps {
    data: OhlcvData[];
    interval: string;
    options?: ChartOptions;
    chartType?: string; // Added prop
    analysis?: AnalysisResult | null;
}

export const StockChart: React.FC<StockChartProps> = ({ data, interval, options = {}, analysis = null }) => {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);
    const [chartInstance, setChartInstance] = useState<IChartApi | null>(null);
    const mainSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

    const [isFullscreen, setIsFullscreen] = useState(false);
    const [showSettings, setShowSettings] = useState(false);
    const [activeTool, setActiveTool] = useState('cursor');

    // Chart Configuration State
    const [chartConfig, setChartConfig] = useState({
        showSMA5: true, showSMA20: true, showSMA50: false, showSMA200: false,
        showEMA9: false, showEMA20: false, showEMA50: false,
        showSupertrend: true, showTrendCloud: true,
        showBB: true, showKC: false, showDC: false,
        showRSI: false, showMACD: false, showStochastic: false,
        showVolume: true, showVolumeProfile: true,
        showMacroEvents: true, showAIPatterns: true, showAIQuotes: true, showPivot: false,
        showSupportResistance: true, showAutoTrendlines: true
    });

    const { upColor = '#ef4444', downColor = '#3b82f6', isDark = true } = options;

    // 1. Initialize Chart
    useEffect(() => {
        if (!chartContainerRef.current) return;

        // Cleanup existing chart
        if (chartRef.current) {
            chartRef.current.remove();
            chartRef.current = null;
        }

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: isDark ? '#09090b' : '#ffffff' },
                textColor: isDark ? '#94a3b8' : '#334155',
                fontFamily: 'JetBrains Mono, monospace',
            },
            grid: {
                vertLines: { color: isDark ? '#111111' : '#f0f0f0' },
                horzLines: { color: isDark ? '#111111' : '#f0f0f0' },
            },
            crosshair: {
                mode: CrosshairMode.Normal,
                vertLine: { labelBackgroundColor: '#FACC15', color: '#FACC15', style: 2, labelVisible: true },
                horzLine: { labelBackgroundColor: '#FACC15', color: '#FACC15', style: 2, labelVisible: true },
            },
            timeScale: { borderColor: isDark ? '#111111' : '#e2e8f0', barSpacing: 10 },
            rightPriceScale: { borderColor: isDark ? '#111111' : '#e2e8f0' },
            autoSize: true,
        });

        chartRef.current = chart;
        setChartInstance(chart);

        // Main Candlestick Series
        const mainSeries = chart.addSeries(CandlestickSeries, {
            upColor, downColor, borderVisible: false, wickUpColor: upColor, wickDownColor: downColor,
        });
        mainSeriesRef.current = mainSeries;

        // Initial Data Set
        if (data && data.length > 0) {
            const processedData = data.map((d: any) => {
                let time = d.time || d.Date;
                if (typeof time === 'string' && time.includes(':')) {
                    time = new Date(time).getTime() / 1000;
                }
                return { ...d, time };
            });
            mainSeries.setData(processedData);
        }

        return () => {
            setChartInstance(null);
            if (chartRef.current) {
                chartRef.current.remove();
                chartRef.current = null;
            }
        };
    }, [isDark, upColor, downColor]);

    // Data Update Effect separate from Init
    useEffect(() => {
        if (!mainSeriesRef.current || !data) return;

        if (data.length > 0) {
            let processedData = data.map((d: any) => {
                let time = d.time || d.Date;
                if (typeof time === 'string' && time.includes(':')) {
                    time = new Date(time).getTime() / 1000;
                }
                return { ...d, time };
            });

            // Frontend Resampling for 1Y if backend sends raw data
            // (백엔드 리로드가 안 되었을 경우를 대비한 2중 안전장치)
            if (interval === '1y' && processedData.length > 100) { // 100개 이상이면 월봉일 가능성 높음
                const yearlyData: any[] = [];
                let currentYear: string | null = null;
                let agg: any = null;

                processedData.forEach((candle: any) => {
                    // candle.time은 'YYYY-MM-DD' 문자열이거나 timestamp
                    let dateStr = '';
                    if (typeof candle.time === 'string') {
                        dateStr = candle.time;
                    } else if (typeof candle.time === 'number') {
                        dateStr = new Date(candle.time * 1000).toISOString().split('T')[0];
                    } else {
                        // lightweight-charts Time object handling if needed
                        // Assuming standardized string or timestamp for now
                        return;
                    }

                    const year = dateStr.substring(0, 4);

                    if (year !== currentYear) {
                        if (agg) {
                            yearlyData.push(agg);
                        }
                        currentYear = year;
                        agg = {
                            time: candle.time, // Use start time of year
                            open: candle.open,
                            high: candle.high,
                            low: candle.low,
                            close: candle.close,
                            volume: candle.volume
                        };
                    } else {
                        // Aggregate
                        agg.high = Math.max(agg.high, candle.high);
                        agg.low = Math.min(agg.low, candle.low);
                        agg.close = candle.close;
                        agg.volume += candle.volume;
                        // Update time to latest? No, usually yearly bar starts at 'YYYY-01-01' or similar. 
                        // But lightweight charts needs sorted time. Keeping the first date is fine.
                    }
                });
                if (agg) yearlyData.push(agg);
                processedData = yearlyData;
            }

            mainSeriesRef.current.setData(processedData);
        }
    }, [data, interval]);


    // 2. Attach Hooks
    useChartResize(chartInstance, chartContainerRef, isFullscreen);
    const { drawings, magnetEnabled, setMagnetEnabled, setDrawings } = useChartDrawing(chartInstance, mainSeriesRef, activeTool, setActiveTool);
    useChartIndicators(chartInstance, mainSeriesRef, data, chartConfig, analysis, options);

    // Fullscreen Toggle
    const toggleFullscreen = () => {
        setIsFullscreen(!isFullscreen);
    };

    const chartContent = (
        <div className={`w-full bg-background flex flex-col transition-all duration-300 ${isFullscreen ? 'fixed inset-0 z-[9999] h-screen' : 'relative h-full flex-1'}`}>
            {/* 1. Chart Container (Base Layer) */}
            <div ref={chartContainerRef} className="w-full flex-1 relative overflow-hidden" />

            {/* 2. Top Toolbar (Controls) */}
            <div className="absolute top-4 right-4 z-[50] flex items-center gap-3">
                <button onClick={() => setShowSettings(!showSettings)} className={`p-3 bg-white/5 backdrop-blur-md hover:bg-white/10 rounded-xl border border-white/5 transition-[background-color,transform,box-shadow] duration-200 shadow-2xl group active:scale-90 ${showSettings ? 'border-yellow-400/40 bg-yellow-400/10' : ''}`}>
                    <Settings size={20} className={`transition-colors duration-200 ${showSettings ? 'text-yellow-400' : 'text-zinc-500 group-hover:text-zinc-100'}`} />
                </button>
                <button onClick={toggleFullscreen} className={`px-5 py-3 bg-yellow-400 hover:bg-yellow-400/90 rounded-xl transition-[background-color,transform,box-shadow] duration-200 active:scale-95 shadow-[0_10px_20px_-5px_#FACC1540] flex items-center gap-3 text-black font-black text-[10px] tracking-widest uppercase`}>
                    {isFullscreen ? <><Minimize2 size={16} /> EXIT_FS</> : <><Maximize2 size={16} /> FULLSCAN</>}
                </button>
            </div>

            {/* 3. Left Drawing Toolbar */}
            <DrawingToolbar
                activeTool={activeTool}
                onSelectTool={setActiveTool}
                magnetEnabled={magnetEnabled}
                onToggleMagnet={() => setMagnetEnabled(!magnetEnabled)}
                onClearAll={() => {
                    if (window.confirm('Clear all drawings?')) {
                        setDrawings([]);
                        localStorage.removeItem('chart_drawings');
                    }
                }}
            />

            {/* 4. Settings Panel (Overlay) */}
            {showSettings && (
                <div className="absolute top-20 right-4 z-[60] bg-[#09090b]/90 backdrop-blur-3xl border border-white/10 rounded-[2rem] p-8 shadow-[0_40px_80px_-20px_rgba(0,0,0,0.8)] w-96 max-h-[calc(100%-100px)] overflow-y-auto custom-scrollbar animate-in slide-in-from-top-4 fade-in duration-300">
                    <h4 className="text-zinc-100 font-black mb-8 text-base flex items-center gap-4 uppercase tracking-tighter font-mono">
                        <div className="w-1.5 h-6 bg-yellow-400 rounded-full shadow-[0_0_10px_#FACC15]"></div>
                        INTELLIG_LAYER_CTRL
                    </h4>

                    <div className="space-y-10">
                        {/* 1. Trend */}
                        <div>
                            <h5 className="text-yellow-400/60 text-[10px] mb-4 font-black uppercase tracking-[0.3em] flex items-center gap-3 font-mono">
                                TREND_ENGINE_X
                            </h5>
                            <div className="space-y-2 pl-4 border-l-[1px] border-white/5">
                                <Toggle label="Supertrend AI" value={chartConfig.showSupertrend} onToggle={() => setChartConfig(c => ({ ...c, showSupertrend: !c.showSupertrend }))} />
                                <Toggle label="Smart Trend Cloud" value={chartConfig.showTrendCloud} onToggle={() => setChartConfig(c => ({ ...c, showTrendCloud: !c.showTrendCloud }))} />
                                <Toggle label="SMA Array (5/20/50)" value={chartConfig.showSMA20} onToggle={() => setChartConfig(c => ({ ...c, showSMA20: !c.showSMA20, showSMA5: !c.showSMA5, showSMA50: !c.showSMA50 }))} />
                            </div>
                        </div>

                        {/* 2. Volatility & Impulse */}
                        <div>
                            <h5 className="text-emerald-500/60 text-[10px] mb-4 font-black uppercase tracking-[0.3em] flex items-center gap-3 font-mono">
                                VOLATILITY_SCANNER
                            </h5>
                            <div className="space-y-2 pl-4 border-l-[1px] border-white/5">
                                <Toggle label="Bollinger Bands" value={chartConfig.showBB} onToggle={() => setChartConfig(c => ({ ...c, showBB: !c.showBB }))} />
                                <Toggle label="RSI Scanner" value={chartConfig.showRSI} onToggle={() => setChartConfig(c => ({ ...c, showRSI: !c.showRSI }))} />
                                <Toggle label="Volume Flow" value={chartConfig.showVolume} onToggle={() => setChartConfig(c => ({ ...c, showVolume: !c.showVolume }))} />
                            </div>
                        </div>

                        {/* 3. AI & Macro */}
                        <div>
                            <h5 className="text-yellow-400/60 text-[10px] mb-4 font-black uppercase tracking-[0.3em] flex items-center gap-3 font-mono">
                                AI_VISION_HARMONICS
                            </h5>
                            <div className="space-y-2 pl-4 border-l-[1px] border-white/5">
                                <Toggle label="Volume Profile (VPVR)" value={chartConfig.showVolumeProfile} onToggle={() => setChartConfig(c => ({ ...c, showVolumeProfile: !c.showVolumeProfile }))} />
                                <Toggle label="Macro Event Timeline" value={chartConfig.showMacroEvents} onToggle={() => setChartConfig(c => ({ ...c, showMacroEvents: !c.showMacroEvents }))} />
                                <Toggle label="AI Support & Resistance" value={chartConfig.showSupportResistance} onToggle={() => setChartConfig(c => ({ ...c, showSupportResistance: !c.showSupportResistance }))} />
                                <Toggle label="AI Auto-Trendlines" value={chartConfig.showAutoTrendlines} onToggle={() => setChartConfig(c => ({ ...c, showAutoTrendlines: !c.showAutoTrendlines }))} />
                                <Toggle label="AI Pattern Auto-Detect" value={chartConfig.showAIPatterns} onToggle={() => setChartConfig(c => ({ ...c, showAIPatterns: !c.showAIPatterns }))} />
                                <Toggle label="Strategic Entry/Exit" value={chartConfig.showAIQuotes} onToggle={() => setChartConfig(c => ({ ...c, showAIQuotes: !c.showAIQuotes }))} />
                            </div>
                        </div>
                    </div>
                </div>
            )}


            {/* Loading / Empty State Overlay */}
            {(!data || data.length === 0) && (
                <div className="absolute inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm z-10">
                    <div className="flex flex-col items-center gap-4 opacity-70">
                        <Activity className="w-10 h-10 text-primary animate-pulse" />
                        <span className="text-xs font-black uppercase tracking-[0.3em] text-muted-foreground">Initializing Quantum Bridge...</span>
                    </div>
                </div>
            )}
        </div>
    );

    return chartContent;
};
