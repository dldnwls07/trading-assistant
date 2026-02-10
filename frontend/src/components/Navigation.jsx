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

const Navigation = () => {
    const location = useLocation();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const navItems = [
        { path: '/', label: 'Markets', icon: BarChart2 },
        { path: '/chat', label: 'AI Analysis', icon: MessageSquare },
        { path: '/calendar', label: 'Calendar', icon: Calendar },
        { path: '/portfolio', label: 'Portfolio', icon: PieChart },
        { path: '/screener', label: 'Screener', icon: TrendingUp },
    ];

    return (
        <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">

                    {/* Logo & Desktop Nav */}
                    <div className="flex">
                        <div className="flex-shrink-0 flex items-center">
                            <Link to="/" className="flex items-center gap-2">
                                <div className="bg-blue-600 text-white p-1.5 rounded font-bold text-xl tracking-tighter">
                                    QC
                                </div>
                                <span className="font-bold text-gray-900 text-lg hidden sm:block">
                                    QuantCore<span className="text-blue-600">.Pro</span>
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
                                        className={`inline-flex items-center px-4 py-2 border-b-2 text-sm font-medium transition-colors ${isActive
                                                ? 'border-blue-600 text-blue-600'
                                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
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
                    <div className="flex items-center space-x-4">
                        <button className="text-gray-400 hover:text-gray-600 p-1">
                            <Search className="h-5 w-5" />
                        </button>
                        <button className="text-gray-400 hover:text-gray-600 p-1 relative">
                            <Bell className="h-5 w-5" />
                            <span className="absolute top-0 right-0 block h-2 w-2 rounded-full ring-2 ring-white bg-red-500"></span>
                        </button>
                        <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-sm cursor-pointer">
                            JD
                        </div>

                        {/* Mobile menu button */}
                        <div className="flex items-center md:hidden">
                            <button
                                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                                className="text-gray-400 hover:text-gray-600 p-2"
                            >
                                {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            {mobileMenuOpen && (
                <div className="md:hidden border-t border-gray-100 bg-white absolute w-full shadow-lg">
                    <div className="pt-2 pb-3 space-y-1 px-2">
                        {navItems.map((item) => {
                            const isActive = location.pathname === item.path;
                            const Icon = item.icon;
                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={`flex items-center px-3 py-3 text-base font-medium rounded-md ${isActive
                                            ? 'bg-blue-50 text-blue-600'
                                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
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
