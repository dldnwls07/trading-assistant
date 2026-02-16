import React, { useEffect, useRef, useState } from 'react';
import ReactDOM from 'react-dom';
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
    <div onClick={onToggle} className="flex items-center justify-between p-2.5 hover:bg-slate-700/50 rounded-lg cursor-pointer transition-colors group">
        <span className="text-xs text-slate-400 group-hover:text-slate-200 font-medium transition-colors">{label}</span>
        <div className={`w-9 h-5 rounded-full transition-colors ${value ? 'bg-blue-600' : 'bg-slate-700'} relative`}>
            <div className={`w-3.5 h-3.5 bg-white rounded-full absolute top-0.5 transition-all shadow-sm ${value ? 'left-4.5' : 'left-0.5'}`} />
        </div>
    </div>
);

export interface ChartOptions {
    upColor?: string;
    downColor?: string;
    isDark?: boolean;
}

export interface StockChartProps {
    data: any[]; // TODO: Define strict data interface
    interval: string;
    options?: ChartOptions;
    chartType?: string; // Added prop
    analysis?: any;
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
                background: { type: ColorType.Solid, color: isDark ? '#0f172a' : '#ffffff' },
                textColor: isDark ? '#94a3b8' : '#334155',
            },
            grid: {
                vertLines: { color: isDark ? '#1e293b' : '#e2e8f0' },
                horzLines: { color: isDark ? '#1e293b' : '#e2e8f0' },
            },
            crosshair: {
                mode: CrosshairMode.Normal,
                vertLine: { labelBackgroundColor: '#3b82f6' },
                horzLine: { labelBackgroundColor: '#3b82f6' },
            },
            timeScale: { borderColor: isDark ? '#334155' : '#cbd5e1' },
            rightPriceScale: { borderColor: isDark ? '#334155' : '#cbd5e1' },
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
        <div className={`w-full bg-[#0f172a] ${isFullscreen ? 'fixed inset-0 z-[9999] h-screen flex flex-col' : 'relative h-[600px] flex flex-col'}`}>
            {/* 1. Chart Container (Base Layer) */}
            <div ref={chartContainerRef} className="w-full flex-1 transition-all duration-300 relative" />

            {/* 2. Top Toolbar (Controls) */}
            <div className="absolute top-3 right-3 z-[50] flex items-center gap-2">
                <button onClick={() => setShowSettings(!showSettings)} className="p-2 bg-slate-800/80 hover:bg-slate-700 backdrop-blur-md rounded-lg border border-slate-700 transition-all shadow-lg group">
                    {showSettings ? <X size={18} className="text-slate-400 group-hover:text-white" /> : <Settings size={18} className="text-slate-400 group-hover:text-white" />}
                </button>
                <button onClick={toggleFullscreen} className={`px-3 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg transition-all shadow-lg flex items-center gap-2 text-white font-bold text-xs ${isFullscreen ? 'ring-2 ring-blue-400 ring-offset-2 ring-offset-slate-900' : ''}`}>
                    {isFullscreen ? <><Minimize2 size={16} /> EXIT</> : <Maximize2 size={16} />}
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
                <div className="absolute top-16 right-3 z-[60] bg-slate-800/95 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 shadow-2xl w-80 max-h-[80vh] overflow-y-auto custom-scrollbar animate-in slide-in-from-top-2 fade-in duration-200">
                    <h4 className="text-white font-black mb-6 text-sm flex items-center gap-2 uppercase tracking-wide">
                        <Settings size={14} className="text-blue-500" />
                        Intelligence Layer
                    </h4>

                    <div className="space-y-6">
                        {/* 1. Trend */}
                        <div>
                            <h5 className="text-blue-400 text-[10px] mb-3 font-black uppercase tracking-widest flex items-center gap-2">
                                <div className="w-1 h-4 bg-blue-500 rounded-full"></div>
                                Trend Analysis
                            </h5>
                            <div className="space-y-1 pl-2 border-l border-slate-700/50">
                                <Toggle label="Supertrend AI" value={chartConfig.showSupertrend} onToggle={() => setChartConfig(c => ({ ...c, showSupertrend: !c.showSupertrend }))} />
                                <Toggle label="Smart Trend Cloud" value={chartConfig.showTrendCloud} onToggle={() => setChartConfig(c => ({ ...c, showTrendCloud: !c.showTrendCloud }))} />
                                <Toggle label="SMA Array (5/20/50)" value={chartConfig.showSMA20} onToggle={() => setChartConfig(c => ({ ...c, showSMA20: !c.showSMA20, showSMA5: !c.showSMA5, showSMA50: !c.showSMA50 }))} />
                            </div>
                        </div>

                        {/* 2. Volatility & Impulse */}
                        <div>
                            <h5 className="text-emerald-400 text-[10px] mb-3 font-black uppercase tracking-widest flex items-center gap-2">
                                <div className="w-1 h-4 bg-emerald-500 rounded-full"></div>
                                Volatility & Impulse
                            </h5>
                            <div className="space-y-1 pl-2 border-l border-slate-700/50">
                                <Toggle label="Bollinger Bands" value={chartConfig.showBB} onToggle={() => setChartConfig(c => ({ ...c, showBB: !c.showBB }))} />
                                <Toggle label="RSI Scanner" value={chartConfig.showRSI} onToggle={() => setChartConfig(c => ({ ...c, showRSI: !c.showRSI }))} />
                                <Toggle label="Volume Flow" value={chartConfig.showVolume} onToggle={() => setChartConfig(c => ({ ...c, showVolume: !c.showVolume }))} />
                            </div>
                        </div>

                        {/* 3. AI & Macro */}
                        <div>
                            <h5 className="text-purple-400 text-[10px] mb-3 font-black uppercase tracking-widest flex items-center gap-2">
                                <div className="w-1 h-4 bg-purple-500 rounded-full"></div>
                                AI & Macro Vision
                            </h5>
                            <div className="space-y-1 pl-2 border-l border-slate-700/50">
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
                <div className="absolute inset-0 flex items-center justify-center bg-[#0f172a] z-10">
                    <div className="flex flex-col items-center gap-4 opacity-50">
                        <Activity className="w-10 h-10 text-blue-500 animate-pulse" />
                        <span className="text-xs font-black uppercase tracking-[0.3em] text-slate-400">Initializing Quantum Bridge...</span>
                    </div>
                </div>
            )}
        </div>
    );

    return chartContent;
};
