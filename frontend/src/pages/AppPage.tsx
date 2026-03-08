import React, { useState, useEffect, useRef } from 'react';
import { BookOpen, Send, Paperclip, Menu, X, CheckCircle, FileText, Plus, MessageCircle, MoreHorizontal, Loader2, AlertTriangle, TrendingUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import './AppPage.css';
import { uploadDocument, askQuestion, generateQuiz, submitQuiz, getProgress } from '../services/api';
import type { QuizQuestion, QuizSubmitResponse, ProgressResponse } from '../services/api';

type Tab = 'chat' | 'knowledge' | 'tests' | 'analytics';

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

    // Quiz State
    const [quizTopic, setQuizTopic] = useState('');
    const [quizQuestions, setQuizQuestions] = useState<QuizQuestion[]>([]);
    const [quizAnswers, setQuizAnswers] = useState<string[]>([]);
    const [quizResult, setQuizResult] = useState<QuizSubmitResponse | null>(null);
    const [isGeneratingQuiz, setIsGeneratingQuiz] = useState(false);
    const [isSubmittingQuiz, setIsSubmittingQuiz] = useState(false);
    const [quizError, setQuizError] = useState('');

    // Analytics State
    const [progressData, setProgressData] = useState<ProgressResponse | null>(null);
    const [isLoadingProgress, setIsLoadingProgress] = useState(false);

    const messagesEndRef = useRef<HTMLDivElement>(null);

    const activeChat = chats.find(c => c.id === activeChatId) || chats[0];

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [activeChat?.messages]);

    // Reset quiz & upload state when switching chats
    useEffect(() => {
        setQuizQuestions([]);
        setQuizAnswers([]);
        setQuizResult(null);
        setQuizError('');
        setQuizTopic('');
        setUploadMessage('');
        setActiveTab('chat');
    }, [activeChatId]);

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

    const handleGenerateQuiz = async () => {
        const topic = quizTopic.trim() || activeChat?.title || 'General';
        setIsGeneratingQuiz(true);
        setQuizError('');
        setQuizQuestions([]);
        setQuizAnswers([]);
        setQuizResult(null);

        try {
            const response = await generateQuiz(topic, 5, true);
            setQuizQuestions(response.questions);
            setQuizAnswers(new Array(response.questions.length).fill(''));
            setQuizTopic(response.topic);
        } catch (err: any) {
            console.error('Quiz generation failed:', err);
            setQuizError(err.response?.data?.detail || 'Failed to generate quiz. Make sure documents are uploaded first.');
        } finally {
            setIsGeneratingQuiz(false);
        }
    };

    const handleSubmitQuiz = async () => {
        if (quizAnswers.some(a => !a)) {
            setQuizError('Please answer all questions before submitting.');
            return;
        }
        setIsSubmittingQuiz(true);
        setQuizError('');

        try {
            // Backend expects just the letter (e.g. "A"), but quizAnswers stores
            // the full option text (e.g. "A) THE PLAINS..."). Extract the letter.
            const letterAnswers = quizAnswers.map(ans => {
                const match = ans.match(/^([A-Da-d])\)/);
                return match ? match[1].toUpperCase() : ans;
            });
            const result = await submitQuiz(quizTopic, letterAnswers, quizQuestions);
            setQuizResult(result);
        } catch (err: any) {
            console.error('Quiz submit failed:', err);
            setQuizError(err.response?.data?.detail || 'Failed to submit quiz.');
        } finally {
            setIsSubmittingQuiz(false);
        }
    };

    const handleSelectAnswer = (questionIdx: number, option: string) => {
        setQuizAnswers(prev => {
            const updated = [...prev];
            updated[questionIdx] = option;
            return updated;
        });
    };

    const resetQuiz = () => {
        setQuizQuestions([]);
        setQuizAnswers([]);
        setQuizResult(null);
        setQuizError('');
    };

    const renderTests = () => (
        <div className="app-content-view">
            <div className="content-header">
                <h1 className="content-title">Quizzes</h1>
                <p className="content-subtitle">Test your understanding of <b>"{activeChat?.title}"</b>.</p>
            </div>

            {/* No quiz active — show generator */}
            {quizQuestions.length === 0 && !quizResult && (
                <div className="quiz-generator">
                    <div className="quiz-topic-input">
                        <input
                            type="text"
                            placeholder={`Topic (defaults to "${activeChat?.title}")`}
                            value={quizTopic}
                            onChange={e => setQuizTopic(e.target.value)}
                            className="quiz-topic-field"
                        />
                        <button
                            className="primary-btn"
                            onClick={handleGenerateQuiz}
                            disabled={isGeneratingQuiz}
                        >
                            {isGeneratingQuiz ? 'Generating...' : 'Generate Quiz'}
                        </button>
                    </div>
                    {isGeneratingQuiz && (
                        <div className="quiz-loading">
                            <Loader2 size={32} className="spinning" />
                            <p>Krishna is preparing questions from your materials...</p>
                        </div>
                    )}
                </div>
            )}

            {/* Quiz questions with radio buttons */}
            {quizQuestions.length > 0 && !quizResult && (
                <div className="quiz-questions">
                    {quizQuestions.map((q, qIdx) => (
                        <div key={qIdx} className="quiz-question-card">
                            <h4 className="question-number">Question {qIdx + 1} of {quizQuestions.length}</h4>
                            <p className="question-text">{q.question}</p>
                            <div className="question-options">
                                {q.options.map((opt, oIdx) => (
                                    <label key={oIdx} className={`option-label ${quizAnswers[qIdx] === opt ? 'selected' : ''}`}>
                                        <input
                                            type="radio"
                                            name={`q-${qIdx}`}
                                            value={opt}
                                            checked={quizAnswers[qIdx] === opt}
                                            onChange={() => handleSelectAnswer(qIdx, opt)}
                                        />
                                        <span className="option-radio" />
                                        <span className="option-text">{opt}</span>
                                    </label>
                                ))}
                            </div>
                        </div>
                    ))}

                    <button
                        className="primary-btn quiz-submit-btn"
                        onClick={handleSubmitQuiz}
                        disabled={isSubmittingQuiz}
                    >
                        {isSubmittingQuiz ? 'Submitting...' : 'Submit Answers'}
                    </button>
                </div>
            )}

            {/* Quiz result */}
            {quizResult && (
                <div className="quiz-result">
                    <div className="result-score-card">
                        <h2 className="result-score">{quizResult.percentage}%</h2>
                        <p className="result-detail">{quizResult.score} / {quizResult.total} correct</p>
                        <p className="result-topic">Topic: {quizResult.topic}</p>
                    </div>

                    {quizResult.incorrect_questions.length > 0 && (
                        <div className="result-review">
                            <h4>Review Incorrect Answers</h4>
                            {quizResult.incorrect_questions.map((item, i) => (
                                <div key={i} className="review-item incorrect">
                                    <p className="review-question">{item.question}</p>
                                    <p className="review-answer">Your answer: <span className="wrong">{item.user_answer}</span></p>
                                    <p className="review-answer">Correct: <span className="correct">{item.correct_answer}</span></p>
                                    <p className="review-explanation">{item.explanation}</p>
                                </div>
                            ))}
                        </div>
                    )}

                    {quizResult.correct_questions.length > 0 && (
                        <div className="result-review">
                            <h4>Correct Answers</h4>
                            {quizResult.correct_questions.map((item, i) => (
                                <div key={i} className="review-item correct-item">
                                    <p className="review-question">{item.question}</p>
                                    <p className="review-explanation">{item.explanation}</p>
                                </div>
                            ))}
                        </div>
                    )}

                    <button className="primary-btn" onClick={resetQuiz}>Take Another Quiz</button>
                </div>
            )}

            {quizError && (
                <div className="upload-result-msg" style={{ borderColor: '#e74c3c' }}>
                    <p>{quizError}</p>
                </div>
            )}
        </div>
    );

    // ── Analytics ───────────────────────────────────────────────────────
    const fetchProgress = async () => {
        setIsLoadingProgress(true);
        try {
            const data = await getProgress();
            setProgressData(data);
        } catch (err) {
            console.error('Failed to fetch progress:', err);
        } finally {
            setIsLoadingProgress(false);
        }
    };

    const renderAnalytics = () => {
        // Fetch on first open
        if (!progressData && !isLoadingProgress) {
            fetchProgress();
        }

        if (isLoadingProgress) {
            return (
                <div className="app-content-view" style={{ alignItems: 'center', justifyContent: 'center' }}>
                    <Loader2 size={40} className="spinning" />
                    <p style={{ color: 'var(--text-secondary)' }}>Loading your progress...</p>
                </div>
            );
        }

        if (!progressData) {
            return (
                <div className="app-content-view">
                    <p style={{ color: 'var(--text-secondary)' }}>No progress data available yet. Complete some quizzes first.</p>
                </div>
            );
        }

        const barData = progressData.topics.map(t => ({
            topic: t.topic.length > 15 ? t.topic.substring(0, 15) + '...' : t.topic,
            accuracy: Math.round(t.accuracy * 100),
            attempts: t.attempts,
        }));

        const lineData = progressData.topics.map((t, i) => ({
            name: `Quiz ${i + 1}`,
            score: Math.round(t.accuracy * 100),
        }));

        return (
            <div className="app-content-view">
                <div className="content-header">
                    <h1 className="content-title">Progress</h1>
                    <p className="content-subtitle">Your learning analytics across all topics.</p>
                </div>

                {/* Charts Row */}
                <div className="analytics-charts">
                    <div className="chart-card">
                        <h4 className="chart-title">Accuracy by Topic</h4>
                        <ResponsiveContainer width="100%" height={280}>
                            <BarChart data={barData} margin={{ top: 10, right: 10, left: -10, bottom: 30 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                                <XAxis dataKey="topic" tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} angle={-30} textAnchor="end" />
                                <YAxis tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }} domain={[0, 100]} unit="%" />
                                <Tooltip
                                    contentStyle={{ background: '#1a1f36', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 8, color: '#fff' }}
                                    formatter={(value: any) => [`${value}%`, 'Accuracy']}
                                />
                                <Bar dataKey="accuracy" fill="#fbd34d" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    <div className="chart-card">
                        <h4 className="chart-title">Score Trend</h4>
                        <ResponsiveContainer width="100%" height={280}>
                            <LineChart data={lineData} margin={{ top: 10, right: 10, left: -10, bottom: 10 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                                <XAxis dataKey="name" tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }} />
                                <YAxis tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }} domain={[0, 100]} unit="%" />
                                <Tooltip
                                    contentStyle={{ background: '#1a1f36', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 8, color: '#fff' }}
                                    formatter={(value: any) => [`${value}%`, 'Score']}
                                />
                                <Line type="monotone" dataKey="score" stroke="#fbd34d" strokeWidth={2} dot={{ fill: '#fbd34d', r: 4 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Topic Lists */}
                <div className="analytics-lists">
                    <div className="analytics-list-card">
                        <h4 className="list-card-title">
                            <AlertTriangle size={18} style={{ color: '#e74c3c' }} />
                            Weak Topics
                        </h4>
                        {progressData.weak_topics.length === 0 ? (
                            <p className="list-empty">No weak topics identified yet.</p>
                        ) : (
                            progressData.weak_topics.map((t, i) => (
                                <div key={i} className="topic-item weak">
                                    <span className="topic-name">{t.topic}</span>
                                    <div className="topic-stats">
                                        <span className="topic-accuracy">{Math.round(t.accuracy * 100)}%</span>
                                        <span className="topic-attempts">{t.attempts} attempts</span>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>

                    <div className="analytics-list-card">
                        <h4 className="list-card-title">
                            <TrendingUp size={18} style={{ color: '#2ecc71' }} />
                            Strong Topics
                        </h4>
                        {progressData.strong_topics.length === 0 ? (
                            <p className="list-empty">No strong topics identified yet.</p>
                        ) : (
                            progressData.strong_topics.map((t, i) => (
                                <div key={i} className="topic-item strong">
                                    <span className="topic-name">{t.topic}</span>
                                    <div className="topic-stats">
                                        <span className="topic-accuracy">{Math.round(t.accuracy * 100)}%</span>
                                        <span className="topic-attempts">{t.attempts} attempts</span>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Recommendations */}
                {progressData.recommendations.length > 0 && (
                    <div className="analytics-list-card">
                        <h4 className="list-card-title">
                            <BookOpen size={18} style={{ color: 'var(--accent-color)' }} />
                            Recommendations
                        </h4>
                        {progressData.recommendations.map((rec, i) => (
                            <div key={i} className="recommendation-item">
                                <span>{rec}</span>
                            </div>
                        ))}
                    </div>
                )}

                <button className="primary-btn" onClick={fetchProgress} style={{ alignSelf: 'center' }}>
                    Refresh Data
                </button>
            </div>
        );
    };

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
                        <button
                            className={`top-tab ${activeTab === 'analytics' ? 'active' : ''}`}
                            onClick={() => setActiveTab('analytics')}
                        >
                            Progress
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
                    {activeTab === 'analytics' && renderAnalytics()}
                </div>
            </main>
        </div>
    );
}
