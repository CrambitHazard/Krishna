import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { DesktopNav, MobileNav } from './components/Navbars';
import LandingPage from './pages/LandingPage';
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
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route path="/home" element={<LandingPage />} />

          {/* Catch all old routes and redirect them to standard home scrolling sections or app */}
          <Route path="/upload" element={<Navigate to="/home" replace />} />
          <Route path="/chat" element={<Navigate to="/home" replace />} />
          <Route path="/quiz" element={<Navigate to="/home" replace />} />
          <Route path="/analytics" element={<Navigate to="/home" replace />} />

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
