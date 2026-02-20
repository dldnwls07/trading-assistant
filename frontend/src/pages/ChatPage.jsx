import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import {
    Sparkles,
    Trash2,
    Bot,
    MessageSquare,
    User,
    History,
    Send,
    TrendingUp,
    BarChart3
} from 'lucide-react';
import { useTranslation } from '../utils/translations';
import api from '../utils/api';

const ChatPage = ({ settings }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [suggestions, setSuggestions] = useState([]);
    const messagesEndRef = useRef(null);

    const isDark = settings?.darkMode;
    const t = useTranslation(settings);

    useEffect(() => {
        const fetchSuggestions = async () => {
            try {
                const res = await api.get('/api/chat/suggestions');
                setSuggestions(res.data.suggestions || []);
            } catch (err) { console.error(err); }
        };
        fetchSuggestions();
    }, []);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, loading]);

    const handleSend = async (text) => {
        const msg = text || input;
        if (!msg.trim()) return;

        const userMsg = { role: 'user', content: msg, timestamp: new Date().toLocaleTimeString() };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const res = await api.post('/api/chat', { message: msg });
            const botMsg = { role: 'assistant', content: res.data.response, timestamp: new Date().toLocaleTimeString() };
            setMessages(prev => [...prev, botMsg]);
        } catch (err) {
            console.error(err);
            const errorMsg = { role: 'assistant', content: "Sorry, I'm having trouble connecting to the neural network. Please check your connection or try again later.", timestamp: new Date().toLocaleTimeString() };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setLoading(false);
        }
    };

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
    };

    const bubbleVariants = {
        hidden: { opacity: 0, y: 10, scale: 0.95 },
        visible: { opacity: 1, y: 0, scale: 1, transition: { type: 'spring', stiffness: 300, damping: 24 } }
    };

    return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="min-h-screen py-6 md:py-10 flex flex-col transition-all duration-300 bg-[#09090b] text-foreground relative">

            {/* Header */}
            <div className="max-w-4xl mx-auto w-full px-4 sm:px-6 mb-6">
                <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="flex items-center justify-between pb-6 border-b border-white/5">
                    <h1 className="text-3xl font-black tracking-tighter flex items-center gap-3 text-zinc-100 uppercase">
                        <div className="bg-yellow-400 p-2 rounded-xl text-black shadow-lg shadow-yellow-400/20">
                            <Sparkles className="w-7 h-7" />
                        </div>
                        AI {t.nav_chat || 'Assistant'}
                    </h1>

                    <button onClick={() => setMessages([])} className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 text-zinc-500 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-yellow-400 border border-white/10">
                        <Trash2 className="w-4 h-4" /> Clear_Buffer
                    </button>
                </motion.div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto px-4 sm:px-6 max-w-4xl mx-auto w-full custom-scrollbar">
                {messages.length === 0 ? (
                    <motion.div initial="hidden" animate="visible" variants={containerVariants} className="flex flex-col items-center justify-center h-full text-center space-y-8 py-20">
                        <motion.div variants={bubbleVariants} className="w-24 h-24 bg-yellow-400/5 rounded-full flex items-center justify-center border-4 border-yellow-400/20 shadow-2xl shadow-yellow-400/10">
                            <Bot className="w-12 h-12 text-yellow-400" />
                        </motion.div>
                        <motion.div variants={bubbleVariants} className="space-y-2">
                            <h2 className="text-2xl font-black tracking-tighter text-zinc-100 uppercase">How can I assist your trading today?</h2>
                            <p className="text-zinc-500 font-bold text-sm tracking-tight uppercase">Ask about market trends, technical patterns, or specific tickers.</p>
                        </motion.div>

                        <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8 w-full max-w-2xl">
                            {suggestions.slice(0, 4).map((s, i) => (
                                <motion.button
                                    variants={bubbleVariants}
                                    key={i}
                                    onClick={() => handleSend(s)}
                                    className="p-4 text-left rounded-2xl border bg-white/5 backdrop-blur-sm border-white/10 hover:border-yellow-400/50 hover:bg-white/10 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-yellow-400 group"
                                >
                                    <MessageSquare className="w-4 h-4 mb-3 text-yellow-400 opacity-40 group-hover:opacity-100 transition-opacity" />
                                    <p className="text-xs font-bold text-zinc-400 group-hover:text-zinc-100 transition-colors uppercase tracking-tight">{s}</p>
                                </motion.button>
                            ))}
                            {suggestions.length === 0 && (
                                <>
                                    <button onClick={() => handleSend("What is the current market sentiment?")} className="p-4 text-left rounded-2xl border bg-white/5 border-white/10 hover:border-yellow-400/50 hover:bg-white/10 transition-all text-xs font-bold text-zinc-400 uppercase tracking-tight"><MessageSquare className="w-4 h-4 mb-3 text-yellow-400 opacity-40" />What is the current market sentiment?</button>
                                    <button onClick={() => handleSend("Analyze AAPL chart patterns.")} className="p-4 text-left rounded-2xl border bg-white/5 border-white/10 hover:border-yellow-400/50 hover:bg-white/10 transition-all text-xs font-bold text-zinc-400 uppercase tracking-tight"><MessageSquare className="w-4 h-4 mb-3 text-yellow-400 opacity-40" />Analyze AAPL chart patterns.</button>
                                </>
                            )}
                        </motion.div>
                    </motion.div>
                ) : (
                    <motion.div initial="hidden" animate="visible" variants={containerVariants} className="space-y-6 pb-6">
                        {messages.map((m, i) => (
                            <motion.div variants={bubbleVariants} key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`flex gap-4 max-w-[85%] ${m.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                                    <div className={`shrink-0 w-10 h-10 rounded-2xl flex items-center justify-center shadow-lg ${m.role === 'user' ? 'bg-yellow-400 text-black shadow-yellow-400/20' : 'bg-white/5 border border-white/10 text-zinc-100'}`}>
                                        {m.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                                    </div>
                                    <div className={`p-5 rounded-3xl ${m.role === 'user' ? 'bg-yellow-400 text-black border border-yellow-400/20 rounded-tr-sm shadow-xl shadow-yellow-400/10' : 'bg-white/5 backdrop-blur-md border border-white/10 text-zinc-100 rounded-tl-sm shadow-xl'}`}>
                                        <p className="text-sm font-bold leading-relaxed whitespace-pre-wrap tracking-tight">{m.content}</p>
                                        <div className={`text-[9px] font-black uppercase tracking-widest mt-3 opacity-50 flex items-center gap-1 font-mono ${m.role === 'user' ? 'justify-end text-black' : 'justify-start text-zinc-500'}`}>
                                            <History className="w-3 h-3" /> {m.timestamp}
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                        {loading && (
                            <motion.div variants={bubbleVariants} className="flex justify-start">
                                <div className="flex gap-4 max-w-[85%]">
                                    <div className="shrink-0 w-10 h-10 rounded-2xl flex items-center justify-center shadow-lg bg-white/5 border border-white/10 text-zinc-100">
                                        <Bot className="w-5 h-5" />
                                    </div>
                                    <div className="p-5 rounded-3xl bg-white/5 backdrop-blur-md border border-white/10 text-zinc-100 rounded-tl-sm shadow-xl flex items-center gap-2">
                                        <div className="w-2 h-2 bg-yellow-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                                        <div className="w-2 h-2 bg-yellow-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                        <div className="w-2 h-2 bg-yellow-400 rounded-full animate-bounce"></div>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                        <div ref={messagesEndRef} />
                    </motion.div>
                )}
            </div>

            {/* Input Area */}
            <div className="px-4 sm:px-6 py-6 max-w-4xl mx-auto w-full bg-[#09090b]/80 backdrop-blur-xl border-t border-white/5 mt-auto sticky bottom-0 z-20">
                <div className="flex items-center gap-4 bg-white/5 p-2 pl-6 rounded-3xl border border-white/10 focus-within:border-yellow-400 focus-within:ring-2 focus-within:ring-yellow-400/20 transition-all shadow-xl">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        className="flex-1 bg-transparent border-none text-zinc-100 font-bold outline-none focus-visible:outline-none focus-visible:ring-0 rounded-lg px-2 py-1 placeholder-zinc-600 min-w-0"
                        placeholder="Ask AI anything about the markets..."
                        autoComplete="off"
                        spellCheck={false}
                    />
                    <button
                        onClick={() => handleSend()}
                        disabled={loading || !input.trim()}
                        className="bg-yellow-400 text-black p-4 rounded-2xl hover:bg-yellow-400/90 transition-all shadow-lg shadow-yellow-400/20 disabled:opacity-50 disabled:scale-100 hover:scale-105 active:scale-95 flex-shrink-0"
                        aria-label="Send message"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </motion.div>
    );
};

export default ChatPage;
