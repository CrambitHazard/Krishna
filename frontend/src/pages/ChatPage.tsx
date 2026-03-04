import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, MessageCircle, Lightbulb, Compass } from 'lucide-react';
import './ChatPage.css';

// Mock Knowledge Nodes for interaction display
const KNOWLEDGE_NODES = [
    { id: '1', title: 'ADAPTS TO YOU', desc: 'Krishna understands your level, offering simpler explanations when you struggle and deeper details when you excel.' },
    { id: '2', title: 'TRUE TO YOUR NOTES', desc: 'Every answer is drawn directly from the texts you provide, making sure it is highly relevant.' },
    { id: '3', title: 'GUIDED LEARNING', desc: 'Krishna does not just give you the answer; he asks helpful questions to make sure you actually understand the topic.' }
];

const ChatPage: React.FC = () => {
    const [hoveredNode, setHoveredNode] = useState<string | null>(null);

    return (
        <div className="chat-view">
            <section className="interaction-header">
                <h1 className="section-title text-massive">CHAT WITH KRISHNA</h1>
                <p className="section-subtitle">Ask questions based on your uploaded notes.</p>
            </section>

            {/* ── Laptop: List-to-Hover Interaction ── */}
            <section className="list-to-hover desktop-only">
                <div className="lth-container">
                    {KNOWLEDGE_NODES.map((node) => (
                        <div
                            key={node.id}
                            className="lth-item"
                            onMouseEnter={() => setHoveredNode(node.id)}
                            onMouseLeave={() => setHoveredNode(null)}
                        >
                            <div className="lth-text-block">
                                <span className="lth-id">0{node.id} &mdash;</span>
                                <h2>{node.title}</h2>
                            </div>
                            <ArrowRight size={40} className="lth-arrow" />
                        </div>
                    ))}
                </div>

                {/* Floating preview attached to hovering */}
                <div className="lth-preview-layer">
                    <AnimatePresence>
                        {hoveredNode && (
                            <motion.div
                                className="lth-floating-card"
                                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                                animate={{ opacity: 1, scale: 1, y: 0 }}
                                exit={{ opacity: 0, scale: 0.95, y: -20 }}
                                transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                            >
                                <div className="floating-inner">
                                    {hoveredNode === '1' && <MessageCircle size={80} strokeWidth={1} color="var(--accent-color)" />}
                                    {hoveredNode === '2' && <Compass size={80} strokeWidth={1} color="var(--accent-color)" />}
                                    {hoveredNode === '3' && <Lightbulb size={80} strokeWidth={1} color="var(--accent-color)" />}

                                    <p>{KNOWLEDGE_NODES.find(n => n.id === hoveredNode)?.desc}</p>

                                    <button className="initiate-btn">START CHAT</button>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </section>

            {/* ── Mobile: Full-Bleed Stacked Cards (NO HOVER) ── */}
            <section className="mobile-stacked mobile-only">
                {KNOWLEDGE_NODES.map((node, i) => (
                    <motion.div
                        key={node.id}
                        className="mobile-card"
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: '-50px' }}
                        transition={{ delay: i * 0.1, duration: 0.6 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <div className="mobile-badge">0{node.id}</div>

                        <div className="mobile-card-media">
                            {node.id === '1' && <MessageCircle size={50} strokeWidth={1} color="var(--accent-color)" />}
                            {node.id === '2' && <Compass size={50} strokeWidth={1} color="var(--accent-color)" />}
                            {node.id === '3' && <Lightbulb size={50} strokeWidth={1} color="var(--accent-color)" />}
                        </div>

                        <div className="mobile-card-content">
                            <h3>{node.title}</h3>
                            <p>{node.desc}</p>
                        </div>

                        {/* Native Mobile active touch target overlay */}
                        <div className="mobile-card-touch-layer">
                            <ArrowRight /> Get Started
                        </div>
                    </motion.div>
                ))}
            </section>

        </div>
    );
};

export default ChatPage;
