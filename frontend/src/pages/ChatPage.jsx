import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Bot, User, Trash2, Sparkles, AlertCircle } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

const ChatPage = () => {
    const [messages, setMessages] = useState([
        { id: 1, role: 'assistant', content: '안녕하세요! 저는 AI 투자 어시스턴트입니다. 어떤 종목에 대해 분석해 드릴까요? (예: "삼성전자 전망 어때?", "비트코인 지금 사도 돼?")' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [suggestions, setSuggestions] = useState([]);

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
            // 실제 API 연동
            const res = await axios.post(`${API_BASE}/api/chat`, {
                message: text,
                // context: { ... } // 필요시 차트 분석 데이터 등을 컨텍스트로 전달 가능
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
        <div className="flex flex-col h-[calc(100vh-64px)] bg-gray-50">
            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
                <div className="max-w-3xl mx-auto space-y-6">
                    {messages.map((msg) => (
                        <div key={msg.id} className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`flex max-w-[85%] sm:max-w-[75%] gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>

                                {/* Avatar */}
                                <div className={`flex-shrink-0 h-10 w-10 rounded-full flex items-center justify-center shadow-sm ${msg.role === 'user' ? 'bg-blue-600 text-white' :
                                        msg.role === 'system' ? 'bg-red-100 text-red-600' : 'bg-white border border-gray-200 text-blue-600'
                                    }`}>
                                    {msg.role === 'user' ? <User className="h-5 w-5" /> :
                                        msg.role === 'system' ? <AlertCircle className="h-5 w-5" /> : <Bot className="h-6 w-6" />}
                                </div>

                                {/* Bubble */}
                                <div className={`p-4 rounded-2xl shadow-sm text-sm leading-relaxed whitespace-pre-wrap ${msg.role === 'user'
                                        ? 'bg-blue-600 text-white rounded-tr-none'
                                        : msg.role === 'system'
                                            ? 'bg-red-50 text-red-800 border border-red-100 rounded-tl-none'
                                            : 'bg-white border border-gray-200 text-gray-800 rounded-tl-none'
                                    }`}>
                                    {msg.content}
                                </div>
                            </div>
                        </div>
                    ))}

                    {loading && (
                        <div className="flex w-full justify-start">
                            <div className="flex gap-3">
                                <div className="h-10 w-10 bg-white border border-gray-200 rounded-full flex items-center justify-center shadow-sm">
                                    <Bot className="h-6 w-6 text-blue-600 animate-pulse" />
                                </div>
                                <div className="bg-white border border-gray-200 p-4 rounded-2xl rounded-tl-none shadow-sm flex items-center gap-2">
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input Area */}
            <div className="bg-white border-t border-gray-200 p-4 sticky bottom-0">
                <div className="max-w-3xl mx-auto space-y-4">

                    {/* Suggestions Chips */}
                    {!loading && suggestions.length > 0 && messages.length < 3 && (
                        <div className="flex flex-wrap gap-2 justify-center">
                            {suggestions.map((s, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => handleSend(s)}
                                    className="px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs rounded-full border border-blue-200 transition-colors flex items-center gap-1"
                                >
                                    <Sparkles className="w-3 h-3" />
                                    {s}
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Input Field */}
                    <div className="relative flex items-center gap-2">
                        <button
                            onClick={clearHistory}
                            className="p-3 text-gray-400 hover:text-red-500 hover:bg-gray-100 rounded-full transition-colors"
                            title="Clear Chat"
                        >
                            <Trash2 className="w-5 h-5" />
                        </button>

                        <div className="flex-1 relative">
                            <textarea
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' && !e.shiftKey) {
                                        e.preventDefault();
                                        handleSend();
                                    }
                                }}
                                placeholder="Ask about stocks, markets, or strategies..."
                                className="w-full pl-4 pr-12 py-3 bg-gray-100 border-none rounded-2xl focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all resize-none text-sm max-h-32 min-h-[50px] scrollbar-hide"
                                rows={1}
                            />
                            <button
                                onClick={() => handleSend()}
                                disabled={loading || !input.trim()}
                                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 transition-all shadow-md"
                            >
                                <Send className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                    <div className="text-center">
                        <p className="text-xs text-gray-400">AI can make mistakes. Consider checking important information.</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChatPage;
