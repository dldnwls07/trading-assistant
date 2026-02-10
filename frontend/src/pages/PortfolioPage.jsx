import React, { useState } from 'react';
import axios from 'axios';
import { PieChart, Plus, Trash2, ArrowUpRight, TrendingUp, ShieldAlert, BarChart } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

const PortfolioPage = () => {
    const [holdings, setHoldings] = useState([
        { ticker: 'AAPL', shares: 10, avg_price: 150 },
        { ticker: 'TSLA', shares: 5, avg_price: 200 }
    ]);
    const [newHolding, setNewHolding] = useState({ ticker: '', shares: '', avg_price: '' });
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);

    const addHolding = () => {
        if (!newHolding.ticker || !newHolding.shares || !newHolding.avg_price) return;
        setHoldings([...holdings, { ...newHolding }]);
        setNewHolding({ ticker: '', shares: '', avg_price: '' });
    };

    const removeHolding = (idx) => {
        const newHoldings = [...holdings];
        newHoldings.splice(idx, 1);
        setHoldings(newHoldings);
    };

    const analyzePortfolio = async () => {
        if (holdings.length === 0) return;
        setLoading(true);
        try {
            const res = await axios.post(`${API_BASE}/api/portfolio/analyze`, { holdings });
            setAnalysis(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <PieChart className="w-6 h-6 text-blue-600" />
                Portfolio Analytics
            </h1>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Input Section */}
                <div className="bg-white shadow rounded-lg border border-gray-200 p-6">
                    <h2 className="text-lg font-bold text-gray-900 mb-4">Current Holdings</h2>
                    <ul className="divide-y divide-gray-200 mb-6">
                        {holdings.map((h, idx) => (
                            <li key={idx} className="py-3 flex justify-between items-center group">
                                <div>
                                    <span className="font-bold text-gray-900">{h.ticker}</span>
                                    <span className="text-sm text-gray-500 ml-2">{h.shares} shares @ ${h.avg_price}</span>
                                </div>
                                <button onClick={() => removeHolding(idx)} className="text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all">
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </li>
                        ))}
                    </ul>

                    <div className="grid grid-cols-3 gap-2 mb-4">
                        <input
                            placeholder="Ticker"
                            value={newHolding.ticker}
                            onChange={e => setNewHolding({ ...newHolding, ticker: e.target.value.toUpperCase() })}
                            className="border border-gray-300 rounded px-2 py-1 text-sm upppercase"
                        />
                        <input
                            placeholder="Shares"
                            type="number"
                            value={newHolding.shares}
                            onChange={e => setNewHolding({ ...newHolding, shares: Number(e.target.value) })}
                            className="border border-gray-300 rounded px-2 py-1 text-sm"
                        />
                        <input
                            placeholder="Avg Price"
                            type="number"
                            value={newHolding.avg_price}
                            onChange={e => setNewHolding({ ...newHolding, avg_price: Number(e.target.value) })}
                            className="border border-gray-300 rounded px-2 py-1 text-sm"
                        />
                    </div>
                    <button onClick={addHolding} className="w-full flex items-center justify-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold py-2 rounded transition-colors mb-4">
                        <Plus className="w-4 h-4" /> Add Asset
                    </button>

                    <button
                        onClick={analyzePortfolio}
                        disabled={loading || holdings.length === 0}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg shadow-md transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                        {loading ? 'Analyzing...' : <>Run AI Analysis <ArrowUpRight className="w-4 h-4" /></>}
                    </button>
                </div>

                {/* Results Section */}
                <div className="lg:col-span-2 space-y-6">
                    {analysis ? (
                        <>
                            {/* Key Metrics */}
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                                <div className="bg-white p-6 rounded-lg shadow border border-gray-200 text-center">
                                    <p className="text-sm text-gray-500 uppercase tracking-wide font-bold mb-1">Total Value</p>
                                    <p className="text-3xl font-black text-gray-900">${analysis.total_value?.toLocaleString()}</p>
                                </div>
                                <div className="bg-white p-6 rounded-lg shadow border border-gray-200 text-center">
                                    <p className="text-sm text-gray-500 uppercase tracking-wide font-bold mb-1">Total Return</p>
                                    <p className={`text-3xl font-black ${analysis.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {analysis.total_return > 0 ? '+' : ''}{analysis.total_return}%
                                    </p>
                                </div>
                                <div className="bg-white p-6 rounded-lg shadow border border-gray-200 text-center">
                                    <p className="text-sm text-gray-500 uppercase tracking-wide font-bold mb-1">Risk Score</p>
                                    <div className="flex items-center justify-center gap-2">
                                        <ShieldAlert className={`w-6 h-6 ${analysis.risk_score > 70 ? 'text-red-500' : 'text-green-500'}`} />
                                        <p className="text-3xl font-black text-gray-900">{analysis.risk_score}</p>
                                    </div>
                                </div>
                            </div>

                            {/* AI Recommendations */}
                            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
                                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <TrendingUp className="w-5 h-5 text-blue-600" />
                                    AI Strategy Recommendations
                                </h3>
                                <ul className="space-y-4">
                                    {analysis.recommendations?.map((rec, idx) => (
                                        <li key={idx} className="flex items-start gap-3 bg-blue-50 p-4 rounded-lg border border-blue-100">
                                            <div className="w-2 h-2 mt-2 rounded-full bg-blue-500 flex-shrink-0" />
                                            <p className="text-sm text-gray-800 leading-relaxed">{rec}</p>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            {/* Sector Allocation (Placeholder) */}
                            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
                                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <BarChart className="w-5 h-5 text-gray-600" />
                                    Diversification Analysis
                                </h3>
                                <div className="h-48 bg-gray-50 rounded flex items-center justify-center text-gray-400 text-sm">
                                    Sector allocation chart will appear here...
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg text-gray-400 p-12">
                            <PieChart className="w-16 h-16 mb-4 opacity-50" />
                            <p className="text-lg font-medium">Add holdings and run analysis to see insights.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default PortfolioPage;
