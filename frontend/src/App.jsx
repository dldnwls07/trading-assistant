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
  MousePointer2
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

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

  // Settings State
  const [showSettings, setShowSettings] = useState(false);
  const [chartOptions, setChartOptions] = useState({
    showVolume: true,
    showGrid: true,
    showSMA: true,
    showBB: true,
    showRSI: false,
    showMACD: false,
    showAIQuotes: true,
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
      console.error("History update failed", err);
    }
  };

  const performAnalysis = async (symbol) => {
    if (!symbol) return;
    setLoading(true);
    setError(null);
    setShowSuggestions(false);
    try {
      const [res, histRes] = await Promise.all([
        axios.get(`${API_BASE}/analyze/${encodeURIComponent(symbol)}`),
        axios.get(`${API_BASE}/history/${encodeURIComponent(symbol)}?interval=${selectedInterval}`)
      ]);

      setAnalysis(res.data);
      if (histRes.data && Array.isArray(histRes.data.data)) {
        setHistory(histRes.data.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "통신 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const selectSuggestion = (suggestion) => {
    setTicker(suggestion.symbol);
    performAnalysis(suggestion.symbol);
  };

  const toggleOption = (key) => {
    setChartOptions(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="min-h-screen p-4 md:p-8">
      {/* Top Header */}
      <header className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center mb-12 gap-6">
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-4">
          <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-cyan-500/20 pointer-events-none">
            <Zap className="text-white w-6 h-6 fill-white" />
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-2 cursor-default">
              QUANT<span className="text-cyan-400 text-neon">CORE</span>
              <span className="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 py-0.5 rounded-full border border-cyan-500/20 ml-2">PRO</span>
            </h1>
            <p className="text-slate-500 text-[10px] uppercase tracking-[0.2em] font-bold">Neural Trading Intelligence</p>
          </div>
        </motion.div>

        <div className="relative w-full max-w-md group" ref={searchRef}>
          <form onSubmit={(e) => { e.preventDefault(); performAnalysis(ticker); }}>
            <div className="absolute inset-0 bg-cyan-500/20 blur-xl opacity-0 group-focus-within:opacity-100 transition-opacity"></div>
            <div className="relative glass-card search-focus flex items-center px-4 py-1.5 rounded-2xl border border-slate-700/50">
              <Search className="text-slate-500 w-5 h-5 mr-3" />
              <input
                type="text" value={ticker}
                onFocus={() => setShowSuggestions(true)}
                onChange={(e) => { setTicker(e.target.value); setShowSuggestions(true); }}
                placeholder="Search symbol or name..."
                className="w-full bg-transparent border-none py-3 text-sm text-white focus:outline-none placeholder:text-slate-600 font-medium"
              />
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => setShowSettings(!showSettings)}
                  type="button"
                  className={`p-2 rounded-xl transition-all ${showSettings ? 'bg-cyan-500 text-slate-900 shadow-[0_0_15px_#22d3ee]' : 'text-slate-400 hover:bg-slate-800'}`}
                >
                  <Settings className="w-5 h-5" />
                </button>
                <button type="submit" className="bg-cyan-400 hover:bg-cyan-500 p-2 rounded-xl transition-colors text-slate-900 shadow-lg shadow-cyan-500/20">
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          </form>

          {/* Autocomplete Dropdown */}
          <AnimatePresence>
            {showSuggestions && suggestions.length > 0 && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }} className="absolute top-full left-0 right-0 mt-2 glass-card rounded-2xl border border-slate-700/50 overflow-hidden z-[200] shadow-2xl">
                <div className="p-2 space-y-1">
                  {suggestions.map((s, idx) => (
                    <button key={idx} onClick={() => selectSuggestion(s)} className="w-full text-left flex items-center justify-between p-3 rounded-xl hover:bg-cyan-500/10 group transition-colors">
                      <div className="flex flex-col">
                        <span className="text-white font-black text-sm group-hover:text-cyan-400">{s.name}</span>
                        <span className="text-xs text-slate-500">{s.symbol} • {s.exchange}</span>
                      </div>
                      <ArrowUpRight className="w-4 h-4 text-slate-600 group-hover:text-cyan-400" />
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Settings Dropdown Advanced */}
          <AnimatePresence>
            {showSettings && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }} className="absolute top-full right-0 mt-2 w-72 glass-card rounded-[2rem] border border-slate-700/50 p-6 z-[200] shadow-2xl">
                <h4 className="text-[10px] font-black text-cyan-400 uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
                  <MousePointer2 className="w-3 h-3" /> Visualization Core
                </h4>
                <div className="space-y-4">
                  <ToggleItem label="AI Auto-Drawing" active={chartOptions.showAIQuotes} onClick={() => toggleOption('showAIQuotes')} />
                  <div className="h-[1px] bg-slate-800/50 my-2"></div>
                  <ToggleItem label="Volume Dynamics" active={chartOptions.showVolume} onClick={() => toggleOption('showVolume')} />
                  <ToggleItem label="Moving Averages" active={chartOptions.showSMA} onClick={() => toggleOption('showSMA')} />
                  <ToggleItem label="Bollinger Bands" active={chartOptions.showBB} onClick={() => toggleOption('showBB')} />
                  <div className="h-[1px] bg-slate-800/50 my-2"></div>
                  <ToggleItem label="RSI Oscillator" active={chartOptions.showRSI} onClick={() => toggleOption('showRSI')} />
                  <ToggleItem label="MACD Indicator" active={chartOptions.showMACD} onClick={() => toggleOption('showMACD')} />
                  <ToggleItem label="Chart Grid" active={chartOptions.showGrid} onClick={() => toggleOption('showGrid')} />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <div className="lg:col-span-8 space-y-8">

          {/* Chart Card */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card rounded-[2.5rem] p-8 overflow-hidden relative">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-6">
              <div className="flex items-center gap-3">
                <div className="w-2 h-8 bg-cyan-500 rounded-full shadow-[0_0_20px_#22d3ee]"></div>
                <div>
                  <h2 className="text-xl font-black text-white tracking-tight">{analysis?.display_name || "READY FOR INPUT"}</h2>
                  <div className="flex items-center gap-2 mt-1">
                    <Activity className="w-3 h-3 text-cyan-500" />
                    <span className="text-[10px] text-slate-500 font-black uppercase tracking-widest">{selectedInterval} Neural Stream</span>
                  </div>
                </div>
              </div>

              {/* Interval Switcher - Responsive Grid */}
              <div className="grid grid-cols-5 md:flex bg-slate-950/40 p-1.5 rounded-2xl border border-slate-800/50 gap-1">
                {INTERVALS.map((int) => (
                  <button
                    key={int.value}
                    onClick={() => setSelectedInterval(int.value)}
                    className={`px-3 py-2 rounded-xl text-[10px] font-black transition-all ${selectedInterval === int.value
                        ? 'bg-cyan-500 text-slate-900 shadow-[0_0_20px_rgba(34,211,238,0.4)] scale-105'
                        : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/50'
                      }`}
                  >
                    {int.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="h-[550px] w-full bg-slate-950/30 rounded-[2.5rem] border border-slate-800/40 overflow-hidden relative group">
              <div className="absolute top-4 left-4 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="bg-slate-900/80 backdrop-blur px-3 py-1.5 rounded-full border border-slate-700/50 flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-rose-500 rounded-full animate-pulse"></div>
                  <span className="text-[9px] font-black text-slate-300 uppercase tracking-widest">Live Engine</span>
                </div>
              </div>
              {history.length > 0 ? (
                <StockChart data={history} interval={selectedInterval} options={chartOptions} analysis={analysis} />
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center space-y-6">
                  <div className="relative">
                    <Activity className="w-16 h-16 text-slate-800 animate-pulse" />
                    <div className="absolute inset-0 bg-cyan-500/5 blur-3xl rounded-full"></div>
                  </div>
                  <p className="text-xs font-black uppercase tracking-[0.4em] text-slate-700">Awaiting Signal Synchronization</p>
                </div>
              )}
            </div>
          </motion.div>

          {/* AI Report Card */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card rounded-[2.5rem] p-10 relative overflow-hidden">
            <div className="absolute -top-10 -right-10 opacity-[0.02] pointer-events-none transition-transform group-hover:scale-110 duration-1000">
              <Brain className="w-96 h-96" />
            </div>
            <div className="flex items-center gap-4 mb-10">
              <div className="w-12 h-12 bg-cyan-500/10 rounded-2xl flex items-center justify-center border border-cyan-500/20 shadow-inner">
                <Brain className="text-cyan-400 w-6 h-6" />
              </div>
              <div>
                <h3 className="text-xs font-black text-slate-500 uppercase tracking-[0.5em]">Neural Intelligence Analysis</h3>
                <p className="text-[9px] text-cyan-500/50 mt-1 uppercase font-bold tracking-widest">Protocol Version 9.8.2 Active</p>
              </div>
            </div>
            <div className="text-slate-300 leading-[2] text-lg font-light whitespace-pre-wrap selection:bg-cyan-500/30">
              {analysis?.full_report || (
                <div className="py-24 text-center">
                  <div className="w-20 h-20 bg-slate-900/50 rounded-[2rem] flex items-center justify-center mx-auto mb-6 border border-slate-800/50 shadow-2xl">
                    <Lock className="w-8 h-8 text-cyan-500 opacity-30" />
                  </div>
                  <p className="text-xs font-black uppercase tracking-[0.3em] text-slate-600">Encrypted Dataset Instance</p>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-4 space-y-8">
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="glass-card rounded-[3.5rem] p-12 text-center relative overflow-hidden group shadow-2xl border border-white/5">
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent"></div>
            <p className="text-slate-500 text-[10px] font-black uppercase tracking-[0.4em] mb-12 relative">Strategic Convection</p>
            <div className="relative inline-block mb-10">
              <div className="absolute inset-0 bg-cyan-500/20 blur-[100px] rounded-full"></div>
              <div className="relative text-[10rem] font-black text-white leading-none tracking-tighter drop-shadow-[0_0_30px_rgba(34,211,238,0.2)]">
                {analysis?.final_score ?? '--'}
                <span className="text-2xl text-cyan-400 align-top mt-8 inline-block drop-shadow-none">%</span>
              </div>
            </div>
            <div className={`mt-2 py-4 px-12 rounded-[2rem] inline-flex items-center gap-4 border text-[13px] font-black uppercase tracking-[0.2em] shadow-xl backdrop-blur-xl transition-all duration-500 ${analysis?.signal?.includes('BUY') ? 'bg-rose-500/20 text-rose-400 border-rose-500/30 shadow-rose-900/20' :
                analysis?.signal?.includes('SELL') ? 'bg-blue-500/20 text-blue-400 border-blue-500/30 shadow-blue-900/20' : 'bg-slate-900/80 text-slate-500 border-slate-700'
              }`}>
              <div className={`w-3 h-3 rounded-full shadow-[0_0_10px_currentColor] ${analysis?.signal ? 'animate-ping' : ''}`}></div>
              {analysis?.signal || 'WAITING'}
            </div>
          </motion.div>

          <div className="space-y-4">
            <h4 className="text-[10px] font-black text-slate-600 uppercase tracking-[0.5em] px-10 mb-6">Neural Targets</h4>
            <PriceTarget label="Precision entry" value={analysis?.entry_points?.buy} color="text-rose-400" icon={<Target className="w-5 h-5" />} delay={0.1} />
            <PriceTarget label="Quantum target" value={analysis?.entry_points?.target} color="text-cyan-400" icon={<TrendingUp className="w-5 h-5" />} delay={0.2} />
            <PriceTarget label="Capital defense" value={analysis?.entry_points?.stop} color="text-blue-400" icon={<Lock className="w-5 h-5" />} delay={0.3} />
          </div>

          {error && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="p-10 bg-rose-500/10 border border-rose-500/20 rounded-[3rem] shadow-2xl">
              <div className="flex items-center gap-4 mb-4">
                <div className="p-3 bg-rose-500/20 rounded-2xl"><CircleAlert className="text-rose-500 w-6 h-6" /></div>
                <h5 className="text-rose-400 font-black text-xs uppercase tracking-[0.2em]">Synchronization Failure</h5>
              </div>
              <p className="text-[11px] text-rose-200/60 font-medium leading-[1.8]">{error}</p>
            </motion.div>
          )}
        </div>
      </main>

      <footer className="max-w-7xl mx-auto mt-32 pb-20 border-t border-slate-800/30 pt-20 flex flex-col md:flex-row justify-between items-center opacity-20 group">
        <p className="text-slate-500 text-[10px] font-black uppercase tracking-[0.3em] group-hover:text-cyan-500 transition-colors">QuantCore Intelligence Framework © 2026</p>
        <div className="flex gap-12 mt-8 md:mt-0 text-[9px] font-black uppercase tracking-widest text-slate-600">
          <span className="cursor-help hover:text-white transition-colors">Neural Net Instance: #9921-A</span>
          <span className="cursor-help hover:text-white transition-colors">Kernel Runtime: PRO.V4</span>
        </div>
      </footer>
    </div>
  );
}

function ToggleItem({ label, active, onClick }) {
  return (
    <button onClick={onClick} className="w-full flex items-center justify-between text-left group p-1 hover:bg-white/[0.02] rounded-xl transition-all">
      <span className="text-[11px] font-bold text-slate-400 group-hover:text-cyan-400 transition-colors uppercase tracking-tight">{label}</span>
      <div className={`p-2 rounded-xl transition-all ${active ? 'bg-cyan-500/20 text-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.2)]' : 'text-slate-700 hover:text-slate-500'}`}>
        {active ? <Eye className="w-4.5 h-4.5" /> : <EyeOff className="w-4.5 h-4.5" />}
      </div>
    </button>
  );
}

function PriceTarget({ label, value, color, icon, delay }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
      whileHover={{ x: 10, scale: 1.02 }}
      className="glass-card p-7 rounded-[2.5rem] flex items-center justify-between border border-transparent hover:border-slate-700/50 transition-all cursor-pointer group shadow-2xl relative"
    >
      <div className="flex items-center gap-6 relative">
        <div className="p-4 bg-slate-900/80 rounded-2xl text-slate-600 group-hover:text-cyan-400 transition-all border border-slate-800/80 group-hover:border-cyan-500/40 shadow-inner">{icon}</div>
        <span className="text-[11px] font-black text-slate-500 group-hover:text-slate-300 uppercase tracking-[0.3em] transition-colors">{label}</span>
      </div>
      <span className={`text-3xl font-black ${color} font-mono tracking-tighter relative`}>{value || '---'}</span>
    </motion.div>
  );
}

export default App;
