import React, { useState, useEffect, useRef } from 'react';
import { BookOpen, Target, Send, Paperclip, Menu, X, CheckCircle, FileText, Plus, MessageCircle, MoreHorizontal } from 'lucide-react';
import './AppPage.css';

type Tab = 'chat' | 'knowledge' | 'tests';

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

interface ChatSession {
    id: string;
    title: string;
    date: string;
}

const MOCK_CHATS: ChatSession[] = [
    { id: '1', title: 'Vedantic Philosophy', date: 'Today' },
    { id: '2', title: 'Calculus: Derivatives', date: 'Yesterday' },
    { id: '3', title: 'World War II Timeline', date: 'Previous 7 Days' }
];

export default function AppPage() {
    const [activeTab, setActiveTab] = useState<Tab>('chat');
    const [isSidebarOpen, setSidebarOpen] = useState(false);
    const [activeChatId, setActiveChatId] = useState<string>('1');

    // Chat State
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState<Message[]>([
        { role: 'assistant', content: 'Greetings. I am Krishna. What knowledge seek you from your materials today?' }
    ]);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = input;
        setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setInput('');

        // Simulate AI response
        setTimeout(() => {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'I understand your inquiry. Based on the sacred texts and materials you provided, the essence lies within the foundational principles we previously uploaded. Let me guide you clearly...'
            }]);
        }, 1200);
    };

    const renderChat = () => (
        <div className="app-chat-view">
            <div className="chat-messages-container">
                {messages.map((msg, i) => (
                    <div key={i} className={`chat-message-row ${msg.role}`}>
                        <div className="chat-avatar">
                            {msg.role === 'assistant' ? 'K' : 'U'}
                        </div>
                        <div className={`chat-bubble ${msg.role}`}>
                            <p>{msg.content}</p>
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-area">
                <form className="chat-input-box" onSubmit={handleSend}>
                    <button type="button" className="attach-btn" title="Upload Document"><Paperclip size={20} /></button>
                    <input
                        type="text"
                        placeholder="Seek guidance from Krishna..."
                        value={input}
                        onChange={e => setInput(e.target.value)}
                    />
                    <button type="submit" className="send-btn" disabled={!input.trim()}><Send size={18} /></button>
                </form>
                <p className="chat-footer-text">Krishna only references your uploaded documents. Absolute fidelity.</p>
            </div>
        </div>
    );

    const renderKnowledge = () => (
        <div className="app-content-view">
            <div className="content-header">
                <h1 className="content-title">Knowledgebase</h1>
                <p className="content-subtitle">Manage the documents specific to this conversation.</p>
            </div>

            <div className="upload-dropzone">
                <BookOpen size={48} className="dropzone-icon" />
                <h3>Drag & Drop your texts here</h3>
                <p className="dropzone-formats">Supports .PDF, .TXT, .MD, .DOCX</p>
                <button className="primary-btn">Browse Files</button>
            </div>

            <div className="uploaded-list">
                <h4 className="list-title">Active Materials in this Chat</h4>
                <div className="uploaded-file">
                    <div className="file-info-group">
                        <FileText size={24} className="file-icon" />
                        <div className="file-info">
                            <span className="file-name">Complete_Syllabus_Notes.pdf</span>
                            <span className="file-meta">1.2 MB • Indexed</span>
                        </div>
                    </div>
                    <CheckCircle size={24} className="file-status active" />
                </div>
            </div>
        </div>
    );

    const renderTests = () => (
        <div className="app-content-view">
            <div className="content-header">
                <h1 className="content-title">Mastery Quizzes</h1>
                <p className="content-subtitle">Quizzes generated for the topics discussed in this thread.</p>
            </div>

            <div className="tests-grid">
                <div className="test-card">
                    <h4>Chapter 1: Core Concepts</h4>
                    <p className="test-meta">10 Questions • Needs Review</p>
                    <button className="secondary-btn">Retake Quiz</button>
                </div>
                <div className="test-card">
                    <h4>The Nature of Duty</h4>
                    <p className="test-meta">5 Questions • Excellent</p>
                    <button className="secondary-btn">Review Answers</button>
                </div>
                <button className="create-test-card">
                    <Target size={32} className="create-test-icon" />
                    <span>Generate New Quiz</span>
                </button>
            </div>
        </div>
    );

    return (
        <div className="product-layout">
            {/* Sidebar (ChatGPT Style Chat History) */}
            <aside className={`product-sidebar ${isSidebarOpen ? 'open' : ''}`}>
                <div className="sidebar-header">
                    <button className="new-chat-btn">
                        <Plus size={20} /> New Chat
                    </button>
                    <button onClick={() => setSidebarOpen(false)} className="close-sidebar mobile-only">
                        <X size={24} />
                    </button>
                </div>

                <div className="sidebar-history">
                    <div className="history-group">
                        <span className="history-label">Recent</span>
                        {MOCK_CHATS.map(chat => (
                            <button
                                key={chat.id}
                                className={`history-item ${activeChatId === chat.id ? 'active' : ''}`}
                                onClick={() => { setActiveChatId(chat.id); setSidebarOpen(false); }}
                            >
                                <MessageCircle size={18} className="history-icon" />
                                <span className="history-title">{chat.title}</span>
                                <MoreHorizontal size={16} className="history-more" />
                            </button>
                        ))}
                    </div>
                </div>

                <div className="sidebar-footer">
                    <div className="user-profile">
                        <div className="user-avatar">U</div>
                        <div className="user-details">
                            <span className="user-name">User Account</span>
                            <span className="user-plan">Free Plan</span>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Backdrop for mobile */}
            {isSidebarOpen && <div className="sidebar-backdrop mobile-only" onClick={() => setSidebarOpen(false)} />}

            {/* Main Area */}
            <main className="product-main">
                {/* Top Navbar (Chat context aware) */}
                <header className="product-topbar">
                    <div className="topbar-left">
                        <button onClick={() => setSidebarOpen(true)} className="menu-btn mobile-only">
                            <Menu size={24} />
                        </button>
                        <div className="topbar-context desktop-only">
                            <span className="context-label">Krishna</span>
                            <span className="context-title">{MOCK_CHATS.find(c => c.id === activeChatId)?.title || 'New Chat'}</span>
                        </div>
                    </div>

                    <div className="topbar-tabs">
                        <button
                            className={`top-tab ${activeTab === 'chat' ? 'active' : ''}`}
                            onClick={() => setActiveTab('chat')}
                        >
                            Chat
                        </button>
                        <button
                            className={`top-tab ${activeTab === 'knowledge' ? 'active' : ''}`}
                            onClick={() => setActiveTab('knowledge')}
                        >
                            Knowledgebase
                        </button>
                        <button
                            className={`top-tab ${activeTab === 'tests' ? 'active' : ''}`}
                            onClick={() => setActiveTab('tests')}
                        >
                            Quizzes
                        </button>
                    </div>

                    <div className="topbar-right">
                        {/* Empty placeholder to balance layout, or future settings icon */}
                    </div>
                </header>

                <div className="product-content-area">
                    {activeTab === 'chat' && renderChat()}
                    {activeTab === 'knowledge' && renderKnowledge()}
                    {activeTab === 'tests' && renderTests()}
                </div>
            </main>
        </div>
    );
}
