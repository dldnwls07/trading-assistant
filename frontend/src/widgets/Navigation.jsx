import { useLocation, Link } from 'react-router-dom';
import { BarChart2, Calendar, PieChart, Search, TrendingUp, Wallet, X, Menu, Settings, Bell, Trophy } from 'lucide-react';
import { useState } from 'react';
import { useTranslation } from '../utils/translations';

const Navigation = ({ settings, onOpenSettings }) => {
    const location = useLocation();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const t = useTranslation(settings);

    const navItems = [
        { path: '/', label: t.nav_analysis, icon: BarChart2 },
        // { path: '/chat', label: t.nav_chat, icon: MessageSquare },
        { path: '/calendar', label: t.nav_calendar, icon: Calendar },
        { path: '/earnings', label: t.nav_earnings, icon: TrendingUp },
        { path: '/portfolio', label: t.nav_portfolio, icon: PieChart },
        { path: '/leaderboard', label: "AI 리그", icon: Trophy },
        { path: '/wallet', label: t.nav_wallet, icon: Wallet },
        { path: '/screener', label: t.nav_screener, icon: Search },
    ];

    const isDark = settings?.darkMode;

    return (
        <nav className="border-b transition-colors duration-300 sticky top-0 z-50 bg-[#09090b]/80 backdrop-blur-md border-white/10">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">

                    {/* Logo & Desktop Nav */}
                    <div className="flex">
                        <div className="flex-shrink-0 flex items-center">
                            <Link to="/" className="flex items-center gap-2 group cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-yellow-400 rounded-lg px-2 py-1">
                                <div className="bg-yellow-400 text-black p-2 rounded-lg font-bold text-xl tracking-tighter shadow-lg shadow-yellow-400/20 transition-transform group-hover:scale-105">
                                    AI
                                </div>
                                <span className="font-bold text-lg hidden sm:block text-zinc-100">
                                    TRADING <span className="text-yellow-400">ASSISTANT</span>
                                </span>
                            </Link>
                        </div>

                        <div className="hidden md:ml-4 md:flex md:space-x-0.5 h-full items-center">
                            {navItems.map((item) => {
                                const isActive = location.pathname === item.path;
                                const Icon = item.icon;
                                return (
                                    <Link
                                        key={item.path}
                                        to={item.path}
                                        className={`inline-flex items-center px-3 py-2 border-b-2 text-xs font-black transition-all cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-yellow-400 rounded-t-xl h-full whitespace-nowrap ${isActive
                                            ? 'border-yellow-400 text-yellow-400 bg-yellow-400/5 shadow-[inset_0_-10px_20px_-10px_rgba(250,204,21,0.2)]'
                                            : 'border-transparent text-zinc-500 hover:text-zinc-100 hover:bg-white/5'
                                            }`}
                                    >
                                        <Icon className={`w-3.5 h-3.5 mr-1.5 shrink-0 ${isActive ? 'text-yellow-400' : 'text-zinc-500'}`} />
                                        {item.label}
                                    </Link>
                                );
                            })}
                        </div>
                    </div>

                    {/* Right Side Icons */}
                    <div className="flex items-center space-x-4">
                        <button
                            onClick={() => window.location.href = '/'}
                            className="p-2 rounded-full transition-colors text-zinc-500 hover:bg-white/5 hover:text-zinc-100 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-yellow-400"
                            title="검색"
                            aria-label="검색"
                        >
                            <Search className="h-5 w-5" />
                        </button>

                        <button
                            onClick={onOpenSettings}
                            className="p-2 rounded-full transition-colors text-zinc-500 hover:bg-white/5 hover:text-zinc-100 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-yellow-400"
                            title="설정"
                            aria-label="설정"
                        >
                            <Settings className="h-5 w-5" />
                        </button>

                        <button
                            onClick={() => alert('알림 기능은 곧 출시됩니다!')}
                            className="p-2 rounded-full transition-colors relative text-zinc-500 hover:bg-white/5 hover:text-zinc-100 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-yellow-400"
                            title="알림"
                            aria-label="알림"
                        >
                            <Bell className="h-5 w-5" />
                            <span className="absolute top-2 right-2 block h-2 w-2 rounded-full ring-2 ring-[#09090b] bg-yellow-400 shadow-sm shadow-yellow-400/50"></span>
                        </button>

                        <button
                            onClick={() => alert('사용자 메뉴는 곧 출시됩니다!')}
                            className="h-8 w-8 rounded-full flex items-center justify-center font-bold text-sm cursor-pointer border shadow-sm bg-white/5 border-white/10 text-zinc-100 hover:bg-yellow-400/10 hover:text-yellow-400 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-yellow-400"
                            title="사용자 프로필"
                            aria-label="사용자 프로필"
                        >
                            JD
                        </button>

                        {/* Mobile menu button */}
                        <div className="flex items-center md:hidden">
                            <button
                                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                                className="p-2 rounded-lg text-zinc-500 hover:text-zinc-100 hover:bg-white/5 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-yellow-400"
                                aria-label="메뉴 토글"
                            >
                                {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            {mobileMenuOpen && (
                <div className="md:hidden border-t absolute w-full shadow-2xl transition-colors bg-background border-border">
                    <div className="pt-2 pb-3 space-y-1 px-2">
                        {navItems.map((item) => {
                            const isActive = location.pathname === item.path;
                            const Icon = item.icon;
                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={`flex items-center px-4 py-4 text-base font-bold rounded-xl transition-all cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-yellow-400 ${isActive
                                        ? 'bg-yellow-400/10 text-yellow-400'
                                        : 'text-zinc-500 hover:bg-white/5 hover:text-zinc-100'
                                        }`}
                                >
                                    <Icon className="w-5 h-5 mr-4" />
                                    {item.label}
                                </Link>
                            );
                        })}
                    </div>
                </div>
            )}
        </nav>
    );
};

export default Navigation;
