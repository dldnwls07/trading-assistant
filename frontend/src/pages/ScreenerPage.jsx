import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, ArrowUpRight, ArrowDownRight, Filter, Rocket, Briefcase, Scale } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

const ScreenerPage = () => {
    const [style, setStyle] = useState('balanced');
    const [recommendations, setRecommendations] = useState([]);
    const [topMovers, setTopMovers] = useState({ gainers: [], losers: [] });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, [style]);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [recRes, movRes] = await Promise.all([
                axios.get(`${API_BASE}/api/screener/recommendations?style=${style}`),
                axios.get(`${API_BASE}/api/screener/top-movers`)
            ]);
            setRecommendations(recRes.data.recommendations || []);
            setTopMovers(movRes.data || { gainers: [], losers: [] });
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const styles = [
        { id: 'aggressive', label: 'Aggressive Growth', icon: Rocket, color: 'text-purple-600', bg: 'bg-purple-100' },
        { id: 'balanced', label: 'Balanced Tech', icon: Scale, color: 'text-blue-600', bg: 'bg-blue-100' },
        { id: 'conservative', label: 'Stable Value', icon: Briefcase, color: 'text-green-600', bg: 'bg-green-100' },
    ];

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                    <TrendingUp className="w-6 h-6 text-blue-600" />
                    AI Stock Screener
                </h1>
                <p className="text-sm text-gray-500 mt-1">Discover opportunities using advanced AI algorithms.</p>
            </div>

            {/* Top Movers Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white shadow rounded-lg border border-gray-200 overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-200 bg-green-50 flex justify-between items-center">
                        <h3 className="text-sm font-bold text-green-800 uppercase tracking-widest flex items-center gap-2">
                            <ArrowUpRight className="w-4 h-4" /> Top Gainers
                        </h3>
                    </div>
                    <ul className="divide-y divide-gray-200">
                        {topMovers.gainers?.slice(0, 5).map((stock, idx) => (
                            <li key={idx} className="px-6 py-3 flex justify-between items-center hover:bg-gray-50 transition-colors">
                                <span className="font-bold text-gray-900">{stock.ticker}</span>
                                <span className="font-bold text-green-600">+{stock.change}%</span>
                            </li>
                        ))}
                        {topMovers.gainers?.length === 0 && <li className="p-6 text-center text-gray-400 text-sm">No data available</li>}
                    </ul>
                </div>

                <div className="bg-white shadow rounded-lg border border-gray-200 overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-200 bg-red-50 flex justify-between items-center">
                        <h3 className="text-sm font-bold text-red-800 uppercase tracking-widest flex items-center gap-2">
                            <ArrowDownRight className="w-4 h-4" /> Top Losers
                        </h3>
                    </div>
                    <ul className="divide-y divide-gray-200">
                        {topMovers.losers?.slice(0, 5).map((stock, idx) => (
                            <li key={idx} className="px-6 py-3 flex justify-between items-center hover:bg-gray-50 transition-colors">
                                <span className="font-bold text-gray-900">{stock.ticker}</span>
                                <span className="font-bold text-red-600">{stock.change}%</span>
                            </li>
                        ))}
                        {topMovers.losers?.length === 0 && <li className="p-6 text-center text-gray-400 text-sm">No data available</li>}
                    </ul>
                </div>
            </div>

            {/* Strategy Selection */}
            <div className="space-y-6">
                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                    <Filter className="w-5 h-5 text-gray-500" />
                    Select Strategy
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {styles.map((s) => {
                        const Icon = s.icon;
                        const isSelected = style === s.id;
                        return (
                            <button
                                key={s.id}
                                onClick={() => setStyle(s.id)}
                                className={`flex items-center gap-4 p-4 rounded-xl border-2 transition-all ${isSelected
                                        ? `border-blue-600 bg-blue-50 shadow-md transform scale-105`
                                        : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
                                    }`}
                            >
                                <div className={`p-3 rounded-lg ${s.bg} ${s.color}`}>
                                    <Icon className="w-6 h-6" />
                                </div>
                                <div className="text-left">
                                    <p className={`font-bold ${isSelected ? 'text-blue-900' : 'text-gray-900'}`}>{s.label}</p>
                                    <p className="text-xs text-gray-500 mt-1">High potential picks</p>
                                </div>
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Recommendations Table */}
            <div className="bg-white shadow rounded-lg border border-gray-200 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="text-lg font-bold text-gray-900">AI Pick List</h3>
                </div>
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ticker</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">AI Score</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reason</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {recommendations.length > 0 ? (
                                recommendations.map((rec, idx) => (
                                    <tr key={idx} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <div className="h-8 w-8 rounded bg-gray-100 flex items-center justify-center text-xs font-bold text-gray-600 mr-3">
                                                    {rec.ticker}
                                                </div>
                                                <div className="text-sm font-medium text-gray-900">{rec.ticker}</div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${rec.score >= 80 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                                                {rec.score}/100
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-normal text-sm text-gray-500 max-w-xs">
                                            {rec.reason}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <a href="#" className="text-blue-600 hover:text-blue-900 font-bold">Analyze</a>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="4" className="px-6 py-12 text-center text-gray-500">
                                        {loading ? "Scanning markets..." : "No recommendations found for this strategy."}
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default ScreenerPage;
