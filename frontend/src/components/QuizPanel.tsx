"use client";

import React, { useState } from "react";
import { Brain, Loader2, CheckCircle2, AlertCircle, HelpCircle } from "lucide-react";
import { api } from "@/lib/api";
import type { QuizQuestion, QuizValidation } from "@/types";

interface QuizPanelProps {
    questions: QuizQuestion[];
    explanation: string;
    complexityLevel: number;
    onGenerateQuiz: () => void;
    isGenerating: boolean;
}

const QUALITY_INFO = {
    excellent: { emoji: "✨", color: "#4f8a61", label: "Excellent!" },
    good: { emoji: "✅", color: "#4f8a61", label: "Good job" },
    partial: { emoji: "🤔", color: "#b1823e", label: "Almost there" },
    needs_work: { emoji: "📖", color: "#b15d52", label: "Needs review" },
};

export default function QuizPanel({
    questions,
    explanation,
    complexityLevel,
    onGenerateQuiz,
    isGenerating,
}: QuizPanelProps) {
    const [answers, setAnswers] = useState<Record<number, string>>({});
    const [results, setResults] = useState<Record<number, QuizValidation>>({});
    const [validating, setValidating] = useState<number | null>(null);

    const handleSelectOption = (questionId: number, option: string) => {
        if (results[questionId]) return;
        setAnswers((prev) => ({ ...prev, [questionId]: option }));
    };

    const handleSubmitAnswer = async (q: QuizQuestion) => {
        const userAnswer = answers[q.id];
        if (!userAnswer || results[q.id]) return;

        setValidating(q.id);
        try {
            const result = await api.validateAnswer(
                q.question,
                q.correct_answer,
                userAnswer,
                q.type
            );
            setResults((prev) => ({ ...prev, [q.id]: result }));
        } catch (error) {
            console.error("Validation error:", error);
        } finally {
            setValidating(null);
        }
    };

    return (
        <div className="quiz-section">
            <div className="quiz-header">
                <div className="quiz-header-title">
                    <Brain size={18} className="doc-item-icon" />
                    <span>Interactive Quiz</span>
                </div>
                {explanation && (
                    <button
                        className="quiz-generate-btn"
                        onClick={onGenerateQuiz}
                        disabled={isGenerating}
                    >
                        {isGenerating ? (
                            <Loader2 size={14} className="spinner" />
                        ) : questions.length > 0 ? (
                            "Regenerate Quiz"
                        ) : (
                            "Test My Knowledge"
                        )}
                    </button>
                )}
            </div>

            {questions.length > 0 ? (
                <div className="quiz-body">
                    {questions.map((q) => {
                        const result = results[q.id];
                        const qInfo = result ? QUALITY_INFO[result.quality] : null;

                        return (
                            <div key={q.id} className="quiz-question">
                                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                                    <span className={`quiz-question-type quiz-type-${q.type}`}>
                                        {q.type.replace("_", " ")}
                                    </span>
                                    {result && (
                                        <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, fontWeight: 700, color: qInfo?.color }}>
                                            {qInfo?.emoji} {qInfo?.label} {q.type !== 'mcq' && `(${result.closeness_score}%)`}
                                        </div>
                                    )}
                                </div>

                                <p className="quiz-question-text" style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)' }}>
                                    {q.question}
                                </p>

                                {/* MCQ Options */}
                                {q.type === "mcq" && q.options && (
                                    <div className="quiz-options">
                                        {q.options.map((option, i) => {
                                            const isSelected = answers[q.id] === option;
                                            let statusClass = "";
                                            if (result) {
                                                if (option === q.correct_answer) statusClass = "correct";
                                                else if (isSelected) statusClass = "incorrect";
                                            } else if (isSelected) {
                                                statusClass = "selected";
                                            }

                                            return (
                                                <button
                                                    key={i}
                                                    className={`quiz-option ${statusClass}`}
                                                    onClick={() => handleSelectOption(q.id, option)}
                                                    disabled={!!result}
                                                >
                                                    {option}
                                                </button>
                                            );
                                        })}
                                    </div>
                                )}

                                {/* Text Answer */}
                                {(q.type === "short_answer" || q.type === "conceptual") && (
                                    <div style={{ marginTop: 12 }}>
                                        <textarea
                                            className="quiz-answer-input"
                                            placeholder="Type your explanation here..."
                                            value={answers[q.id] || ""}
                                            onChange={(e) =>
                                                setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))
                                            }
                                            disabled={!!result}
                                            style={{
                                                width: '100%',
                                                minHeight: 80,
                                                padding: 14,
                                                borderRadius: 12,
                                                border: '1px solid var(--border-muted)',
                                                backgroundColor: result ? '#f9f9f9' : 'white',
                                                fontFamily: 'inherit'
                                            }}
                                        />
                                    </div>
                                )}

                                {/* Submit / Feedback */}
                                {!result ? (
                                    answers[q.id] && (
                                        <button
                                            className="quiz-submit-btn"
                                            onClick={() => handleSubmitAnswer(q)}
                                            disabled={validating === q.id}
                                            style={{
                                                marginTop: 12,
                                                backgroundColor: 'var(--text-primary)',
                                                color: 'white',
                                                padding: '10px 24px',
                                                borderRadius: 30,
                                                fontWeight: 700,
                                                fontSize: 13,
                                                cursor: 'pointer',
                                                border: 'none'
                                            }}
                                        >
                                            {validating === q.id ? "Evaluating..." : "Check Answer"}
                                        </button>
                                    )
                                ) : (
                                    <div style={{
                                        marginTop: 16,
                                        padding: 16,
                                        borderRadius: 12,
                                        backgroundColor: 'rgba(0,0,0,0.03)',
                                        borderLeft: `4px solid ${qInfo?.color || '#ccc'}`,
                                        fontSize: 14,
                                        lineHeight: 1.6
                                    }}>
                                        <p style={{ fontWeight: 700, marginBottom: 4, color: qInfo?.color }}>Feedback:</p>
                                        <p>{result.feedback}</p>
                                        {q.type !== 'mcq' && (
                                            <div style={{ marginTop: 10, fontSize: 13, color: 'var(--text-tertiary)' }}>
                                                <strong>Reference Answer:</strong> {q.correct_answer}
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            ) : (
                <div style={{ padding: '60px 40px', textAlign: 'center' }}>
                    <HelpCircle size={48} style={{ opacity: 0.1, marginBottom: 16 }} />
                    <p style={{ color: 'var(--text-tertiary)', fontSize: 15 }}>
                        Ready to test your understanding? Generate a quick quiz based on this explanation.
                    </p>
                </div>
            )}
        </div>
    );
}
