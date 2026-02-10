import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';

// Pages
import AnalysisPage from './pages/AnalysisPage';
import ChatPage from './pages/ChatPage';
import CalendarPage from './pages/CalendarPage';
import PortfolioPage from './pages/PortfolioPage';
import ScreenerPage from './pages/ScreenerPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
        <Navigation />
        <Routes>
          <Route path="/" element={<AnalysisPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/calendar" element={<CalendarPage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
          <Route path="/screener" element={<ScreenerPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
