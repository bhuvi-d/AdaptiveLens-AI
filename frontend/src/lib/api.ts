/**
 * AdaptiveLens AI - API Client
 * Handles all communication with the FastAPI backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

import type {
    DocumentInfo,
    UploadResponse,
    QueryResponse,
    QuizResponse,
    QuizValidation,
} from "@/types";

class ApiClient {
    private baseUrl: string;

    constructor() {
        this.baseUrl = API_BASE;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseUrl}${endpoint}`;
        const response = await fetch(url, {
            ...options,
            headers: {
                ...options.headers,
            },
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: "Unknown error" }));
            throw new Error(error.detail || `API error: ${response.status}`);
        }

        return response.json();
    }

    // --- Documents ---
    async uploadDocument(file: File): Promise<UploadResponse> {
        const formData = new FormData();
        formData.append("file", file);

        return this.request<UploadResponse>("/api/documents/upload", {
            method: "POST",
            body: formData,
        });
    }

    async listDocuments(): Promise<{ documents: DocumentInfo[]; total: number }> {
        return this.request("/api/documents");
    }

    async deleteDocument(docId: string): Promise<{ message: string }> {
        return this.request(`/api/documents/${docId}`, { method: "DELETE" });
    }

    async getSuggestions(): Promise<string[]> {
        return this.request("/api/documents/suggestions");
    }

    // --- Query ---
    async query(
        question: string,
        complexityLevel: number,
        detailLevel: number = 2000,
        documentIds?: string[],
        chatHistory?: { role: string; content: string }[]
    ): Promise<QueryResponse> {
        return this.request<QueryResponse>("/api/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question,
                complexity_level: complexityLevel,
                detail_level: detailLevel,
                document_ids: documentIds,
                chat_history: chatHistory,
            }),
        });
    }

    async regenerate(
        question: string,
        complexityLevel: number,
        detailLevel: number = 2000,
        documentIds?: string[]
    ): Promise<QueryResponse> {
        return this.request<QueryResponse>("/api/query/regenerate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question,
                complexity_level: complexityLevel,
                detail_level: detailLevel,
                document_ids: documentIds,
            }),
        });
    }

    // --- Quiz ---
    async generateQuiz(
        explanationText: string,
        complexityLevel: number,
        questionCount: number = 5
    ): Promise<QuizResponse> {
        return this.request<QuizResponse>("/api/quiz/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                explanation_text: explanationText,
                complexity_level: complexityLevel,
                question_count: questionCount,
            }),
        });
    }

    async validateAnswer(
        question: string,
        correctAnswer: string,
        userAnswer: string,
        questionType: string = "mcq"
    ): Promise<QuizValidation> {
        return this.request<QuizValidation>("/api/quiz/validate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question,
                correct_answer: correctAnswer,
                user_answer: userAnswer,
                question_type: questionType,
            }),
        });
    }

    // --- Health ---
    async healthCheck(): Promise<{ status: string; version: string; documents_count: number }> {
        return this.request("/health");
    }
}

export const api = new ApiClient();
