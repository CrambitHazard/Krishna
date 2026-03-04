import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { DesktopNav, MobileNav } from './components/Navbars';
import UploadPage from './pages/UploadPage';
import ChatPage from './pages/ChatPage';
import QuizPage from './pages/QuizPage';
import AnalyticsPage from './pages/AnalyticsPage';
import AppPage from './pages/AppPage';
import './App.css';

const AppContent: React.FC = () => {
  const location = useLocation();
  const isAppRoute = location.pathname.startsWith('/app');

  return (
    <>
      {!isAppRoute && <DesktopNav />}
      {!isAppRoute && <MobileNav />}
      <main className={isAppRoute ? "app-fullscreen-wrapper" : "main-content"}>
        <Routes>
          <Route path="/" element={<Navigate to="/upload" replace />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/quiz" element={<QuizPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/app" element={<AppPage />} />
        </Routes>
      </main>
    </>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <div className="noise-overlay" />
      <div className="bg-aura" />
      <div className="bg-aura-2" />
      <div className="app-container">
        <AppContent />
      </div>
    </Router>
  );
};

export default App;
