import React from 'react';
import { motion } from 'framer-motion';
import type { Variants } from 'framer-motion';
import { Book, Sparkles, Navigation, ShieldCheck } from 'lucide-react';
import './UploadPage.css';

const fadeUp: Variants = {
    hidden: { opacity: 0, y: 50 },
    visible: (i: number) => ({
        opacity: 1,
        y: 0,
        transition: {
            delay: i * 0.1,
            duration: 0.8,
            ease: [0.16, 1, 0.3, 1]
        }
    })
};

const UploadPage: React.FC = () => {
    return (
        <div className="upload-view">
            {/* The Hook (Hero) */}
            <section className="hero-section">
                <motion.div
                    className="hero-badge"
                    initial="hidden" animate="visible" custom={0} variants={fadeUp}
                >
                    01 // STUDY MATERIALS
                </motion.div>

                <motion.h1
                    className="hero-title"
                    initial="hidden" animate="visible" custom={1} variants={fadeUp}
                >
                    Upload Your<br />
                    <span className="text-italic">Study Materials</span>
                </motion.h1>

                <motion.p
                    className="hero-subtext"
                    initial="hidden" animate="visible" custom={2} variants={fadeUp}
                >
                    Upload your documents, notes, or textbooks. Krishna will read and understand your materials to help guide you through any subject, making sure every answer is based on your own notes.
                </motion.p>

                <motion.button
                    className="hero-cta desktop-only"
                    initial="hidden" animate="visible" custom={3} variants={fadeUp}
                >
                    <Book size={20} /> UPLOAD DOCUMENTS
                </motion.button>
                <motion.button
                    className="hero-cta mobile-only"
                    initial="hidden" animate="visible" custom={3} variants={fadeUp}
                >
                    <Book size={20} /> UPLOAD
                </motion.button>

                {/* Custom scroll affordance */}
                <motion.div
                    className="scroll-indicator desktop-only"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1, height: [0, 60, 0] }}
                    transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                />
            </section>

            {/* Infinite Marquee */}
            <div className="marquee-container">
                <div className="marquee-content">
                    <span className="marquee-text">focused learning • honest answers • active guidance •</span>
                    <span className="marquee-text">focused learning • honest answers • active guidance •</span>
                </div>
            </div>

            {/* Bento Grid (Desktop) / Horizontal Snap (Mobile) */}
            <section className="capabilities-section">
                <motion.h2
                    className="section-title"
                    initial={{ opacity: 0, x: -50 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true, margin: "-100px" }}
                    transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                >
                    How Krishna Guides You
                </motion.h2>

                <div className="bento-grid">
                    <motion.div className="bento-item wide-item"
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                    >
                        <div className="bento-icon"><Sparkles size={32} /></div>
                        <h3>Deep Understanding</h3>
                        <p>Your documents are securely processed and understood, allowing Krishna to find exact, relevant contexts for your questions instantly.</p>
                    </motion.div>

                    <motion.div className="bento-item tall-item"
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6, delay: 0.1 }}
                    >
                        <div className="bento-icon"><ShieldCheck size={32} /></div>
                        <h3>True to the Text</h3>
                        <p>Krishna never guesses or makes things up. Every answer is strictly grounded in the exact materials and documents you upload.</p>
                    </motion.div>

                    <motion.div className="bento-item"
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                    >
                        <div className="bento-icon"><Navigation size={32} /></div>
                        <h3>Adaptive Pathing</h3>
                        <p>Krishna extracts core concepts to automatically forge a learning path tailored exactly to your progress.</p>
                    </motion.div>
                </div>
            </section>
        </div>
    );
};

export default UploadPage;
