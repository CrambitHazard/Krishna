import React, { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import UploadPage from './UploadPage';
import ChatPage from './ChatPage';
import QuizPage from './QuizPage';
import AnalyticsPage from './AnalyticsPage';

const LandingPage: React.FC = () => {
    const location = useLocation();

    // Scroll to the hash section if present in the URL
    useEffect(() => {
        if (location.hash) {
            const element = document.getElementById(location.hash.substring(1));
            if (element) {
                element.scrollIntoView({ behavior: 'smooth' });
            }
        } else {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }, [location]);

    return (
        <div style={{ scrollBehavior: 'smooth' }}>
            <section id="upload">
                <UploadPage />
            </section>

            <section id="chat">
                <ChatPage />
            </section>

            <section id="quiz">
                <QuizPage />
            </section>

            <section id="analytics">
                <AnalyticsPage />
            </section>
        </div>
    );
};

export default LandingPage;
