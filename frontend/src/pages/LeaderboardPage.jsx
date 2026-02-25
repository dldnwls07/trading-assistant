import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const LeaderboardPage = () => {
    const [leaderboard, setLeaderboard] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isCreatorOpen, setIsCreatorOpen] = useState(false);

    // New Agent Form State
    const [name, setName] = useState('');
    const [llmWeight, setLlmWeight] = useState(50);
    const [risk, setRisk] = useState('medium');
    const [initialBalanceUSD, setInitialBalanceUSD] = useState(10000);
    const [exchangeRate, setExchangeRate] = useState(1350);

    const fetchLeaderboard = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/agents/leaderboard');
            const data = await res.json();
            if (data.status === 'success') {
                setLeaderboard(data.leaderboard);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLeaderboard();
        fetch('http://localhost:8000/api/exchange-rate')
            .then(res => res.json())
            .then(data => { if (data.rate) setExchangeRate(data.rate); })
            .catch(err => console.error("Exchange rate error:", err));
    }, []);

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            const rlWeight = 100 - llmWeight;
            await fetch('http://localhost:8000/api/agents', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name,
                    llm_weight: llmWeight / 100,
                    rl_weight: rlWeight / 100,
                    risk_tolerance: risk,
                    base_llm: 'gemini',
                    initial_balance: initialBalanceUSD * exchangeRate
                })
            });
            setIsCreatorOpen(false);
            setName('');
            setInitialBalanceUSD(10000);
            fetchLeaderboard();
        } catch (e) {
            console.error(e);
        }
    };

    const handleToggle = async (id, currentStatus) => {
        try {
            await fetch(`http://localhost:8000/api/agents/${id}/toggle`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_active: currentStatus ? 0 : 1 })
            });
            fetchLeaderboard();
        } catch (e) {
            console.error(e);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("정말로 이 에이전트와 연관된 모든 가상 계좌 데이터를 삭제하시겠습니까?")) return;
        try {
            await fetch(`http://localhost:8000/api/agents/${id}`, {
                method: 'DELETE'
            });
            fetchLeaderboard();
        } catch (e) {
            console.error(e);
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-black bg-clip-text text-transparent bg-gradient-to-r from-yellow-400 to-amber-500 uppercase tracking-tighter">
                        AI 리그 (리더보드)
                    </h1>
                    <p className="text-muted-foreground mt-2 font-mono">나만의 AI 펀드 매니저를 만들고 수익률을 겨뤄보세요.</p>
                </div>
                <button
                    onClick={() => setIsCreatorOpen(true)}
                    className="bg-yellow-400 hover:bg-yellow-500 text-black px-4 py-2 rounded-lg font-bold transition-all shadow-lg shadow-yellow-400/20 active:scale-95"
                >
                    + 새 에이전트 생성
                </button>
            </div>

            {isCreatorOpen && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-[#0f0f13] border border-zinc-800 p-6 rounded-xl w-full max-w-md shadow-2xl"
                    >
                        <h2 className="text-xl font-bold mb-4">🤖 커스텀 에이전트 생성</h2>
                        <form onSubmit={handleCreate} className="space-y-4">
                            <div>
                                <label className="block text-sm mb-1 text-zinc-400">에이전트 이름</label>
                                <input
                                    type="text" required value={name} onChange={e => setName(e.target.value)}
                                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-white focus:ring-2 focus:ring-yellow-400 outline-none transition-all"
                                    placeholder="예: 기술주 집중 공격형 봇"
                                />
                            </div>
                            <div>
                                <label className="block text-sm mb-2 text-zinc-400">
                                    분석 방법 (LLM: {llmWeight}% / 퀀트: {100 - llmWeight}%)
                                </label>
                                <input
                                    type="range" min="0" max="100" value={llmWeight}
                                    onChange={e => setLlmWeight(Number(e.target.value))}
                                    className="w-full h-2 bg-zinc-800 rounded-lg appearance-none cursor-pointer"
                                />
                                <div className="flex justify-between text-xs text-zinc-500 mt-2">
                                    <span>⬅️ 퀀트(RL) 집중</span>
                                    <span>기본적분석(LLM) 집중 ➡️</span>
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm mb-1 text-zinc-400">위험 선호도</label>
                                <select
                                    value={risk} onChange={e => setRisk(e.target.value)}
                                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-white focus:ring-2 focus:ring-yellow-400 outline-none"
                                >
                                    <option value="low">안전 추구 (Low Risk)</option>
                                    <option value="medium">중립 (Medium Risk)</option>
                                    <option value="high">공격적 (High Risk)</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm mb-1 text-zinc-400">초기 투자 자본금($)</label>
                                <input
                                    type="number" required value={initialBalanceUSD} onChange={e => setInitialBalanceUSD(Number(e.target.value))}
                                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-white focus:ring-2 focus:ring-yellow-400 outline-none transition-all"
                                    placeholder="예: 10000"
                                    min="1"
                                    step="1"
                                />
                            </div>
                            <div className="flex justify-end gap-3 mt-8">
                                <button type="button" onClick={() => setIsCreatorOpen(false)} className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition-colors">취소</button>
                                <button type="submit" className="px-4 py-2 bg-yellow-400 hover:bg-yellow-500 text-black rounded-lg font-bold transition-colors">생성하기</button>
                            </div>
                        </form>
                    </motion.div>
                </div>
            )}

            {loading ? (
                <div className="text-center py-20 text-zinc-500 animate-pulse">데이터를 불러오는 중입니다...</div>
            ) : (
                <div className="grid gap-4">
                    {leaderboard.map((agent) => (
                        <motion.div
                            key={agent.agent_id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-[#121216] border border-zinc-800/50 p-5 rounded-2xl flex flex-col md:flex-row md:items-center justify-between shadow-lg hover:border-zinc-700 transition-colors"
                        >
                            <div className="flex items-center gap-5">
                                <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-xl ${agent.rank === 1 ? 'bg-yellow-500/10 text-yellow-500 border border-yellow-500/20' : agent.rank === 2 ? 'bg-zinc-300/10 text-zinc-300 border border-zinc-300/20' : agent.rank === 3 ? 'bg-orange-500/10 text-orange-400 border border-orange-500/20' : 'bg-zinc-800/50 text-zinc-500'}`}>
                                    {agent.rank}
                                </div>
                                <div>
                                    <h3 className="font-bold text-lg flex items-center gap-3">
                                        {agent.name}
                                        <span className={`text-[10px] px-2 py-1 rounded-full uppercase tracking-wider font-semibold ${agent.is_active ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
                                            {agent.is_active ? 'Active' : 'Paused'}
                                        </span>
                                    </h3>
                                    <div className="text-sm text-zinc-400 flex gap-4 mt-1.5">
                                        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-500"></span> LLM {agent.llm_weight * 100}%</span>
                                        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-purple-500"></span> RL {agent.rl_weight * 100}%</span>
                                        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500"></span> 종목 {agent.positions_count}개</span>
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center gap-8 mt-4 md:mt-0 pt-4 md:pt-0 border-t border-zinc-800/50 md:border-0">
                                <div className="text-right">
                                    <div className="text-xs text-zinc-500 uppercase tracking-wider mb-1">총 자산</div>
                                    <div className="font-mono text-lg text-yellow-500">${(agent.total_value / exchangeRate).toLocaleString(undefined, { maximumFractionDigits: 2 })}</div>
                                </div>
                                <div className="text-right">
                                    <div className="text-xs text-zinc-500 uppercase tracking-wider mb-1">수익률</div>
                                    <div className={`font-mono font-bold text-lg ${agent.roi >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                        {agent.roi > 0 ? '+' : ''}{agent.roi.toFixed(2)}%
                                    </div>
                                </div>
                                <button
                                    onClick={() => handleToggle(agent.agent_id, agent.is_active)}
                                    className={`p-3 rounded-xl transition-colors ${agent.is_active ? 'bg-zinc-800 hover:bg-red-900/30 text-zinc-400 hover:text-red-400' : 'bg-blue-600/10 hover:bg-blue-600/20 text-blue-500'}`}
                                    title={agent.is_active ? "중지" : "시작"}
                                >
                                    {agent.is_active ? (
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                    ) : (
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                    )}
                                </button>
                                <button
                                    onClick={() => handleDelete(agent.agent_id)}
                                    className="p-3 bg-rose-500/10 hover:bg-rose-500/20 text-rose-500 rounded-xl transition-colors"
                                    title="삭제"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                                </button>
                            </div>
                        </motion.div>
                    ))}
                    {leaderboard.length === 0 && (
                        <motion.div
                            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                            className="text-center py-16 bg-zinc-900/30 border border-zinc-800/50 rounded-2xl"
                        >
                            <div className="text-4xl mb-4">🏆</div>
                            <h3 className="text-lg font-medium text-zinc-300">리더보드가 비어있습니다</h3>
                            <p className="text-zinc-500 mt-2">첫 번째 AI 펀드 매니저를 생성하여 대결을 시작해보세요!</p>
                        </motion.div>
                    )}
                </div>
            )}
        </div>
    );
};

export default LeaderboardPage;
