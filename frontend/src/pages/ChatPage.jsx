import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Bot, User, Trash2, Sparkles, AlertCircle } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

const ChatPage = ({ settings }) => {
    const [messages, setMessages] = useState([
        { id: 1, role: 'assistant', content: '안녕하세요! 저는 AI 투자 어시스턴트입니다. 어떤 종목에 대해 분석해 드릴까요? (예: "삼성전자 전망 어때?", "비트코인 지금 사도 돼?")' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [suggestions, setSuggestions] = useState([]);

    const isDark = settings?.darkMode;

    // Auto-scroll to bottom
    const messagesEndRef = useRef(null);
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };
    useEffect(scrollToBottom, [messages]);

    // Load Suggestions on mount
    useEffect(() => {
        fetchSuggestions();
    }, []);

    const fetchSuggestions = async () => {
        try {
            const res = await axios.get(`${API_BASE}/api/chat/suggestions`);
            setSuggestions(res.data.suggestions || []);
        } catch (err) {
            console.error("Failed to load suggestions", err);
        }
    };

    const handleSend = async (text = input) => {
        if (!text.trim()) return;

        const userMsg = { id: Date.now(), role: 'user', content: text };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const res = await axios.post(`${API_BASE}/api/chat`, {
                message: text,
            });

            const aiMsg = {
                id: Date.now() + 1,
                role: 'assistant',
                content: res.data.response
            };
            setMessages(prev => [...prev, aiMsg]);
        } catch (err) {
            const errorMsg = {
                id: Date.now() + 1,
                role: 'system',
                content: '죄송합니다. 서버 연결에 실패했습니다. 잠시 후 다시 시도해 주세요.'
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setLoading(false);
        }
    };

    const clearHistory = async () => {
        if (window.confirm("대화 내용을 모두 삭제하시겠습니까?")) {
            try {
                await axios.delete(`${API_BASE}/api/chat/history`);
                setMessages([{ id: Date.now(), role: 'assistant', content: '대화 기록이 초기화되었습니다. 새로운 질문을 입력해 주세요.' }]);
            } catch (err) {
                alert("초기화 실패");
            }
        }
    };

    return (
        <div className={`flex flex-col h-[calc(100vh-64px)] transition-colors duration-300 ${isDark ? 'bg-slate-950 text-slate-100' : 'bg-gray-50 text-gray-900'}`}>
            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-8 space-y-10 custom-scrollbar">
                <div className="max-w-4xl mx-auto space-y-8">
                    {messages.map((msg) => (
                        <div key={msg.id} className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`flex max-w-[85%] sm:max-w-[80%] gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>

                                {/* Avatar */}
                                <div className={`flex-shrink-0 h-12 w-12 rounded-2xl flex items-center justify-center shadow-lg transition-transform hover:scale-110 ${msg.role === 'user' ? 'bg-blue-600 text-white shadow-blue-500/20' :
                                    msg.role === 'system' ? 'bg-rose-500 text-white' : (isDark ? 'bg-slate-800 border border-slate-700 text-blue-400' : 'bg-white border border-gray-100 text-blue-600')
                                    }`}>
                                    {msg.role === 'user' ? <User className="h-6 w-6" /> :
                                        msg.role === 'system' ? <AlertCircle className="h-6 w-6" /> : <Bot className="h-7 w-7" />}
                                </div>

                                {/* Bubble */}
                                <div className={`p-5 rounded-[2rem] shadow-xl text-sm leading-relaxed whitespace-pre-wrap transition-all ${msg.role === 'user'
                                    ? 'bg-blue-600 text-white rounded-tr-none shadow-blue-500/10'
                                    : msg.role === 'system'
                                        ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded-tl-none'
                                        : (isDark ? 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none' : 'bg-white border border-gray-100 text-gray-800 rounded-tl-none')
                                    }`}>
                                    {msg.content}
                                </div>
                            </div>
                        </div>
                    ))}

                    {loading && (
                        <div className="flex w-full justify-start">
                            <div className="flex gap-4">
                                <div className={`h-12 w-12 rounded-2xl flex items-center justify-center shadow-lg ${isDark ? 'bg-slate-800 border border-slate-700' : 'bg-white border border-gray-100'}`}>
                                    <Bot className="h-7 w-7 text-blue-500 animate-pulse" />
                                </div>
                                <div className={`p-5 rounded-[2rem] rounded-tl-none shadow-xl flex items-center gap-2 ${isDark ? 'bg-slate-900 border border-slate-800' : 'bg-white border border-gray-100'}`}>
                                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input Area */}
            <div className={`p-6 border-t transition-colors ${isDark ? 'bg-slate-900/50 border-slate-800' : 'bg-white border-gray-200'}`}>
                <div className="max-w-4xl mx-auto space-y-6">

                    {/* Suggestions Chips */}
                    {!loading && suggestions.length > 0 && messages.length < 3 && (
                        <div className="flex flex-wrap gap-2 justify-center">
                            {suggestions.map((s, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => handleSend(s)}
                                    className={`px-4 py-2 text-[10px] font-black uppercase tracking-widest rounded-full border transition-all flex items-center gap-2 ${isDark ? 'bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border-blue-500/20' : 'bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-200'
                                        }`}
                                >
                                    <Sparkles className="w-3.5 h-3.5" />
                                    {s}
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Input Field */}
                    <div className="relative flex items-end gap-3">
                        <button
                            onClick={clearHistory}
                            className={`p-4 rounded-2xl transition-all ${isDark ? 'bg-slate-800 hover:bg-rose-500/10 text-slate-400 hover:text-rose-500' : 'bg-gray-100 hover:bg-rose-50 text-gray-400 hover:text-rose-500'}`}
                            title="Clear Chat"
                        >
                            <Trash2 className="w-5 h-5" />
                        </button>

                        <div className="flex-1 relative group">
                            <textarea
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' && !e.shiftKey) {
                                        e.preventDefault();
                                        handleSend();
                                    }
                                }}
                                placeholder="Analyze market harmonics..."
                                className={`w-full pl-6 pr-16 py-4 rounded-3xl border-2 transition-all resize-none text-sm max-h-48 min-h-[56px] focus:outline-none focus:ring-4 ${isDark
                                    ? 'bg-slate-800 border-slate-700 text-white placeholder:text-slate-600 focus:border-blue-500/50 focus:ring-blue-500/10'
                                    : 'bg-gray-50 border-gray-100 text-gray-900 placeholder:text-gray-300 focus:border-blue-500 focus:ring-blue-500/5 focus:bg-white'
                                    }`}
                                rows={1}
                            />
                            <button
                                onClick={() => handleSend()}
                                disabled={loading || !input.trim()}
                                className={`absolute right-2.5 bottom-2.5 p-3 rounded-2xl transition-all shadow-xl disabled:opacity-30 flex items-center gap-2 ${isDark ? 'bg-blue-600 text-white shadow-blue-500/20 hover:bg-blue-500' : 'bg-blue-600 text-white shadow-blue-500/20 hover:bg-blue-700'
                                    }`}
                            >
                                <Send className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                    <div className="text-center">
                        <p className="text-[10px] font-bold uppercase tracking-widest opacity-20">AI engine may produce inaccuracies • Quantitative verification recommended</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChatPage;
