import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { StockChart } from './components/StockChart';
import {
  Search,
  Brain,
  Target,
  TrendingUp,
  CircleAlert,
  Activity,
  ChevronRight,
  Zap,
  Globe,
  Lock,
  ArrowUpRight,
  Calendar,
  Settings,
  Eye,
  EyeOff,
  LineChart,
  BarChart3,
  MousePointer2,
  PieChart,
  Waves,
  LayoutGrid,
  Maximize2
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

const THEMES = [
  { name: 'Cyber', color: '#22d3ee', bg: 'from-cyan-400 to-blue-600' },
  { name: 'Stealth', color: '#94a3b8', bg: 'from-slate-400 to-slate-600' },
  { name: 'Bloom', color: '#fb7185', bg: 'from-rose-400 to-pink-600' }
];

const INTERVALS = [
  { label: '1m', value: '1m' },
  { label: '5m', value: '5m' },
  { label: '15m', value: '15m' },
  { label: '30m', value: '30m' },
  { label: '1h', value: '60m' },
  { label: '4h', value: '4h' },
  { label: '1D', value: '1d' },
  { label: '1W', value: '1wk' },
  { label: '1M', value: '1mo' },
  { label: '1Y', value: '1y' }
];

function App() {
  const [ticker, setTicker] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedInterval, setSelectedInterval] = useState('1d');

  // Settings State (Expanded for Multi-Indicator)
  const [showSettings, setShowSettings] = useState(false);
  const [chartOptions, setChartOptions] = useState({
    showVolume: true,
    showGrid: true,
    showSMA: true,
    showBB: true,
    showRSI: true,
    showMACD: true,
    showAIQuotes: true,
    showIchimoku: false,
    showStochastic: false,
    themeColor: '#22d3ee'
  });

  const searchRef = useRef(null);

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (ticker.length < 1) {
        setSuggestions([]);
        return;
      }
      try {
        const res = await axios.get(`${API_BASE}/search?query=${encodeURIComponent(ticker)}`);
        setSuggestions(res.data.candidates || []);
      } catch (err) {
        console.error("Suggestion fetch failed", err);
      }
    };
    const timeoutId = setTimeout(fetchSuggestions, 300);
    return () => clearTimeout(timeoutId);
  }, [ticker]);

  useEffect(() => {
    if (analysis?.ticker) {
      updateHistory(analysis.ticker, selectedInterval);
    }
  }, [selectedInterval]);

  const updateHistory = async (symbol, interval) => {
    try {
      const res = await axios.get(`${API_BASE}/history/${encodeURIComponent(symbol)}?interval=${interval}`);
      if (res.data && Array.isArray(res.data.data)) {
        setHistory(res.data.data);
      }
    } catch (err) {
      console.error("History fetch failed", err);
    }
  };

  const handleSearch = async (s) => {
    const sym = s || ticker;
    if (!sym) return;
    setLoading(true);
    setError(null);
    setAnalysis(null);
    setShowSuggestions(false);
    try {
      const resp = await axios.post(`${API_BASE}/analyze`, { ticker: sym });
      setAnalysis(resp.data);
      updateHistory(resp.data.ticker, selectedInterval);
    } catch (err) {
      setError(err.response?.data?.detail || "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  const toggleOption = (opt) => setChartOptions(prev => ({ ...prev, [opt]: !prev[opt] }));

  // Logic for Breakout Detection
  const currentPrice = history.length > 0 ? history[history.length - 1].close : null;
  const isBreakout = analysis?.entry_points?.target && currentPrice >= (analysis.entry_points.target * 0.98);

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 p-6 md:p-12 font-['Outfit'] selection:bg-cyan-500/30 overflow-x-hidden">
      {/* Premium Navigation */}
      <header className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center mb-16 gap-10">
        <motion.div initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-5 group cursor-pointer">
          <div className="w-16 h-16 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-[2rem] flex items-center justify-center shadow-[0_20px_40px_rgba(34,211,238,0.3)] group-hover:scale-110 transition-transform duration-500">
            <Zap className="text-white w-8 h-8 fill-current" />
          </div>
          <div>
            <h1 className="text-[10px] font-black text-cyan-400 uppercase tracking-[0.5em] mb-1">Neural Finance Platform</h1>
            <p className="text-3xl font-black text-white tracking-tighter">QUANTCORE <span className="text-slate-500 font-light italic">v3.1</span></p>
          </div>
        </motion.div>

        {/* Search Engine - High Tech Design */}
        <div className="relative w-full md:w-[500px] z-[100]" ref={searchRef}>
          <div className="relative group">
            <div className={`absolute -inset-1 bg-gradient-to-r ${THEMES.find(t => t.color === chartOptions.themeColor)?.bg || 'from-cyan-500 to-blue-600'} rounded-[2.5rem] blur opacity-25 group-hover:opacity-60 transition duration-1000 group-hover:duration-200`}></div>
            <div className="relative flex items-center bg-slate-900 border border-slate-700/50 rounded-[2.5rem] p-1.5 shadow-2xl backdrop-blur-xl">
              <Search className="w-6 h-6 ml-6 text-slate-500" />
              <input
                type="text"
                value={ticker}
                onChange={(e) => { setTicker(e.target.value); setShowSuggestions(true); }}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Synchronize with symbol (e.g. NVDA, AAPL)"
                className="w-full bg-transparent border-none outline-none py-4 px-6 text-xl font-bold text-white placeholder:text-slate-600 placeholder:font-medium tracking-tight"
              />
              <button
                onClick={() => handleSearch()}
                disabled={loading}
                className={`px-10 py-4 bg-gradient-to-r ${THEMES.find(t => t.color === chartOptions.themeColor)?.bg || 'from-cyan-500 to-blue-600'} rounded-[2rem] text-white font-black text-xs uppercase tracking-[0.2em] shadow-xl hover:shadow-cyan-500/20 active:scale-95 transition-all disabled:opacity-50`}
              >
                {loading ? 'SYNCING...' : 'ANALYZE'}
              </button>
            </div>
          </div>

          <AnimatePresence>
            {showSuggestions && suggestions.length > 0 && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }} className="absolute top-full left-0 right-0 mt-4 bg-slate-900/95 border border-slate-800 rounded-[2.5rem] overflow-hidden backdrop-blur-3xl shadow-[0_30px_60px_rgba(0,0,0,0.6)] z-[100]">
                {suggestions.map((s, idx) => (
                  <button key={idx} onClick={() => { setTicker(s.symbol); handleSearch(s.symbol); }} className="w-full text-left px-8 py-5 hover:bg-white/5 border-b border-white/5 last:border-none flex items-center justify-between group">
                    <div className="flex items-center gap-5">
                      <div className="w-10 h-10 bg-slate-800 rounded-2xl flex items-center justify-center font-black text-xs text-cyan-400 group-hover:bg-cyan-500 group-hover:text-white transition-all">{idx + 1}</div>
                      <div>
                        <p className="font-black text-white text-lg tracking-tight">{s.symbol}</p>
                        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">{s.shortname}</p>
                      </div>
                    </div>
                    <ChevronRight className="w-5 h-5 text-slate-700 group-hover:text-cyan-400 group-hover:translate-x-1 transition-all" />
                  </button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Settings Dropdown Advanced */}
          <div className="relative mt-4 flex justify-end">
            <button onClick={() => setShowSettings(!showSettings)} className={`p-4 rounded-full border transition-all ${showSettings ? 'bg-cyan-500/10 border-cyan-500 text-cyan-400' : 'bg-slate-900 border-slate-700/50 text-slate-500 hover:text-white'}`}>
              <Settings className={`w-6 h-6 ${showSettings ? 'animate-spin-slow' : ''}`} />
            </button>

            <AnimatePresence>
              {showSettings && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }} className="absolute top-full right-0 mt-3 w-80 glass-card rounded-[2.5rem] border border-slate-700/50 p-8 z-[200] shadow-[0_30px_60px_rgba(0,0,0,0.6)] backdrop-blur-3xl">
                  <div className="flex items-center justify-between mb-8">
                    <h4 className="text-[10px] font-black text-cyan-400 uppercase tracking-[0.3em]">Neural Viz Core</h4>
                    <LayoutGrid className="w-4 h-4 text-slate-600" />
                  </div>

                  <div className="space-y-4">
                    {/* Theme Selector */}
                    <div className="flex gap-2 mb-6">
                      {THEMES.map(t => (
                        <button
                          key={t.name}
                          onClick={() => setChartOptions(prev => ({ ...prev, themeColor: t.color }))}
                          className={`flex-1 py-2 rounded-xl text-[9px] font-black uppercase transition-all ${chartOptions.themeColor === t.color ? 'bg-slate-800 text-white border border-slate-600' : 'text-slate-500 hover:text-slate-300'}`}
                        >
                          {t.name}
                        </button>
                      ))}
                    </div>

                    <ToggleItem label="AI Pattern Auto-Drawing" active={chartOptions.showAIQuotes} onClick={() => toggleOption('showAIQuotes')} icon={<Brain className="w-3 h-3" />} />
                    <div className="h-[1px] bg-slate-800/50 my-4"></div>
                    <ToggleItem label="Oscillators (RSI/MACD)" active={chartOptions.showRSI} onClick={() => { toggleOption('showRSI'); toggleOption('showMACD'); }} icon={<Waves className="w-3 h-3" />} />
                    <ToggleItem label="Trend Bands (BB/SMA)" active={chartOptions.showBB} onClick={() => { toggleOption('showBB'); toggleOption('showSMA'); }} icon={<TrendingUp className="w-3 h-3" />} />
                    <ToggleItem label="Volume Dynamics" active={chartOptions.showVolume} onClick={() => toggleOption('showVolume')} icon={<BarChart3 className="w-3 h-3" />} />
                    <div className="h-[1px] bg-slate-800/50 my-4"></div>
                    <ToggleItem label="Grid Complexity" active={chartOptions.showGrid} onClick={() => toggleOption('showGrid')} icon={<LayoutGrid className="w-3 h-3" />} />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </header>

      {/* Breakout Banner Alert */}
      <AnimatePresence>
        {isBreakout && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="max-w-7xl mx-auto mb-8">
            <div className="bg-gradient-to-r from-cyan-500/20 to-blue-600/20 border border-cyan-500/50 rounded-[2rem] p-6 flex items-center justify-between backdrop-blur-xl">
              <div className="flex items-center gap-5">
                <div className="w-12 h-12 bg-cyan-500 rounded-2xl flex items-center justify-center animate-pulse">
                  <Zap className="text-white w-6 h-6 fill-current" />
                </div>
                <div>
                  <h5 className="text-lg font-black text-white tracking-tight">BREAKOUT DETECTED</h5>
                  <p className="text-xs text-cyan-400 font-bold uppercase tracking-widest">Price is synchronizing with AI Target Protocol</p>
                </div>
              </div>
              <div className="hidden md:flex items-center gap-10">
                <div className="text-right">
                  <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1">Target</p>
                  <p className="text-xl font-black text-white">${analysis.entry_points.target}</p>
                </div>
                <div className="h-10 w-[1px] bg-slate-800"></div>
                <div className="text-right">
                  <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1">Current</p>
                  <p className="text-xl font-black text-cyan-400 animate-pulse">${currentPrice}</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
        <div className="lg:col-span-8 space-y-10">

          {/* Chart Card */}
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} className="glass-card rounded-[3.5rem] p-10 overflow-hidden relative border border-white/5">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 gap-8">
              <div className="flex items-center gap-4">
                <div className="w-1.5 h-10 bg-gradient-to-b from-cyan-400 to-blue-600 rounded-full shadow-[0_0_20px_#22d3ee]"></div>
                <div>
                  <h2 className="text-2xl font-black text-white tracking-tight">{analysis?.display_name || "CORE STANDBY"}</h2>
                  <div className="flex items-center gap-3 mt-2">
                    <Activity className="w-4 h-4 text-cyan-500 animate-pulse" />
                    <span className="text-[10px] text-slate-500 font-black uppercase tracking-[0.3em]">{selectedInterval} Quantum Feed Active</span>
                  </div>
                </div>
              </div>

              {/* Interval Switcher - High End Design */}
              <div className="grid grid-cols-5 md:flex bg-slate-950/60 p-1.5 rounded-[1.5rem] border border-slate-800/60 gap-1 backdrop-blur-md">
                {INTERVALS.map((int) => (
                  <button
                    key={int.value}
                    onClick={() => setSelectedInterval(int.value)}
                    className={`px-4 py-2.5 rounded-xl text-[10px] font-black transition-all duration-300 ${selectedInterval === int.value
                      ? 'bg-cyan-500 text-slate-900 shadow-[0_0_25px_rgba(34,211,238,0.5)] scale-105'
                      : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/50'
                      }`}
                  >
                    {int.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="h-[620px] w-full bg-slate-950/40 rounded-[3rem] border border-slate-800/50 overflow-hidden relative group">
              {history.length > 0 ? (
                <StockChart data={history} interval={selectedInterval} options={chartOptions} analysis={analysis} />
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center space-y-8 bg-slate-950/20">
                  <div className="relative">
                    <div className="w-24 h-24 bg-cyan-500/5 rounded-full blur-3xl absolute inset-0 animate-pulse"></div>
                    <LineChart className="w-16 h-16 text-slate-800 relative z-10" />
                  </div>
                  <p className="text-[10px] font-black uppercase tracking-[0.5em] text-cyan-500/30 animate-pulse">Synchronizing Market Temporal Data</p>
                </div>
              )}
            </div>
          </motion.div>

          {/* AI Report Card - Ultra Premium */}
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card rounded-[3.5rem] p-12 relative overflow-hidden group">
            <div className="absolute -top-32 -right-32 w-96 h-96 bg-cyan-500/5 rounded-full blur-[100px] group-hover:bg-cyan-500/10 transition-all duration-1000"></div>
            <div className="flex items-center gap-5 mb-12">
              <div className="w-14 h-14 bg-gradient-to-br from-slate-900 to-slate-800 rounded-3xl flex items-center justify-center border border-white/5 shadow-2xl">
                <Brain className="text-cyan-400 w-7 h-7" />
              </div>
              <div>
                <h3 className="text-xs font-black text-slate-400 uppercase tracking-[0.6em] mb-1">Strategic Intelligence Report</h3>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                  <p className="text-[10px] text-cyan-500 font-bold uppercase tracking-widest">Protocol Engine Ultra-High</p>
                </div>
              </div>
            </div>
            <div className="text-slate-300 leading-[2.2] text-xl font-light whitespace-pre-wrap selection:bg-cyan-500/40 pr-4 first-letter:text-5xl first-letter:font-black first-letter:text-cyan-400 first-letter:mr-3 first-letter:float-left mb-10">
              {analysis?.full_report || (
                <div className="py-32 text-center opacity-30">
                  <Lock className="w-12 h-12 mx-auto mb-6 text-slate-600" />
                  <p className="text-xs font-black uppercase tracking-[0.4em]">Encrypted Dataset - Clearance Required</p>
                </div>
              )}
            </div>

            {/* Pattern Intelligence Grid */}
            {analysis?.daily_analysis?.patterns?.length > 0 && (
              <div className="mt-12 pt-12 border-t border-slate-800/50">
                <div className="flex items-center gap-3 mb-8">
                  <PieChart className="w-5 h-5 text-cyan-400" />
                  <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.4em]">Pattern Convergence Intelligence</h4>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {analysis.daily_analysis.patterns.map((p, idx) => (
                    <div key={idx} className="bg-slate-900/50 border border-slate-800 p-6 rounded-[2rem] hover:border-cyan-500/30 transition-all group">
                      <div className="flex justify-between items-start mb-3">
                        <span className="text-sm font-black text-white group-hover:text-cyan-400 transition-colors">{p.name}</span>
                        <div className="flex gap-0.5">
                          {[...Array(5)].map((_, i) => (
                            <div key={i} className={`w-2 h-2 rounded-full ${i < Math.round(p.reliability || 0) ? 'bg-cyan-500' : 'bg-slate-800'}`}></div>
                          ))}
                        </div>
                      </div>
                      <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-4 inline-block px-3 py-1 bg-slate-800 rounded-full">{p.type.replace('_', ' ')}</p>
                      <p className="text-[11px] text-slate-400 leading-relaxed font-medium">{p.desc}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        </div>

        {/* Sidebar - Advanced Analytics */}
        <div className="lg:col-span-4 space-y-10">
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="glass-card rounded-[4rem] p-14 text-center relative overflow-hidden group shadow-[0_40px_100px_rgba(0,0,0,0.4)] border border-white/5">
            <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/10 via-transparent to-blue-500/5"></div>
            <p className="text-slate-500 text-[10px] font-black uppercase tracking-[0.6em] mb-14 relative group-hover:text-cyan-400 transition-colors">Neural Confidence Rank</p>
            <div className="relative inline-block mb-12 scale-110 md:scale-125">
              <div className="absolute inset-0 bg-cyan-400/20 blur-[120px] rounded-full animate-pulse"></div>
              <div className="relative text-[12rem] font-black text-white leading-none tracking-tighter drop-shadow-[0_0_50px_rgba(34,211,238,0.3)] select-none">
                {analysis?.final_score ?? '--'}
                <span className="text-3xl text-cyan-400 align-top mt-10 inline-block drop-shadow-none font-bold">%</span>
              </div>
            </div>
            <div className={`mt-4 py-5 px-14 rounded-[2.5rem] inline-flex items-center gap-5 border text-sm font-black uppercase tracking-[0.3em] shadow-2xl backdrop-blur-2xl transition-all duration-700 active:scale-95 cursor-pointer ${analysis?.signal?.includes('BUY') ? 'bg-rose-500/20 text-rose-400 border-rose-500/30' :
              analysis?.signal?.includes('SELL') ? 'bg-blue-500/20 text-blue-400 border-blue-500/30' : 'bg-slate-900/90 text-slate-600 border-slate-700'
              }`}>
              <div className={`w-3.5 h-3.5 rounded-full ${analysis?.signal ? 'animate-ping' : ''} bg-current`}></div>
              {analysis?.signal || 'STANDBY'}
            </div>
          </motion.div>

          <div className="space-y-5">
            <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.6em] px-12 mb-8">Tactical Order Parameters</h4>
            <PriceTarget label="Optimal Entry" value={analysis?.entry_points?.buy} color="text-rose-400" icon={<Target className="w-6 h-6" />} delay={0.2} />
            <PriceTarget label="Projected Target" value={analysis?.entry_points?.target} color="text-cyan-400" icon={<TrendingUp className="w-6 h-6" />} delay={0.3} />
            <PriceTarget label="Defense Threshold" value={analysis?.entry_points?.stop} color="text-blue-400" icon={<Lock className="w-6 h-6" />} delay={0.4} />
          </div>

          {error && (
            <motion.div initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} className="p-10 bg-rose-500/5 border border-rose-500/20 rounded-[3.5rem] shadow-2xl relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-rose-500"></div>
              <div className="flex items-center gap-5 mb-6">
                <CircleAlert className="text-rose-500 w-8 h-8 animate-bounce" />
                <h5 className="text-rose-400 font-black text-sm uppercase tracking-[0.3em]">Neural Link Error</h5>
              </div>
              <p className="text-xs text-rose-300/60 font-medium leading-[2] tracking-wide">{error}</p>
            </motion.div>
          )}
        </div>
      </main>

      <footer className="max-w-7xl mx-auto mt-40 pb-20 border-t border-slate-800/40 pt-20 flex flex-col md:flex-row justify-between items-center opacity-20 hover:opacity-100 transition-opacity duration-700">
        <p className="text-slate-500 text-[11px] font-black uppercase tracking-[0.4em]">QuantCore Intelligence Ultra © 2026</p>
        <div className="flex gap-14 mt-10 md:mt-0 text-[10px] font-black uppercase tracking-[0.3em] text-slate-600">
          <span className="hover:text-cyan-400 transition-colors cursor-crosshair">Stream v4.2.0</span>
          <span className="hover:text-cyan-400 transition-colors cursor-crosshair">Logic Engine PRO</span>
          <span className="hover:text-cyan-400 transition-colors cursor-crosshair">Grid: 102.5.1A</span>
        </div>
      </footer>
    </div>
  );
}

function ToggleItem({ label, active, onClick, icon }) {
  return (
    <button onClick={onClick} className="w-full flex items-center justify-between text-left group p-2 hover:bg-white/[0.03] rounded-2xl transition-all duration-300">
      <div className="flex items-center gap-4">
        <div className={`p-2 rounded-lg transition-all ${active ? 'bg-cyan-500/20 text-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.2)]' : 'bg-slate-900 text-slate-700'}`}>
          {icon}
        </div>
        <span className={`text-[11px] font-black transition-colors uppercase tracking-tight ${active ? 'text-slate-200' : 'text-slate-600 group-hover:text-slate-400'}`}>{label}</span>
      </div>
      <div className={`w-10 h-5 rounded-full relative transition-all duration-500 ${active ? 'bg-cyan-500' : 'bg-slate-800'}`}>
        <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all duration-300 ${active ? 'left-6' : 'left-1'}`}></div>
      </div>
    </button>
  );
}

function PriceTarget({ label, value, color, icon, delay }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
      whileHover={{ scale: 1.05, x: 15 }}
      className="glass-card p-8 rounded-[3rem] flex items-center justify-between border border-white/5 hover:border-cyan-500/30 transition-all cursor-pointer group shadow-2xl relative overflow-hidden"
    >
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
      <div className="flex items-center gap-6 relative">
        <div className="w-14 h-14 bg-slate-950/80 rounded-[1.5rem] flex items-center justify-center text-slate-600 group-hover:text-cyan-400 transition-all border border-slate-800 shadow-inner">{icon}</div>
        <span className="text-[11px] font-black text-slate-500 group-hover:text-slate-200 uppercase tracking-[0.4em] transition-colors">{label}</span>
      </div>
      <span className={`text-4xl font-black ${color} font-mono tracking-tighter relative group-hover:scale-110 transition-transform`}>{value || '---'}</span>
    </motion.div>
  );
}

export default App;
