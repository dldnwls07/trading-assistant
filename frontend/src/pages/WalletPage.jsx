import { motion } from 'framer-motion';
import {
    Wallet,
    Lock,
    Activity,
    TrendingUp,
    Cpu
} from 'lucide-react';
import { useTranslation } from '../utils/translations';

const WalletPage = ({ settings }) => {
    const t = useTranslation(settings);

    // 이 페이지는 KIS API 연동이 필요하므로 현재는 안내 메시지를 표시합니다.

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: { opacity: 1, transition: { staggerChildren: 0.1, delayChildren: 0.1 } }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 30, scale: 0.98 },
        visible: { opacity: 1, y: 0, scale: 1, transition: { type: 'spring', stiffness: 300, damping: 24 } }
    };

    return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="min-h-screen py-10 bg-[#09090b] text-foreground transition-all duration-300">
            <motion.div initial="hidden" animate="visible" variants={containerVariants} className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
                <motion.div variants={itemVariants} className="flex items-center justify-between">
                    <h1 className="text-3xl font-black tracking-tighter flex items-center gap-3 text-zinc-100 uppercase">
                        <div className="bg-yellow-400 text-black p-2 rounded-xl shadow-lg shadow-yellow-400/20">
                            <Wallet className="w-7 h-7" />
                        </div>
                        {t.nav_wallet || 'Real Wallet'}
                    </h1>

                    <div className="flex items-center gap-2 px-4 py-2 bg-yellow-400/10 text-yellow-400 rounded-2xl border border-yellow-400/20">
                        <div className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse"></div>
                        <span className="text-xs font-black uppercase tracking-widest font-mono">KIS_LIVE_SYNC</span>
                    </div>
                </motion.div>

                {/* API Key Required State */}
                <motion.div variants={itemVariants} className="relative group overflow-hidden p-12 rounded-[2.5rem] border bg-white/5 backdrop-blur-md border-white/10 shadow-2xl hover:shadow-yellow-400/5 transition-all text-center space-y-6">
                    <div className="absolute top-0 right-0 p-8 opacity-5 transition-transform group-hover:scale-110">
                        <Lock className="w-64 h-64 text-zinc-100" />
                    </div>

                    <div className="bg-yellow-400/10 w-24 h-24 rounded-3xl flex items-center justify-center mx-auto mb-8 border border-yellow-400/20">
                        <Lock className="w-10 h-10 text-yellow-400" />
                    </div>

                    <h2 className="text-4xl font-black tracking-tighter italic text-zinc-100 uppercase">
                        KIS API <span className="text-yellow-400">Connection</span> Required
                    </h2>

                    <p className="max-w-xl mx-auto text-base text-zinc-400 font-medium leading-relaxed">
                        실전 계좌 데이터 동기화를 위해 <span className="text-zinc-100 font-bold">한국투자증권(KIS) API 키</span> 설정이 필요합니다.<br />
                        현재는 가상 계좌(Portfolio) 모드로 작동 중이며, API 키 등록 후 실제 자산 현황을 실시간으로 확인할 수 있습니다.
                    </p>

                    <div className="flex flex-wrap justify-center gap-4 pt-8">
                        <div className="flex items-center gap-2 px-6 py-3 bg-white/5 rounded-2xl border border-white/10">
                            <Activity className="w-5 h-5 text-yellow-400" />
                            <span className="font-bold text-zinc-300 text-xs uppercase tracking-widest font-mono">실시간 잔고 조회</span>
                        </div>
                        <div className="flex items-center gap-2 px-6 py-3 bg-white/5 rounded-2xl border border-white/10">
                            <TrendingUp className="w-5 h-5 text-yellow-400" />
                            <span className="font-bold text-zinc-300 text-xs uppercase tracking-widest font-mono">실전 수익률 분석</span>
                        </div>
                        <div className="flex items-center gap-2 px-6 py-3 bg-white/5 rounded-2xl border border-white/10">
                            <Cpu className="w-5 h-5 text-yellow-400" />
                            <span className="font-bold text-zinc-300 text-xs uppercase tracking-widest font-mono">AI 자율 매매 연동</span>
                        </div>
                    </div>

                    <div className="pt-10">
                        <button
                            onClick={() => alert('설정 메뉴에서 API 키를 입력해주세요.')}
                            className="px-10 py-4 bg-yellow-400 text-black rounded-[1.5rem] font-black text-lg shadow-xl shadow-yellow-400/20 hover:bg-yellow-400/90 hover:scale-105 transition-all uppercase tracking-tighter"
                        >
                            Configure API Keys
                        </button>
                    </div>
                </motion.div>

                {/* Placeholder Stats (Blurred) */}
                <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-3 gap-6 opacity-30 grayscale blur-[2px] select-none pointer-events-none">
                    <div className="p-8 rounded-[2rem] border bg-white/5 border-white/10">
                        <p className="text-xs font-black uppercase tracking-widest opacity-50 mb-4 text-zinc-500 font-mono">Total Balance</p>
                        <p className="text-3xl font-black tracking-tighter text-zinc-100 font-mono">₩125,480,000</p>
                    </div>
                    <div className="p-8 rounded-[2rem] border bg-white/5 border-white/10">
                        <p className="text-xs font-black uppercase tracking-widest opacity-50 mb-4 text-zinc-500 font-mono">Daily Profit</p>
                        <p className="text-3xl font-black tracking-tighter text-yellow-400 font-mono">+₩2,450,000</p>
                    </div>
                    <div className="p-8 rounded-[2rem] border bg-white/5 border-white/10">
                        <p className="text-xs font-black uppercase tracking-widest opacity-50 mb-4 text-zinc-500 font-mono">Total P/L</p>
                        <p className="text-3xl font-black tracking-tighter text-yellow-400 font-mono">+12.4%</p>
                    </div>
                </motion.div>
            </motion.div>
        </motion.div>
    );
};

export default WalletPage;
