import React, { useState, useEffect, useRef } from 'react';
import { BookOpen, Target, Send, Paperclip, Menu, X, CheckCircle, FileText, Plus, MessageCircle, MoreHorizontal, Loader2 } from 'lucide-react';
import './AppPage.css';
import { uploadDocument, askQuestion } from '../services/api';

type Tab = 'chat' | 'knowledge' | 'tests';

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

interface ChatSession {
    id: string;
    title: string;
    date: string;
    messages: Message[];
    documents: string[];
    quizzes: any[]; // placeholder for quiz data
}

// Initial mock state
const INITIAL_CHATS: ChatSession[] = [
    {
        id: '1',
        title: 'Vedantic Philosophy',
        date: 'Today',
        messages: [
            { role: 'assistant', content: 'Greetings. I am Krishna. We can discuss the Bhagavad Gita and Vedantic principles based on your uploads.' },
            { role: 'user', content: 'What is Dharma?' },
            { role: 'assistant', content: 'In the context of your uploaded text, Dharma refers to righteous duty. It is the path one must follow to maintain cosmic order and personal integrity.' }
        ],
        documents: ['Bhagavad_Gita_Notes.pdf', 'Upanishads_Summary.docx'],
        quizzes: [{ title: 'The Nature of Duty', questions: 5, status: 'Needs Review' }]
    },
    {
        id: '2',
        title: 'Calculus: Derivatives',
        date: 'Yesterday',
        messages: [
            { role: 'assistant', content: 'I am ready to assist with your Calculus materials. What concept needs clarity?' }
        ],
        documents: ['Calculus_Chapter_2.pdf'],
        quizzes: []
    }
];

export default function AppPage() {
    const [activeTab, setActiveTab] = useState<Tab>('chat');
    const [isSidebarOpen, setSidebarOpen] = useState(false);

    // App State
    const [chats, setChats] = useState<ChatSession[]>(INITIAL_CHATS);
    const [activeChatId, setActiveChatId] = useState<string>('1');
    const [input, setInput] = useState('');
    const [isThinking, setIsThinking] = useState(false);

    // Upload State
    const [isUploading, setIsUploading] = useState(false);
    const [uploadMessage, setUploadMessage] = useState('');
    const fileInputRef = useRef<HTMLInputElement>(null);

    const messagesEndRef = useRef<HTMLDivElement>(null);

    const activeChat = chats.find(c => c.id === activeChatId) || chats[0];

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [activeChat?.messages]);

    const handleNewChat = () => {
        const newChatId = Date.now().toString();
        const newChat: ChatSession = {
            id: newChatId,
            title: 'New Conversation',
            date: 'Today',
            messages: [{ role: 'assistant', content: 'Greetings. I am Krishna. What knowledge seek you from your materials today?' }],
            documents: [],
            quizzes: []
        };
        setChats(prev => [newChat, ...prev]);
        setActiveChatId(newChatId);
        setActiveTab('chat');
        if (window.innerWidth < 1024) setSidebarOpen(false);
    };

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || !activeChat || isThinking) return;

        const userMessage = input;

        // Update local state: add user message
        setChats(prev => prev.map(chat => {
            if (chat.id === activeChatId) {
                const title = (chat.title === 'New Conversation' && userMessage.length > 3)
                    ? userMessage.substring(0, 30) + '...'
                    : chat.title;
                return { ...chat, title, messages: [...chat.messages, { role: 'user', content: userMessage }] };
            }
            return chat;
        }));
        setInput('');
        setIsThinking(true);

        try {
            const response = await askQuestion(userMessage);

            setChats(prev => prev.map(chat => {
                if (chat.id === activeChatId) {
                    return {
                        ...chat,
                        messages: [...chat.messages, {
                            role: 'assistant',
                            content: response.answer
                        }]
                    };
                }
                return chat;
            }));
        } catch (err: any) {
            console.error('Chat error:', err);
            setChats(prev => prev.map(chat => {
                if (chat.id === activeChatId) {
                    return {
                        ...chat,
                        messages: [...chat.messages, {
                            role: 'assistant',
                            content: err.response?.data?.detail || 'I could not process your question. Please ensure documents are uploaded and try again.'
                        }]
                    };
                }
                return chat;
            }));
        } finally {
            setIsThinking(false);
        }
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file || !activeChat) return;

        setIsUploading(true);
        setUploadMessage('');

        try {
            const response = await uploadDocument(file);

            setUploadMessage(`Success! ${response.message} (${response.total_chunks} chunks indexed)`);

            // Add document to current chat state
            setChats(prev => prev.map(chat => {
                if (chat.id === activeChatId) {
                    return { ...chat, documents: [...chat.documents, response.filename] };
                }
                return chat;
            }));
        } catch (err: any) {
            console.error('Upload failed:', err);
            setUploadMessage(err.response?.data?.detail || 'Failed to upload document. Please try again.');
        } finally {
            setIsUploading(false);
            // Reset input
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    const triggerFileInput = () => {
        fileInputRef.current?.click();
    };

    const renderChat = () => (
        <div className="app-chat-view">
            <div className="chat-messages-container">
                {activeChat?.messages.map((msg, i) => (
                    <div key={i} className={`chat-message-row ${msg.role}`}>
                        <div className="chat-avatar">
                            {msg.role === 'assistant' ? 'K' : 'U'}
                        </div>
                        <div className={`chat-bubble ${msg.role}`}>
                            <p>{msg.content}</p>
                        </div>
                    </div>
                ))}
                {isThinking && (
                    <div className="chat-message-row assistant">
                        <div className="chat-avatar">K</div>
                        <div className="chat-bubble assistant thinking-bubble">
                            <span className="dot-pulse"></span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-area">
                <form className="chat-input-box" onSubmit={handleSend}>
                    <button type="button" className="attach-btn" title="Upload Document" onClick={() => setActiveTab('knowledge')}>
                        <Paperclip size={20} />
                    </button>
                    <input
                        type="text"
                        placeholder="Seek guidance from Krishna..."
                        value={input}
                        onChange={e => setInput(e.target.value)}
                    />
                    <button type="submit" className="send-btn" disabled={!input.trim() || isThinking}><Send size={18} /></button>
                </form>
                <p className="chat-footer-text">Krishna only references your uploaded documents for <b>"{activeChat?.title}"</b>.</p>
            </div>
        </div>
    );

    const renderKnowledge = () => (
        <div className="app-content-view">
            <div className="content-header">
                <h1 className="content-title">Knowledgebase</h1>
                <p className="content-subtitle">Files isolated to the context of <b>"{activeChat?.title}"</b>.</p>
            </div>

            <div className="upload-dropzone" onClick={isUploading ? undefined : triggerFileInput}>
                {isUploading ? (
                    <Loader2 size={48} className="dropzone-icon spinning" />
                ) : (
                    <BookOpen size={48} className="dropzone-icon" />
                )}

                <h3>{isUploading ? 'Uploading & Indexing...' : 'Upload your text materials directly'}</h3>
                <p className="dropzone-formats">Supports .PDF, .TXT, .MD, .DOCX</p>

                <input
                    type="file"
                    ref={fileInputRef}
                    style={{ display: 'none' }}
                    accept=".pdf,.txt,.md,.docx"
                    onChange={handleFileUpload}
                />
                <button className="primary-btn" disabled={isUploading}>
                    {isUploading ? 'Processing...' : 'Browse Files'}
                </button>
            </div>

            {uploadMessage && (
                <div className="upload-result-msg">
                    <p>{uploadMessage}</p>
                </div>
            )}

            <div className="uploaded-list">
                <h4 className="list-title">Active Materials in this Chat ({activeChat?.documents.length || 0})</h4>
                {activeChat?.documents.length === 0 ? (
                    <p style={{ color: 'var(--text-secondary)', marginTop: '1rem' }}>No documents uploaded for this chat yet.</p>
                ) : (
                    activeChat?.documents.map((doc, idx) => (
                        <div key={idx} className="uploaded-file">
                            <div className="file-info-group">
                                <FileText size={24} className="file-icon" />
                                <div className="file-info">
                                    <span className="file-name">{doc}</span>
                                    <span className="file-meta">Indexed for Retrieval</span>
                                </div>
                            </div>
                            <CheckCircle size={24} className="file-status active" />
                        </div>
                    ))
                )}
            </div>
        </div>
    );

    const renderTests = () => (
        <div className="app-content-view">
            <div className="content-header">
                <h1 className="content-title">Mastery Quizzes</h1>
                <p className="content-subtitle">Quizzes generated for <b>"{activeChat?.title}"</b>.</p>
            </div>

            <div className="tests-grid">
                {activeChat?.quizzes.length === 0 ? (
                    <p style={{ color: 'var(--text-secondary)', gridColumn: '1 / -1' }}>No quizzes generated for this thread yet.</p>
                ) : (
                    activeChat?.quizzes.map((quiz, idx) => (
                        <div key={idx} className="test-card">
                            <h4>{quiz.title}</h4>
                            <p className="test-meta">{quiz.questions} Questions • {quiz.status}</p>
                            <button className="secondary-btn">Review</button>
                        </div>
                    ))
                )}
                <button className="create-test-card" onClick={() => alert('Quiz generation simulation')}>
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
                    <button className="new-chat-btn" onClick={handleNewChat}>
                        <Plus size={20} /> New Chat
                    </button>
                    <button onClick={() => setSidebarOpen(false)} className="close-sidebar mobile-only">
                        <X size={24} />
                    </button>
                </div>

                <div className="sidebar-history">
                    <div className="history-group">
                        <span className="history-label">Recent Conversations</span>
                        {chats.map(chat => (
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
                            <span className="context-label">Krishna AI</span>
                            <span className="context-title">{activeChat?.title || 'New Chat'}</span>
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
                        {/* Balance flex header */}
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
