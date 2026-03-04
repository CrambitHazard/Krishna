import React from 'react';
import { motion } from 'framer-motion';
import './QuizPage.css';

const MOCK_QUIZZES = [
    { id: '1', concept: 'The Bhagavad Gita: Duty', score: '98%', status: 'EXCELLENT' },
    { id: '2', concept: 'Understanding Dharma', score: '64%', status: 'NEEDS REVIEW' },
    { id: '3', concept: 'Paths of Yoga', score: '81%', status: 'GOOD' },
];

const QuizPage: React.FC = () => {
    return (
        <div className="quiz-view">

            {/* ── Laptop: Editorial Split Scroll ── */}
            <section className="editorial-split desktop-only">
                {/* Pinned Left Side */}
                <div className="editorial-pinned">
                    <div className="sticky-content">
                        <span className="editorial-label">03 // ASSESSMENT</span>
                        <h1 className="editorial-title">
                            TAKE A<br />QUIZ
                        </h1>
                        <p className="editorial-desc">
                            Don't just read your notes. Test yourself. Generate custom quizzes based on your uploaded materials to make sure you actually understand and remember the content.
                        </p>
                        <button className="editorial-btn">START NEW QUIZ</button>
                    </div>
                </div>

                {/* Scrolling Right Side */}
                <div className="editorial-scrolling">
                    {MOCK_QUIZZES.map((quiz, i) => (
                        <motion.div
                            key={quiz.id}
                            className="editorial-module"
                            initial={{ opacity: 0, y: 100 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: '-10% 0px -10% 0px' }}
                            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1], delay: i * 0.1 }}
                        >
                            <div className="module-image-card">
                                {/* Visual placeholder for editorial media */}
                                <div className="module-overlay-grain"></div>
                                <div className="module-meta">
                                    <span>LESSON 0{quiz.id}</span>
                                    <span className="accent-tag">{quiz.status}</span>
                                </div>
                            </div>
                            <h2 className="module-heading">{quiz.concept}</h2>
                            <div className="module-metrics">
                                <div>
                                    <label>YOUR SCORE</label>
                                    <span>{quiz.score}</span>
                                </div>
                                <button className="module-action">RETAKE QUIZ</button>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* ── Mobile: Grid-Breaking Blocks ── */}
            <section className="mobile-editorial mobile-only">
                <div className="mobile-editorial-header">
                    <span className="editorial-label">03 // ASSESSMENT</span>
                    <h1 className="editorial-title">QUIZZES</h1>
                    <p className="editorial-desc">Test your knowledge with personalized questions.</p>
                    <button className="editorial-btn">START QUIZ</button>
                </div>

                <div className="mobile-modules-container">
                    {MOCK_QUIZZES.map((quiz, i) => (
                        <motion.div
                            className="mobile-editorial-block"
                            key={quiz.id}
                            initial={{ opacity: 0, y: 50 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.6, delay: i * 0.1 }}
                        >
                            <div className="mobile-image-wrapper">
                                <div className="mobile-grain"></div>
                            </div>
                            {/* Intentional text breaking grid bounds by translating up into the image space */}
                            <div className="mobile-overlap-content">
                                <span className="mobile-status">{quiz.status}</span>
                                <h3>{quiz.concept}</h3>
                                <div className="mobile-score-row">
                                    <span>Score: {quiz.score}</span>
                                    <button className="mobile-retest">RETEST</button>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </section>

        </div>
    );
};

export default QuizPage;
