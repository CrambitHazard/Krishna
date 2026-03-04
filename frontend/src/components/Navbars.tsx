import React from 'react';
// NavLink and React Router is no longer needed here since we use anchor tags
import { UploadCloud, MessageSquare, Target, Activity } from 'lucide-react';
import './Navbars.css';

export const DesktopNav: React.FC = () => {
    return (
        <div className="desktop-only nav-desktop-wrapper">
            <nav className="nav-desktop">
                <div className="nav-brand">KRISHNA</div>
                <div className="nav-links">
                    <a href="/home#upload" className="nav-link">
                        <span>01</span> Upload
                    </a>
                    <a href="/home#chat" className="nav-link">
                        <span>02</span> Chat
                    </a>
                    <a href="/home#quiz" className="nav-link">
                        <span>03</span> Quiz
                    </a>
                </div>
                <a href="/home#analytics" className="nav-btn">
                    <div className="btn-circle"></div>
                    <span className="btn-text">Progress</span>
                </a>
            </nav>
        </div>
    );
};

export const MobileNav: React.FC = () => {
    return (
        <div className="mobile-only nav-mobile-bottom">
            <a href="/home#upload" className="mob-tab">
                <UploadCloud size={24} strokeWidth={1.5} />
            </a>
            <a href="/home#chat" className="mob-tab">
                <MessageSquare size={24} strokeWidth={1.5} />
            </a>
            <a href="/home#quiz" className="mob-tab">
                <Target size={24} strokeWidth={1.5} />
            </a>
            <a href="/home#analytics" className="mob-tab active-mob-portal">
                <Activity size={24} strokeWidth={2.5} color={'var(--accent-color)'} />
            </a>
        </div>
    );
};
