import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import SettingsModal from './components/SettingsModal';

// Pages
import AnalysisPage from './pages/AnalysisPage';
import ChatPage from './pages/ChatPage';
import CalendarPage from './pages/CalendarPage';
import PortfolioPage from './pages/PortfolioPage';
import ScreenerPage from './pages/ScreenerPage';

function App() {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [settings, setSettings] = useState(() => {
    try {
      const saved = localStorage.getItem('trading_asist_settings');
      if (saved && saved !== 'undefined') {
        const parsed = JSON.parse(saved);
        return {
          language: parsed.language || 'ko',
          darkMode: parsed.darkMode || false,
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
      darkMode: false,
      notifications: true,
      priceAlerts: true,
      chartInterval: '1D'
    };
  });

  // 설정 변경 시 로컬 스토리지 저장 및 body 클래스 토글
  useEffect(() => {
    localStorage.setItem('trading_asist_settings', JSON.stringify(settings));
    if (settings.darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [settings]);

  return (
    <Router>
      <div className={`min-h-screen transition-colors duration-300 ${settings?.darkMode ? 'bg-slate-950 text-slate-100' : 'bg-gray-50 text-gray-900'}`}>
        <Navigation settings={settings} onOpenSettings={() => setIsSettingsOpen(true)} />

        <SettingsModal
          isOpen={isSettingsOpen}
          onClose={() => setIsSettingsOpen(false)}
          settings={settings}
          setSettings={setSettings}
        />

        <Routes>
          <Route path="/" element={<AnalysisPage settings={settings} />} />
          <Route path="/chat" element={<ChatPage settings={settings} />} />
          <Route path="/calendar" element={<CalendarPage settings={settings} />} />
          <Route path="/portfolio" element={<PortfolioPage settings={settings} />} />
          <Route path="/screener" element={<ScreenerPage settings={settings} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
