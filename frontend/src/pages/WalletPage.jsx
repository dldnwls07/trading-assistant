import React from 'react';
import { Wallet, ShieldAlert, Cpu, Activity, RefreshCcw, DollarSign, TrendingUp, BarChart2, Lock } from 'lucide-react';
import { useTranslation } from '../utils/translations';

const WalletPage = ({ settings }) => {
    const t = useTranslation(settings);

    // 이 페이지는 KIS API 연동이 필요하므로 현재는 안내 메시지를 표시합니다.

    return (
        <div className="min-h-screen py-10 bg-background text-foreground transition-colors duration-300">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
                <div className="flex items-center justify-between">
                    <h1 className="text-3xl font-black flex items-center gap-3">
                        <div className="bg-emerald-500 p-2 rounded-xl text-white shadow-lg shadow-emerald-500/20">
                            <Wallet className="w-7 h-7" />
                        </div>
                        {t.nav_wallet || 'Real Wallet'}
                    </h1>

                    <div className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 text-emerald-500 rounded-2xl border border-emerald-500/20">
                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                        <span className="text-xs font-black uppercase tracking-widest">KIS Live Sync</span>
                    </div>
                </div>

                {/* API Key Required State */}
                <div className="relative group overflow-hidden p-12 rounded-[2.5rem] border bg-card border-border shadow-2xl text-center space-y-6">
                    <div className="absolute top-0 right-0 p-8 opacity-5 transition-transform group-hover:scale-110">
                        <Lock className="w-64 h-64" />
                    </div>

                    <div className="bg-emerald-500/10 w-24 h-24 rounded-3xl flex items-center justify-center mx-auto mb-8 border border-emerald-500/20">
                        <Lock className="w-10 h-10 text-emerald-500" />
                    </div>

                    <h2 className="text-4xl font-black tracking-tight italic">
                        KIS API <span className="text-emerald-500">Connection</span> Required
                    </h2>

                    <p className="max-w-xl mx-auto text-lg text-muted-foreground font-medium leading-relaxed">
                        실전 계좌 데이터 동기화를 위해 **한국투자증권(KIS) API 키** 설정이 필요합니다.<br />
                        현재는 가상 계좌(Portfolio) 모드로 작동 중이며, API 키 등록 후 실제 자산 현황을 실시간으로 확인할 수 있습니다.
                    </p>

                    <div className="flex flex-wrap justify-center gap-4 pt-8">
                        <div className="flex items-center gap-2 px-6 py-3 bg-muted rounded-2xl border border-border">
                            <Activity className="w-5 h-5 text-emerald-500" />
                            <span className="font-bold">실시간 잔고 조회</span>
                        </div>
                        <div className="flex items-center gap-2 px-6 py-3 bg-muted rounded-2xl border border-border">
                            <TrendingUp className="w-5 h-5 text-emerald-500" />
                            <span className="font-bold">실전 실익률 분석</span>
                        </div>
                        <div className="flex items-center gap-2 px-6 py-3 bg-muted rounded-2xl border border-border">
                            <Cpu className="w-5 h-5 text-emerald-500" />
                            <span className="font-bold">AI 자율 매매 연동</span>
                        </div>
                    </div>

                    <div className="pt-10">
                        <button
                            onClick={() => alert('설정 메뉴에서 API 키를 입력해주세요.')}
                            className="px-10 py-4 bg-emerald-500 text-white rounded-[1.5rem] font-black text-lg shadow-xl shadow-emerald-500/20 hover:bg-emerald-600 hover:scale-105 transition-all"
                        >
                            Configure API Keys
                        </button>
                    </div>
                </div>

                {/* Placeholder Stats (Blurred) */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 opacity-30 grayscale blur-[2px] select-none pointer-events-none">
                    <div className="p-8 rounded-[2rem] border bg-card border-border">
                        <p className="text-xs font-black uppercase tracking-widest opacity-50 mb-4">Total Balance</p>
                        <p className="text-3xl font-black tracking-tighter">₩125,480,000</p>
                    </div>
                    <div className="p-8 rounded-[2rem] border bg-card border-border">
                        <p className="text-xs font-black uppercase tracking-widest opacity-50 mb-4">Daily Profit</p>
                        <p className="text-3xl font-black tracking-tighter text-emerald-500">+₩2,450,000</p>
                    </div>
                    <div className="p-8 rounded-[2rem] border bg-card border-border">
                        <p className="text-xs font-black uppercase tracking-widest opacity-50 mb-4">Total P/L</p>
                        <p className="text-3xl font-black tracking-tighter text-emerald-500">+12.4%</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default WalletPage;
