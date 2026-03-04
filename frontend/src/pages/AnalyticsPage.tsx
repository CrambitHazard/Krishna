import React from 'react';
import { motion } from 'framer-motion';
import { ArrowUpRight } from 'lucide-react';
import './AnalyticsPage.css';

const AnalyticsPage: React.FC = () => {
    return (
        <div className="analytics-view">
            <section className="mega-telemetry">
                <motion.div
                    className="telemetry-inner"
                    initial={{ opacity: 0, scale: 0.95 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
                >
                    <h1 className="mega-heading">
                        YOUR<br />
                        <span className="text-italic">PROGRESS.</span>
                    </h1>

                    <div className="telemetry-form">
                        <div className="brutalist-input-group">
                            <label>01 — CHOOSE TOPIC</label>
                            <input type="text" placeholder="E.G. PHYSICS" className="brutalist-input" />
                        </div>

                        <div className="brutalist-input-group">
                            <label>02 — CURRENT MASTERY</label>
                            <input type="text" placeholder="YOUR SCORE" className="brutalist-input" />
                        </div>

                        <button className="mega-cta">
                            VIEW DETAILS <ArrowUpRight size={40} />
                        </button>
                    </div>
                </motion.div>

                <footer className="telemetry-footer">
                    <div className="footer-meta">
                        <span>KRISHNA 2.0 // AUTONOMOUS GUIDE</span>
                        <span>LISTENING</span>
                    </div>
                </footer>
            </section>
        </div>
    );
};

export default AnalyticsPage;
