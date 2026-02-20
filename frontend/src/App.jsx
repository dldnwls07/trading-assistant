import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import Navigation from './components/Navigation';
import SettingsModal from './components/SettingsModal';

// Pages
import AnalysisPage from './pages/AnalysisPage';
import ChatPage from './pages/ChatPage';
import CalendarPage from './pages/CalendarPage';
import EarningsPage from './pages/EarningsPage';
import PortfolioPage from './pages/PortfolioPage';
import WalletPage from './pages/WalletPage';
import ScreenerPage from './pages/ScreenerPage';

const pageTransition = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.3 } },
  exit: { opacity: 0, y: -10, transition: { duration: 0.2 } }
};

const AnimatedRoutes = ({ settings }) => {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        {['/', '/analysis', '/analysis/:tickerParam'].map(path => (
          <Route key={path} path={path} element={
            <motion.div initial="initial" animate="animate" exit="exit" variants={pageTransition}>
              <AnalysisPage settings={settings} />
            </motion.div>
          } />
        ))}
        {['chat', 'calendar', 'earnings', 'portfolio', 'wallet', 'screener'].map(page => {
          const components = {
            chat: ChatPage,
            calendar: CalendarPage,
            earnings: EarningsPage,
            portfolio: PortfolioPage,
            wallet: WalletPage,
            screener: ScreenerPage
          };
          const Component = components[page];
          return (
            <Route key={page} path={`/${page}`} element={
              <motion.div initial="initial" animate="animate" exit="exit" variants={pageTransition}>
                <Component settings={settings} />
              </motion.div>
            } />
          );
        })}
      </Routes>
    </AnimatePresence>
  );
};

function App() {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [settings, setSettings] = useState(() => {
    try {
      const saved = localStorage.getItem('trading_asist_settings');
      if (saved && saved !== 'undefined') {
        const parsed = JSON.parse(saved);
        return {
          language: parsed.language || 'ko',
          darkMode: parsed.darkMode ?? true, // Default to true for Stitch theme
          notifications: parsed.notifications ?? true,
          priceAlerts: parsed.priceAlerts ?? true,
          chartInterval: parsed.chartInterval || '1D'
        };
      }
    } catch (e) {
      console.error("Settings load error:", e);
    }
    return {
      language: 'ko',
      darkMode: true,
      notifications: true,
      priceAlerts: true,
      chartInterval: '1D'
    };
  });

  // 설정 변경 시 로컬 스토리지 저장 및 body 클래스 고정
  useEffect(() => {
    localStorage.setItem('trading_asist_settings', JSON.stringify(settings));
    // Always dark theme
    document.documentElement.classList.add('dark');
  }, [settings]);

  return (
    <Router>
      <div className="min-h-screen overflow-x-hidden bg-[#09090b] text-foreground transition-colors duration-300 relative">
        <div className="bg-noise" />
        <Navigation settings={settings} onOpenSettings={() => setIsSettingsOpen(true)} />

        <SettingsModal
          isOpen={isSettingsOpen}
          onClose={() => setIsSettingsOpen(false)}
          settings={settings}
          setSettings={setSettings}
        />

        <main className="relative z-10 pt-2 pb-16">
          <AnimatedRoutes settings={settings} />
        </main>
      </div>
    </Router>
  );
}

export default App;
