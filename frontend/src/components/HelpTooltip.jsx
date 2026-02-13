import React, { useState } from 'react';
import { Info, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const HelpTooltip = ({ indicatorId, title, isDark }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [view, setView] = useState('beginner');
    const [explanation, setExplanation] = useState('');
    const [loading, setLoading] = useState(false);

    const fetchExplanation = async () => {
        if (explanation) return;
        setLoading(true);
        try {
            const res = await fetch(`http://127.0.0.1:8000/api/dictionary?indicator_id=${indicatorId}&view=${view}`);
            const data = await res.json();
            setExplanation(data.explanation);
        } catch (e) {
            setExplanation("설명을 불러오는 데 실패했습니다.");
        } finally {
            setLoading(false);
        }
    };

    const handleOpen = () => {
        setIsOpen(true);
        fetchExplanation();
    };

    const toggleView = async (newView) => {
        setView(newView);
        setLoading(true);
        try {
            const res = await fetch(`http://127.0.0.1:8000/api/dictionary?indicator_id=${indicatorId}&view=${newView}`);
            const data = await res.json();
            setExplanation(data.explanation);
        } catch (e) {
            setExplanation("설명을 불러오는 데 실패했습니다.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="relative inline-block ml-1">
            <button
                onClick={(e) => { e.stopPropagation(); handleOpen(); }}
                className={`p-0.5 rounded-full transition-colors ${isDark ? 'text-slate-500 hover:text-blue-400 hover:bg-slate-800' : 'text-gray-400 hover:text-blue-600 hover:bg-gray-100'}`}
            >
                <Info className="w-3.5 h-3.5" />
            </button>

            <AnimatePresence>
                {isOpen && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/40 backdrop-blur-[2px]" onClick={() => setIsOpen(false)}>
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            onClick={(e) => e.stopPropagation()}
                            className={`w-full max-w-md p-6 rounded-3xl shadow-2xl border ${isDark ? 'bg-slate-900 border-slate-700 text-slate-100' : 'bg-white border-gray-100 text-gray-900'}`}
                        >
                            <div className="flex justify-between items-center mb-6">
                                <h4 className="text-xl font-black">{title || indicatorId}</h4>
                                <button onClick={() => setIsOpen(false)} className="p-1 rounded-full hover:bg-black/5 opacity-50">
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            <div className={`flex p-1 rounded-xl mb-6 ${isDark ? 'bg-slate-800' : 'bg-gray-100'}`}>
                                <button
                                    onClick={() => toggleView('beginner')}
                                    className={`flex-1 py-2 text-xs font-black rounded-lg transition-all ${view === 'beginner' ? (isDark ? 'bg-blue-600 text-white' : 'bg-white shadow-sm text-blue-600') : 'text-gray-500'}`}
                                >
                                    초보자 가이드
                                </button>
                                <button
                                    onClick={() => toggleView('expert')}
                                    className={`flex-1 py-2 text-xs font-black rounded-lg transition-all ${view === 'expert' ? (isDark ? 'bg-blue-600 text-white' : 'bg-white shadow-sm text-blue-600') : 'text-gray-500'}`}
                                >
                                    전문가 분석
                                </button>
                            </div>

                            <div className="min-h-[100px] flex items-center justify-center">
                                {loading ? (
                                    <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                                ) : (
                                    <p className="text-sm leading-relaxed font-medium opacity-90">
                                        {explanation}
                                    </p>
                                )}
                            </div>

                            <div className={`mt-8 pt-4 border-t text-[10px] opacity-40 italic text-center ${isDark ? 'border-slate-800' : 'border-gray-50'}`}>
                                QuantCore AI Learning Hub
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default HelpTooltip;
