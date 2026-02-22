import { AnimatePresence, motion } from 'framer-motion';
import { Settings, X, Bell, Globe, Command } from 'lucide-react';
import { useTranslation } from '../utils/translations';

const SettingsModal = ({ isOpen, onClose, settings, setSettings }) => {
    const t = useTranslation(settings);

    // isOpen 조건을 AnimatePresence 외부에서 제어해야 exit 애니메이션이 정상 동작함
    // 내부에서 early return 시 backdrop만 남고 모달 내용이 사라지는 버그 방지

    const languages = [
        { code: 'ko', name: '한국어', icon: '🇰🇷' },
        { code: 'en', name: 'English', icon: '🇺🇸' },
        { code: 'zh', name: '中文', icon: '🇨🇳' },
        { code: 'ja', name: '日本語', icon: '🇯🇵' },
    ];

    return (
        <AnimatePresence mode="wait">
            {isOpen && <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4">
                {/* Backdrop */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                    className="absolute inset-0 bg-black/80 backdrop-blur-xl"
                />

                {/* Modal Container */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.9, y: 40 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9, y: 40 }}
                    className="relative w-full max-w-lg bg-[#09090b] border border-white/10 rounded-[3rem] shadow-[0_50px_100px_rgba(0,0,0,0.8)] overflow-hidden"
                >
                    {/* Header */}
                    <header className="px-10 py-8 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
                        <div className="flex items-center gap-4">
                            <div className="bg-yellow-400 p-3 rounded-2xl text-black shadow-lg shadow-yellow-400/20">
                                <Settings className="w-6 h-6" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-black tracking-tighter uppercase text-zinc-100">{t.settings || 'CONFIG_NODE'}</h2>
                                <p className="text-[10px] font-black text-zinc-600 uppercase tracking-widest font-mono">SYSTEM_PREFERENCES_v4.2</p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-3 rounded-2xl hover:bg-white/5 text-zinc-500 hover:text-white transition-all border border-transparent hover:border-white/10"
                        >
                            <X className="w-6 h-6" />
                        </button>
                    </header>

                    {/* Content */}
                    <div className="p-10 space-y-12">
                        {/* Language Section */}
                        <section className="space-y-6">
                            <div className="flex items-center gap-2 mb-2">
                                <Globe className="w-4 h-4 text-yellow-400/50" />
                                <label className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-500 font-mono">
                                    CORE_LOCALIZATION_PROTOCOL
                                </label>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                {languages.map((lang) => (
                                    <button
                                        key={lang.code}
                                        onClick={() => setSettings(prev => ({ ...prev, language: lang.code }))}
                                        className={`flex items-center gap-4 p-5 rounded-[2rem] border-2 transition-all duration-300 relative group ${settings.language === lang.code
                                            ? 'border-yellow-400 bg-yellow-400/5 text-yellow-400 shadow-lg shadow-yellow-400/5'
                                            : 'border-white/5 hover:border-white/10 bg-white/2 text-zinc-500 hover:text-zinc-300'
                                            }`}
                                    >
                                        <span className="text-2xl grayscale group-hover:grayscale-0 transition-all">{lang.icon}</span>
                                        <span className="font-black text-xs tracking-tighter uppercase">{lang.name}</span>
                                        {settings.language === lang.code && (
                                            <div className="absolute top-2 right-4 w-1.5 h-1.5 bg-yellow-400 rounded-full shadow-[0_0_8px_rgba(250,204,21,0.8)]" />
                                        )}
                                    </button>
                                ))}
                            </div>
                        </section>

                        {/* General Section */}
                        <section className="space-y-6">
                            <div className="flex items-center gap-2 mb-2">
                                <Command className="w-4 h-4 text-yellow-400/50" />
                                <label className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-500 font-mono">
                                    SIGNAL_TRANSMISSION_CONTROLS
                                </label>
                            </div>

                            <div className="flex items-center justify-between p-6 rounded-[2.5rem] bg-white/2 border border-white/5 hover:bg-white/5 transition-all group">
                                <div className="flex items-center gap-5">
                                    <div className="p-3.5 rounded-2xl bg-zinc-900 border border-white/10 shadow-inner group-hover:border-yellow-400/30 transition-colors">
                                        <Bell className={`w-6 h-6 ${settings.notifications ? 'text-yellow-400' : 'text-zinc-700'}`} />
                                    </div>
                                    <div>
                                        <p className="font-black text-sm text-zinc-100 uppercase tracking-tight">{t.set_realtime_pulse || 'NEURAL_PUSH_SIGNALS'}</p>
                                        <p className="text-[9px] opacity-40 font-black uppercase tracking-[0.2em] font-mono mt-1">Real-time market event broadcasting</p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setSettings(prev => ({ ...prev, notifications: !prev.notifications }))}
                                    className={`w-16 h-8 rounded-full transition-all relative border ${settings.notifications ? 'bg-yellow-400 border-yellow-300 shadow-lg shadow-yellow-400/30' : 'bg-zinc-800 border-zinc-700'}`}
                                >
                                    <motion.div
                                        animate={{ x: settings.notifications ? 32 : 4 }}
                                        transition={{ type: "spring", stiffness: 500, damping: 30 }}
                                        className={`absolute top-1 w-5.5 h-5.5 rounded-full shadow-md ${settings.notifications ? 'bg-black' : 'bg-zinc-500'}`}
                                    />
                                </button>
                            </div>
                        </section>
                    </div>

                    {/* Footer */}
                    <footer className="px-10 py-6 text-center border-t border-white/5 bg-white/[0.02]">
                        <p className="text-[9px] font-black tracking-[0.5em] uppercase text-zinc-700 font-mono">
                            QUANT_ORACLE_INTERFACE // STITCH_PROTOCOL_ENABLED
                        </p>
                    </footer>
                </motion.div>
            </div>}
        </AnimatePresence>
    );
};

export default SettingsModal;
