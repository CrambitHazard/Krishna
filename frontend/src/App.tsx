import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { DesktopNav, MobileNav } from './components/Navbars';
import UploadPage from './pages/UploadPage';
import ChatPage from './pages/ChatPage';
import QuizPage from './pages/QuizPage';
import AnalyticsPage from './pages/AnalyticsPage';
import './App.css';

const App: React.FC = () => {
  return (
    <Router>
      <div className="noise-overlay" />
      <div className="bg-aura" />
      <div className="bg-aura-2" />
      <div className="app-container">
        <DesktopNav />
        <MobileNav />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/upload" replace />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/quiz" element={<QuizPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
