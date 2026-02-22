import { useState, useEffect, useRef, useCallback } from 'react';
import { chatApi } from '../api/chatApi';

export function useChat() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [suggestions, setSuggestions] = useState([]);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        const fetchSuggestions = async () => {
            try {
                const fetchedSuggestions = await chatApi.getSuggestions();
                setSuggestions(fetchedSuggestions);
            } catch (err) {
                console.error(err);
            }
        };
        fetchSuggestions();
    }, []);

    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages, loading, scrollToBottom]);

    const handleSend = useCallback(async (text) => {
        const msg = text || input;
        if (!msg.trim()) return;

        const userMsg = { role: 'user', content: msg, timestamp: new Date().toLocaleTimeString() };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const responseText = await chatApi.sendMessage(msg);
            const botMsg = { role: 'assistant', content: responseText, timestamp: new Date().toLocaleTimeString() };
            setMessages(prev => [...prev, botMsg]);
        } catch (err) {
            console.error(err);
            const errorMsg = { role: 'assistant', content: "Sorry, I'm having trouble connecting to the neural network. Please check your connection or try again later.", timestamp: new Date().toLocaleTimeString() };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setLoading(false);
        }
    }, [input]);

    const clearMessages = useCallback(() => {
        setMessages([]);
    }, []);

    return {
        // State
        messages,
        input,
        setInput,
        loading,
        suggestions,

        // Refs
        messagesEndRef,

        // Actions
        handleSend,
        clearMessages
    };
}
