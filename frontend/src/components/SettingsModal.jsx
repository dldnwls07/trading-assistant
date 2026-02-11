import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Globe, Moon, Sun, Bell, Shield, Settings } from 'lucide-react';

const SettingsModal = ({ isOpen, onClose, settings, setSettings }) => {
    if (!isOpen) return null;

    const isDark = settings?.darkMode;

    const languages = [
        { code: 'ko', name: '한국어', icon: '🇰🇷' },
        { code: 'en', name: 'English', icon: '🇺🇸' },
        { code: 'zh', name: '中文', icon: '🇨🇳' },
        { code: 'ja', name: '日本語', icon: '🇯🇵' },
    ];

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-md">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: 30 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: 30 }}
                    className={`rounded-3xl shadow-2xl w-full max-w-md overflow-hidden transition-colors duration-300 ${isDark ? 'bg-slate-900 border border-slate-800 text-slate-100' : 'bg-white border border-gray-100 text-gray-900'}`}
                >
                    {/* Header */}
                    <div className={`px-6 py-5 border-b flex items-center justify-between ${isDark ? 'border-slate-800 bg-slate-900/50' : 'border-gray-100 bg-gray-50/50'}`}>
                        <div className="flex items-center gap-3">
                            <div className="bg-blue-600 p-2 rounded-xl text-white shadow-lg shadow-blue-500/20">
                                <Settings className="w-5 h-5" />
                            </div>
                            <h2 className="text-xl font-black">System Settings</h2>
                        </div>
                        <button onClick={onClose} className={`p-2 rounded-full transition-colors ${isDark ? 'hover:bg-slate-800 text-slate-400' : 'hover:bg-gray-200 text-gray-500'}`}>
                            <X className="w-6 h-6" />
                        </button>
                    </div>

                    {/* Content */}
                    <div className="p-8 space-y-10">
                        {/* Language Section */}
                        <section>
                            <label className={`text-[10px] font-black uppercase tracking-[0.2em] mb-4 block ${isDark ? 'text-slate-500' : 'text-gray-400'}`}>
                                Language Preferences
                            </label>
                            <div className="grid grid-cols-2 gap-3">
                                {languages.map((lang) => (
                                    <button
                                        key={lang.code}
                                        onClick={() => setSettings({ ...settings, language: lang.code })}
                                        className={`flex items-center gap-3 p-4 rounded-2xl border-2 transition-all ${settings.language === lang.code
                                            ? (isDark ? 'border-blue-500 bg-blue-500/10 text-blue-400' : 'border-blue-600 bg-blue-50 text-blue-700 shadow-md')
                                            : (isDark ? 'border-slate-800 hover:border-slate-700 text-slate-400' : 'border-gray-100 hover:border-gray-200 text-gray-600')
                                            }`}
                                    >
                                        <span className="text-2xl drop-shadow-sm">{lang.icon}</span>
                                        <span className="font-bold text-sm tracking-tight">{lang.name}</span>
                                    </button>
                                ))}
                            </div>
                        </section>

                        {/* General Section */}
                        <section className="space-y-4">
                            <label className={`text-[10px] font-black uppercase tracking-[0.2em] mb-4 block ${isDark ? 'text-slate-500' : 'text-gray-400'}`}>
                                Visual & Signals
                            </label>

                            <div className={`flex items-center justify-between p-5 rounded-3xl transition-colors ${isDark ? 'bg-slate-800/50 border border-slate-800' : 'bg-gray-50 border border-transparent'}`}>
                                <div className="flex items-center gap-4">
                                    <div className={`p-2.5 rounded-xl shadow-sm ${isDark ? 'bg-slate-900 border border-slate-700' : 'bg-white'}`}>
                                        {isDark ? <Moon className="w-5 h-5 text-blue-400" /> : <Sun className="w-5 h-5 text-orange-400" />}
                                    </div>
                                    <div>
                                        <p className="font-black text-sm">Theme Mode</p>
                                        <p className="text-[10px] opacity-50 font-bold uppercase tracking-wider">{isDark ? 'Dark Optimized' : 'Light Standard'}</p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setSettings({ ...settings, darkMode: !settings.darkMode })}
                                    className={`w-14 h-7 rounded-full transition-all relative ${isDark ? 'bg-blue-600 shadow-lg shadow-blue-500/20' : 'bg-gray-300'}`}
                                >
                                    <motion.div
                                        animate={{ x: isDark ? 28 : 4 }}
                                        className="absolute top-1 w-5 h-5 bg-white rounded-full shadow-md"
                                    />
                                </button>
                            </div>

                            <div className={`flex items-center justify-between p-5 rounded-3xl transition-colors ${isDark ? 'bg-slate-800/50 border border-slate-800' : 'bg-gray-50 border border-transparent'}`}>
                                <div className="flex items-center gap-4">
                                    <div className={`p-2.5 rounded-xl shadow-sm ${isDark ? 'bg-slate-900 border border-slate-700' : 'bg-white'}`}>
                                        <Bell className={`w-5 h-5 ${settings.notifications ? (isDark ? 'text-blue-400' : 'text-blue-600') : 'text-gray-400'}`} />
                                    </div>
                                    <div>
                                        <p className="font-black text-sm">Real-time Pulse</p>
                                        <p className="text-[10px] opacity-50 font-bold uppercase tracking-wider">Push Notifications</p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setSettings({ ...settings, notifications: !settings.notifications })}
                                    className={`w-14 h-7 rounded-full transition-all relative ${settings.notifications ? (isDark ? 'bg-blue-600 shadow-lg shadow-blue-500/20' : 'bg-blue-600') : 'bg-gray-300'}`}
                                >
                                    <motion.div
                                        animate={{ x: settings.notifications ? 28 : 4 }}
                                        className="absolute top-1 w-5 h-5 bg-white rounded-full shadow-md"
                                    />
                                </button>
                            </div>
                        </section>
                    </div>

                    {/* Footer */}
                    <div className={`px-6 py-5 text-center transition-colors ${isDark ? 'bg-slate-950/50 border-t border-slate-800' : 'bg-gray-50 border-t border-gray-100'}`}>
                        <p className={`text-[10px] font-black tracking-widest uppercase opacity-40 ${isDark ? 'text-slate-400' : 'text-gray-500'}`}>
                            QuantCore Hub v4.2.0 • Advanced Trading Node
                        </p>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default SettingsModal;
