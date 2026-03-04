import React from 'react';
import { NavLink } from 'react-router-dom';
import { UploadCloud, MessageSquare, Target, Activity } from 'lucide-react';
import './Navbars.css';

export const DesktopNav: React.FC = () => {
    return (
        <div className="desktop-only nav-desktop-wrapper">
            <nav className="nav-desktop">
                <div className="nav-brand">KRISHNA</div>
                <div className="nav-links">
                    <NavLink to="/upload" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                        <span>01</span> Upload
                    </NavLink>
                    <NavLink to="/chat" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                        <span>02</span> Chat
                    </NavLink>
                    <NavLink to="/quiz" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                        <span>03</span> Quiz
                    </NavLink>
                </div>
                <NavLink to="/analytics" className={({ isActive }) => `nav-btn ${isActive ? 'active-btn' : ''}`}>
                    <div className="btn-circle"></div>
                    <span className="btn-text">Progress</span>
                </NavLink>
            </nav>
        </div>
    );
};

export const MobileNav: React.FC = () => {
    return (
        <div className="mobile-only nav-mobile-bottom">
            <NavLink to="/upload" className={({ isActive }) => `mob-tab ${isActive ? 'active-tab' : ''}`}>
                {({ isActive }) => <UploadCloud size={24} strokeWidth={isActive ? 2.5 : 1.5} />}
            </NavLink>
            <NavLink to="/chat" className={({ isActive }) => `mob-tab ${isActive ? 'active-tab' : ''}`}>
                {({ isActive }) => <MessageSquare size={24} strokeWidth={isActive ? 2.5 : 1.5} />}
            </NavLink>
            <NavLink to="/quiz" className={({ isActive }) => `mob-tab ${isActive ? 'active-tab' : ''}`}>
                {({ isActive }) => <Target size={24} strokeWidth={isActive ? 2.5 : 1.5} />}
            </NavLink>
            <NavLink to="/analytics" className={({ isActive }) => `mob-tab active-mob-portal ${isActive ? 'active-tab' : ''}`}>
                {({ isActive }) => <Activity size={24} strokeWidth={2.5} color={isActive ? '#000' : 'var(--accent-color)'} />}
            </NavLink>
        </div>
    );
};
