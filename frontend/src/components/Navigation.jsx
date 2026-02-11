import { Link, useLocation } from 'react-router-dom';
import {
    BarChart2,
    MessageSquare,
    Calendar,
    PieChart,
    Search,
    TrendingUp,
    Settings,
    Bell,
    Menu,
    X
} from 'lucide-react';
import { useState } from 'react';
import { useTranslation } from '../utils/translations';

const Navigation = ({ settings, onOpenSettings }) => {
    const location = useLocation();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const t = useTranslation(settings);

    const navItems = [
        { path: '/', label: t.analysis, icon: BarChart2 },
        { path: '/chat', label: t.chat, icon: MessageSquare },
        { path: '/calendar', label: t.calendar, icon: Calendar },
        { path: '/portfolio', label: t.portfolio, icon: PieChart },
        { path: '/screener', label: t.screener, icon: TrendingUp },
    ];

    const isDark = settings?.darkMode;

    return (
        <nav className={`border-b transition-colors duration-300 sticky top-0 z-50 ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-200'}`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">

                    {/* Logo & Desktop Nav */}
                    <div className="flex">
                        <div className="flex-shrink-0 flex items-center">
                            <Link to="/" className="flex items-center gap-2">
                                <div className="bg-blue-600 text-white p-1.5 rounded font-bold text-xl tracking-tighter shadow-lg shadow-blue-500/20">
                                    QC
                                </div>
                                <span className={`font-bold text-lg hidden sm:block ${isDark ? 'text-white' : 'text-gray-900'}`}>
                                    QuantCore<span className="text-blue-500">.Pro</span>
                                </span>
                            </Link>
                        </div>

                        <div className="hidden md:ml-8 md:flex md:space-x-1 h-full items-center">
                            {navItems.map((item) => {
                                const isActive = location.pathname === item.path;
                                const Icon = item.icon;
                                return (
                                    <Link
                                        key={item.path}
                                        to={item.path}
                                        className={`inline-flex items-center px-4 py-2 border-b-2 text-sm font-medium transition-all ${isActive
                                            ? 'border-blue-500 text-blue-500'
                                            : `border-transparent ${isDark ? 'text-slate-400 hover:text-slate-200 hover:border-slate-700' : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'}`
                                            }`}
                                    >
                                        <Icon className="w-4 h-4 mr-2" />
                                        {item.label}
                                    </Link>
                                );
                            })}
                        </div>
                    </div>

                    {/* Right Side Icons */}
                    <div className="flex items-center space-x-3">
                        <button
                            onClick={() => window.location.href = '/'}
                            className={`p-2 rounded-full transition-colors ${isDark ? 'text-slate-400 hover:bg-slate-800 hover:text-white' : 'text-gray-400 hover:bg-gray-100 hover:text-gray-600'}`}
                            title="검색"
                        >
                            <Search className="h-5 w-5" />
                        </button>

                        <button
                            onClick={onOpenSettings}
                            className={`p-2 rounded-full transition-colors ${isDark ? 'text-slate-400 hover:bg-slate-800 hover:text-white' : 'text-gray-400 hover:bg-gray-100 hover:text-gray-600'}`}
                            title="설정"
                        >
                            <Settings className="h-5 w-5" />
                        </button>

                        <button
                            onClick={() => alert('알림 기능은 곧 출시됩니다!')}
                            className={`p-2 rounded-full transition-colors relative ${isDark ? 'text-slate-400 hover:bg-slate-800 hover:text-white' : 'text-gray-400 hover:bg-gray-100 hover:text-gray-600'}`}
                            title="알림"
                        >
                            <Bell className="h-5 w-5" />
                            <span className="absolute top-2 right-2 block h-2 w-2 rounded-full ring-2 ring-transparent bg-red-500 shadow-sm shadow-red-500/50"></span>
                        </button>

                        <div
                            onClick={() => alert('사용자 메뉴는 곧 출시됩니다!')}
                            className={`h-8 w-8 rounded-full flex items-center justify-center font-bold text-sm cursor-pointer border shadow-sm ${isDark ? 'bg-slate-800 border-slate-700 text-blue-400' : 'bg-blue-50 border-blue-100 text-blue-600'}`}
                            title="사용자 메뉴"
                        >
                            JD
                        </div>

                        {/* Mobile menu button */}
                        <div className="flex items-center md:hidden">
                            <button
                                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                                className={`p-2 rounded-lg ${isDark ? 'text-slate-400 hover:text-white hover:bg-slate-800' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'}`}
                            >
                                {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            {mobileMenuOpen && (
                <div className={`md:hidden border-t absolute w-full shadow-2xl transition-colors ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-gray-100'}`}>
                    <div className="pt-2 pb-3 space-y-1 px-2">
                        {navItems.map((item) => {
                            const isActive = location.pathname === item.path;
                            const Icon = item.icon;
                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={`flex items-center px-3 py-3 text-base font-medium rounded-xl transition-all ${isActive
                                        ? (isDark ? 'bg-blue-500/10 text-blue-400' : 'bg-blue-50 text-blue-600')
                                        : (isDark ? 'text-slate-400 hover:bg-slate-800 hover:text-slate-200' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900')
                                        }`}
                                >
                                    <Icon className="w-5 h-5 mr-3" />
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
