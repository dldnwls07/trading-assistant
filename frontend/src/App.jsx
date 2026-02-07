import React, { useState, useEffect } from 'react';
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
  Lock
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

function App() {
  const [ticker, setTicker] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const performAnalysis = async (symbol) => {
    if (!symbol) return;
    setLoading(true);
    setError(null);
    try {
      const [res, histRes] = await Promise.all([
        axios.get(`${API_BASE}/analyze/${encodeURIComponent(symbol)}`),
        axios.get(`${API_BASE}/history/${encodeURIComponent(symbol)}?interval=1d`)
      ]);

      setAnalysis(res.data);
      if (histRes.data && Array.isArray(histRes.data.data)) {
        setHistory(histRes.data.data);
      } else {
        setHistory([]);
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "통신 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (ticker.trim()) performAnalysis(ticker.trim());
  };

  return (
    <div className="min-h-screen p-4 md:p-8">
      {/* Top Navigation */}
      <header className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center mb-12 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-4"
        >
          <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Zap className="text-white w-6 h-6 fill-white" />
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
              QUANT<span className="text-cyan-400 text-neon">CORE</span>
              <span className="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 py-0.5 rounded-full border border-cyan-500/20 ml-2">PRO</span>
            </h1>
            <p className="text-slate-500 text-[10px] uppercase tracking-[0.2em] font-bold">Neural Trading Intelligence</p>
          </div>
        </motion.div>

        <form onSubmit={handleSearch} className="relative w-full max-w-md group">
          <div className="absolute inset-0 bg-cyan-500/20 blur-xl opacity-0 group-focus-within:opacity-100 transition-opacity"></div>
          <div className="relative glass-card search-focus flex items-center px-4 py-1.5 rounded-2xl border border-slate-700/50">
            <Search className="text-slate-500 w-5 h-5 mr-3" />
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              placeholder="Enter symbol or company (e.g. NVDA, 삼성전자)"
              className="w-full bg-transparent border-none py-3 text-sm text-white focus:outline-none placeholder:text-slate-600 font-medium"
            />
            <button type="submit" className="bg-cyan-500/10 hover:bg-cyan-500/20 p-2 rounded-xl transition-colors">
              <ChevronRight className="w-5 h-5 text-cyan-400" />
            </button>
          </div>
        </form>
      </header>

      {/* Main Dashboard Layout */}
      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

        {/* Left Section: Chart & AI Analysis */}
        <div className="lg:col-span-8 space-y-8">

          {/* Chart Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card rounded-[2.5rem] p-8 overflow-hidden relative"
          >
            <div className="flex justify-between items-center mb-8">
              <div className="flex items-center gap-3">
                <div className="w-2 h-8 bg-cyan-500 rounded-full"></div>
                <div>
                  <h2 className="text-xl font-black text-white">{analysis?.ticker || "MARKET OVERVIEW"}</h2>
                  <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest flex items-center gap-1.5">
                    <Globe className="w-3 h-3" /> REAL-TIME QUOTES
                  </p>
                </div>
              </div>
              {loading && (
                <div className="flex items-center gap-3 px-4 py-2 bg-cyan-500/10 rounded-full border border-cyan-500/20 animate-pulse">
                  <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full"></div>
                  <span className="text-[10px] font-black text-cyan-400 uppercase">Analytic Engine Running</span>
                </div>
              )}
            </div>

            <div className="h-[450px] w-full bg-slate-950/40 rounded-3xl border border-slate-800/50 overflow-hidden">
              {history.length > 0 ? (
                <StockChart data={history} interval="1d" />
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center space-y-4 opacity-30">
                  <Activity className="w-12 h-12 text-slate-500 animate-pulse" />
                  <p className="text-sm font-bold tracking-widest uppercase">Waiting for Data Stream</p>
                </div>
              )}
            </div>
          </motion.div>

          {/* AI Strategic Intelligence Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-card rounded-[2.5rem] p-10"
          >
            <div className="flex items-center gap-3 mb-8">
              <Brain className="text-cyan-400 w-6 h-6" />
              <h3 className="text-xs font-black text-slate-500 uppercase tracking-[0.3em]">AI Strategic Intelligence Report</h3>
            </div>

            <div className="relative">
              <div className="absolute -left-10 top-0 bottom-0 w-[1px] bg-gradient-to-b from-cyan-500/50 via-transparent to-transparent hidden md:block"></div>
              <div className="text-slate-300 leading-[1.8] text-lg font-light whitespace-pre-wrap">
                {analysis?.full_report || (
                  <div className="py-20 text-center opacity-20">
                    <Lock className="w-12 h-12 mx-auto mb-4" />
                    <p className="text-sm font-bold uppercase tracking-widest">Execute search to unlock AI strategy</p>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </div>

        {/* Right Section: Scores & Entry Points */}
        <div className="lg:col-span-4 space-y-8">

          {/* Analysis Score Card */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card rounded-[2.5rem] p-10 text-center relative overflow-hidden group"
          >
            <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
              <TrendingUp className="w-24 h-24 text-cyan-400" />
            </div>

            <p className="text-slate-500 text-[10px] font-black uppercase tracking-[0.3em] mb-6">Execution Confidence</p>
            <div className="relative inline-block">
              <div className="text-8xl font-black text-white tracking-tighter mb-2">
                {analysis?.final_score ?? '--'}
                <span className="text-2xl text-cyan-500 ml-1 font-bold">%</span>
              </div>
            </div>

            <div className={`mt-4 py-2 px-6 rounded-full inline-flex items-center gap-2 border font-black text-[11px] uppercase tracking-widest ${analysis?.signal === 'BUY' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' :
                analysis?.signal === 'SELL' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                  'bg-slate-500/10 text-slate-400 border-slate-700/50'
              }`}>
              <div className={`w-2 h-2 rounded-full animate-pulse ${analysis?.signal === 'BUY' ? 'bg-rose-400' : analysis?.signal === 'SELL' ? 'bg-blue-400' : 'bg-slate-400'
                }`}></div>
              {analysis?.signal || 'NEUTRAL / WAITING'}
            </div>
          </motion.div>

          {/* Tactical Price Targets */}
          <div className="space-y-4">
            <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] px-4">Tactical Execution Zone</h4>
            <PriceTarget
              label="Optimal Entry"
              value={analysis?.entry_points?.buy}
              color="text-rose-400"
              icon={<Target className="w-4 h-4" />}
            />
            <PriceTarget
              label="Primary Profit"
              value={analysis?.entry_points?.target}
              color="text-cyan-400"
              icon={<TrendingUp className="w-4 h-4" />}
            />
            <PriceTarget
              label="Capital Protection"
              value={analysis?.entry_points?.stop}
              color="text-blue-400"
              icon={<Lock className="w-4 h-4" />}
            />
          </div>

          {/* Error Message */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="p-6 bg-rose-500/10 border border-rose-500/20 rounded-3xl flex items-center gap-4"
              >
                <div className="p-2 bg-rose-500/20 rounded-xl">
                  <CircleAlert className="text-rose-500 w-5 h-5" />
                </div>
                <p className="text-xs text-rose-200 font-medium leading-relaxed">{error}</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      <footer className="max-w-7xl mx-auto mt-20 pb-10 border-t border-slate-800/50 pt-10 text-center">
        <p className="text-slate-600 text-[10px] font-bold uppercase tracking-widest opacity-50">
          Powered by QuantCore Neural Engine © 2026 Advanced Trading Systems
        </p>
      </footer>
    </div>
  );
}

function PriceTarget({ label, value, color, icon }) {
  return (
    <motion.div
      whileHover={{ x: 5 }}
      className="glass-card p-6 rounded-3xl flex items-center justify-between border-l-4 border-l-slate-800"
    >
      <div className="flex items-center gap-4">
        <div className="p-2 bg-slate-800 rounded-xl text-slate-400 group-hover:text-cyan-400 transition-colors">
          {icon}
        </div>
        <span className="text-[11px] font-black text-slate-400 uppercase tracking-widest">{label}</span>
      </div>
      <span className={`text-2xl font-black ${color} font-mono`}>{value || '---'}</span>
    </motion.div>
  );
}

export default App;
