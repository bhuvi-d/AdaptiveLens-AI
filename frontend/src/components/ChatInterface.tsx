"use client";

import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";
import { Send, Zap, BookOpen, ChevronDown, ChevronRight, HelpCircle } from "lucide-react";
import ReadabilityBadge from "./ReadabilityBadge";
import QuizPanel from "./QuizPanel";
import SplineScene from "./SplineScene";
import LumiAvatar from "./LumiAvatar";
import { api } from "@/lib/api";
import type { ChatMessage, QuizQuestion } from "@/types";

interface ChatInterfaceProps {
    messages: ChatMessage[];
    setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
    complexityLevel: number;
    detailLevel: number;
    selectedDocs: string[];
    isLoading: boolean;
    setIsLoading: React.Dispatch<React.SetStateAction<boolean>>;
    documentsCount: number;
}

export default function ChatInterface({
    messages,
    setMessages,
    complexityLevel,
    detailLevel,
    selectedDocs,
    isLoading,
    setIsLoading,
    documentsCount,
}: ChatInterfaceProps) {
    const [input, setInput] = useState("");
    const [quizzes, setQuizzes] = useState<Record<string, QuizQuestion[]>>({});
    const [generatingQuiz, setGeneratingQuiz] = useState<string | null>(null);
    const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({});
    const [suggestions, setSuggestions] = useState<string[]>([
        "Explain quantum entanglement",
        "What is machine learning?",
        "How does DNA replication work?",
        "Explain the theory of relativity",
    ]);
    const chatEndRef = useRef<HTMLDivElement>(null);
    const chatContainerRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);

    // Fetch contextual suggestions when documents change
    useEffect(() => {
        const fetchSuggestions = async () => {
            try {
                const result = await api.getSuggestions();
                if (result && result.length > 0) {
                    setSuggestions(result);
                }
            } catch (error) {
                console.error("Failed to fetch suggestions:", error);
            }
        };
        fetchSuggestions();
    }, [documentsCount]);

    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [messages, isLoading]);

    const handleSend = async (text?: string) => {
        const messageText = text || input.trim();
        if (!messageText || isLoading) return;

        const userMessage: ChatMessage = {
            id: `user-${Date.now()}`,
            role: "user",
            content: messageText,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            const chatHistory = messages.map((m) => ({
                role: m.role,
                content: m.content,
            }));

            const response = await api.query(
                userMessage.content,
                complexityLevel,
                detailLevel,
                selectedDocs.length > 0 ? selectedDocs : undefined,
                chatHistory
            );

            const assistantMessage: ChatMessage = {
                id: `assistant-${Date.now()}`,
                role: "assistant",
                content: response.explanation || "I'm sorry, I couldn't generate an explanation. Please try asking a different question or rephrasing.",
                timestamp: new Date(),
                complexity_level: response.complexity_level,
                readability_score: response.readability_score,
                readability_label: response.readability_label,
                tldr: response.tldr,
                prerequisites: response.prerequisites,
                sources: response.sources,
            };

            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error: any) {
            const msg = error instanceof Error ? error.message : "Something went wrong";
            const isQuotaError = msg.includes("429") || msg.toLowerCase().includes("quota");
            const botContent = isQuotaError
                ? `**Quota Exceeded (429):** You've reached your daily limit for the Gemini Free Tier (20 requests/day). \n\n**To fix this:**\n1. Wait 24 hours for the quota to reset.\n2. Use a different API key in the backend \`.env\` file.\n3. Consider switching to a pay-as-you-go key in Google AI Studio.`
                : `**Error:** ${msg}\n\nPlease make sure documents are uploaded and the backend is running.`;

            const errorMessage: ChatMessage = {
                id: `error-${Date.now()}`,
                role: "assistant",
                content: botContent,
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handlePrerequisiteClick = (topic: string) => {
        handleSend(`Explain: ${topic}`);
    };

    const handleGenerateQuiz = async (messageId: string, explanation: string) => {
        setGeneratingQuiz(messageId);
        try {
            const response = await api.generateQuiz(explanation, complexityLevel);
            setQuizzes((prev) => ({ ...prev, [messageId]: response.questions }));
        } catch (error) {
            console.error("Quiz generation error:", error);
        } finally {
            setGeneratingQuiz(null);
        }
    };

    const toggleSources = (messageId: string) => {
        setExpandedSources((prev) => ({ ...prev, [messageId]: !prev[messageId] }));
    };

    return (
        <>
            <div className="chat-area" ref={chatContainerRef}>
                {messages.length === 0 ? (
                    <div className="chat-empty">
                        <h2>Meet Lumi ✨</h2>
                        <p>
                            {documentsCount > 0
                                ? "Hi! I'm Lumi, your study buddy. Ask me anything about your documents!"
                                : "Hi! I'm Lumi. Upload a PDF and I'll help you learn from it!"}
                        </p>
                        <div className="chat-suggestions">
                            {suggestions.map((s, i) => (
                                <button
                                    key={i}
                                    className="chat-suggestion"
                                    onClick={() => handleSend(s)}
                                    style={{
                                        backgroundColor: 'white',
                                        border: '2px solid var(--bg-secondary)',
                                        color: 'var(--text-primary)',
                                        padding: '12px 20px',
                                        borderRadius: '16px',
                                        fontSize: '14px',
                                        fontWeight: 600,
                                        transition: 'all 0.2s ease',
                                        boxShadow: '0 4px 6px rgba(0,0,0,0.05)'
                                    }}
                                    onMouseOver={(e) => {
                                        e.currentTarget.style.borderColor = '#D2A59B';
                                        e.currentTarget.style.color = '#D2A59B';
                                        e.currentTarget.style.transform = 'translateY(-2px)';
                                    }}
                                    onMouseOut={(e) => {
                                        e.currentTarget.style.borderColor = 'var(--bg-secondary)';
                                        e.currentTarget.style.color = 'var(--text-primary)';
                                        e.currentTarget.style.transform = 'translateY(0)';
                                    }}
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    messages.map((msg) => (
                        <div key={msg.id} className={`message message-${msg.role}`}>
                            <div className="message-avatar">
                                {msg.role === "user" ? "👤" : <LumiAvatar />}
                            </div>
                            <div className="message-content">
                                <div className="message-bubble">
                                    <ReactMarkdown
                                        remarkPlugins={[remarkMath]}
                                        rehypePlugins={[rehypeKatex]}
                                    >
                                        {msg.content}
                                    </ReactMarkdown>
                                </div>

                                {/* Meta info for assistant messages */}
                                {msg.role === "assistant" && (
                                    <>
                                        <div className="message-meta">
                                            {msg.readability_score !== undefined && (
                                                <ReadabilityBadge
                                                    score={msg.readability_score}
                                                    label={msg.readability_label || ""}
                                                />
                                            )}
                                        </div>

                                        {/* TL;DR */}
                                        {msg.tldr && (
                                            <div className="tldr-card">
                                                <div className="tldr-header">
                                                    <Zap size={12} /> TL;DR
                                                </div>
                                                <div className="tldr-text">{msg.tldr}</div>
                                            </div>
                                        )}

                                        {/* Prerequisites */}
                                        {msg.prerequisites && msg.prerequisites.length > 0 && (
                                            <div className="prerequisites-section">
                                                <div className="prerequisites-title">
                                                    <BookOpen size={12} /> Prerequisite Knowledge
                                                </div>
                                                <div className="prerequisite-chips">
                                                    {msg.prerequisites.map((p, i) => (
                                                        <button
                                                            key={i}
                                                            className="prerequisite-chip"
                                                            onClick={() => handlePrerequisiteClick(p.topic)}
                                                            title={p.description}
                                                        >
                                                            {p.topic}
                                                        </button>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* Sources */}
                                        {msg.sources && msg.sources.length > 0 && (
                                            <div className="sources-section">
                                                <button
                                                    className="sources-toggle"
                                                    onClick={() => toggleSources(msg.id)}
                                                >
                                                    {expandedSources[msg.id] ? (
                                                        <ChevronDown size={14} />
                                                    ) : (
                                                        <ChevronRight size={14} />
                                                    )}
                                                    {msg.sources.length} sources
                                                </button>
                                                {expandedSources[msg.id] && (
                                                    <div className="sources-list">
                                                        {msg.sources.map((s, i) => (
                                                            <div key={i} className="source-item">
                                                                <span className="source-doc">
                                                                    {s.document_name}
                                                                </span>
                                                                {s.page_number && (
                                                                    <span className="source-page">
                                                                        p.{s.page_number}
                                                                    </span>
                                                                )}
                                                                <span className="source-relevance">
                                                                    {(s.relevance_score * 100).toFixed(0)}%
                                                                </span>
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}
                                            </div>
                                        )}

                                        {/* Quiz */}
                                        <QuizPanel
                                            questions={quizzes[msg.id] || []}
                                            explanation={msg.content}
                                            complexityLevel={complexityLevel}
                                            onGenerateQuiz={() =>
                                                handleGenerateQuiz(msg.id, msg.content)
                                            }
                                            isGenerating={generatingQuiz === msg.id}
                                        />
                                    </>
                                )}
                            </div>
                        </div>
                    ))
                )}

                {isLoading && (
                    <div className="message message-assistant">
                        <div className="message-avatar"><LumiAvatar /></div>
                        <div className="message-content">
                            <div className="message-bubble">
                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--text-tertiary)', fontSize: '14px' }}>
                                    <span style={{ fontWeight: 700, color: '#D2A59B' }}>Lumi</span> is thinking
                                    <div className="loading-dots">
                                        <div className="loading-dot" />
                                        <div className="loading-dot" />
                                        <div className="loading-dot" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={chatEndRef} />
            </div>

            {/* Input Area */}
            <div className="chat-input-area">
                <div className="chat-input-container">
                    <div className="chat-input-wrapper">
                        <textarea
                            ref={inputRef}
                            className="chat-input"
                            placeholder="Ask a question about your documents..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            rows={1}
                            disabled={isLoading}
                        />
                        <button
                            className="chat-send-btn"
                            onClick={() => handleSend()}
                            disabled={!input.trim() || isLoading}
                        >
                            <Send size={16} />
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
}
