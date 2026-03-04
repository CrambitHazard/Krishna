import axios from 'axios';

// Get EC2 IP or run local depending on .env
// Defaults to the EC2 IP you provided
const BASE_URL = import.meta.env.VITE_API_URL || 'http://54.210.23.55:8000/api/v1';

const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// ── Types ──────────────────────────────────────────────────────────────

export interface UploadResponse {
    filename: string;
    message: string;
    document_id: string;
    total_pages: number;
    total_chunks: number;
    uploaded_at: string;
}

export interface SourceReference {
    chunk_index: number | null;
    filename: string;
    document_id: string;
    score: number;
}

export interface ChatResponse {
    answer: string;
    sources: SourceReference[];
    session_id: string;
    agent: string;
    metadata: Record<string, any>;
}

export interface QuizQuestion {
    question: string;
    options: string[];
    correct_answer: string;
    explanation: string;
}

export interface QuizResponse {
    topic: string;
    questions: QuizQuestion[];
    total: number;
    metadata: Record<string, any>;
}

export interface QuestionFeedback {
    question: string;
    options: string[];
    user_answer: string;
    correct_answer: string;
    is_correct: boolean;
    explanation: string;
}

export interface QuizSubmitResponse {
    score: number;
    total: number;
    percentage: number;
    topic: string;
    correct_questions: QuestionFeedback[];
    incorrect_questions: QuestionFeedback[];
}

export interface TopicInsight {
    topic: string;
    accuracy: number;
    attempts: number;
    status: string;
    is_struggling: boolean;
}

export interface TopicProgress {
    topic: string;
    accuracy: number;
    attempts: number;
    total_score: number;
    total_questions: number;
    last_updated: string;
}

export interface ProgressResponse {
    topics: TopicProgress[];
    weak_topics: TopicInsight[];
    strong_topics: TopicInsight[];
    recommendations: string[];
    summary: Record<string, any>;
}

// ── API Functions ──────────────────────────────────────────────────────

/**
 * Upload a study document to index and ground the answers on.
 */
export async function uploadDocument(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<UploadResponse>('/upload/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
}

/**
 * Ask a question to KRISHNA via multi-agent pipeline.
 */
export async function askQuestion(query: string, sessionId?: string): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/chat/', {
        query,
        session_id: sessionId,
    });
    return response.data;
}

/**
 * Generate a new MCQ quiz.
 */
export async function generateQuiz(topic: string, numQuestions: number = 5, useContext: boolean = true): Promise<QuizResponse> {
    const response = await api.post<QuizResponse>('/quiz/', {
        topic,
        num_questions: numQuestions,
        use_context: useContext,
    });
    return response.data;
}

/**
 * Submit answers for an generated quiz to be evaluated and persisted.
 */
export async function submitQuiz(
    topic: string,
    userAnswers: string[],
    quizData: QuizQuestion[]
): Promise<QuizSubmitResponse> {
    const response = await api.post<QuizSubmitResponse>('/quiz/submit', {
        topic,
        user_answers: userAnswers,
        quiz_data: quizData,
    });
    return response.data;
}

/**
 * Get learning progress, analytics, and recommendations.
 */
export async function getProgress(): Promise<ProgressResponse> {
    const response = await api.get<ProgressResponse>('/quiz/progress');
    return response.data;
}

export default api;
