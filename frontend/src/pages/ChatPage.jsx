import React, { useState, useEffect, useRef } from 'react';
import { Send, User, Bot, Sparkles, MessageSquare, History, Trash2, Cpu, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
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
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={`min-h-screen flex flex-col transition-colors duration-300 ${isDark ? 'bg-slate-950 text-slate-100' : 'bg-gray-50 text-gray-900'}`}>
            {/* UI 구현 생략 (기존과 동일하되 api 사용) */}
            <div className="flex-1 overflow-y-auto p-4 max-w-4xl mx-auto w-full">
                {messages.map((m, i) => (
                    <div key={i} className={`mb-4 flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`p-4 rounded-2xl max-w-[80%] ${m.role === 'user' ? 'bg-blue-600 text-white' : (isDark ? 'bg-slate-900 border border-slate-800' : 'bg-white border border-gray-100')}`}>
                            {m.content}
                        </div>
                    </div>
                ))}
                {loading && <div className="text-center opacity-50 italic">AI Thinking...</div>}
                <div ref={messagesEndRef} />
            </div>

            <div className="p-4 border-t border-slate-800 max-w-4xl mx-auto w-full">
                <div className="flex gap-2">
                    <input type="text" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSend()} className="flex-1 bg-slate-900 border border-slate-800 p-3 rounded-xl outline-none" placeholder="Ask AI anything..." />
                    <button onClick={() => handleSend()} className="bg-blue-600 p-3 rounded-xl"><Send className="w-5 h-5" /></button>
                </div>
            </div>
        </div>
    );
};

export default ChatPage;
