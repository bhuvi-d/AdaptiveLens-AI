"use client";

import React, { useState, useEffect, useCallback } from "react";
import Sidebar from "@/components/Sidebar";
import ChatInterface from "@/components/ChatInterface";
import ComplexitySlider from "@/components/ComplexitySlider";
import FloatingMascot from "@/components/FloatingMascot";
import { RefreshCw } from "lucide-react";
import { api } from "@/lib/api";
import type { DocumentInfo, ChatMessage } from "@/types";

export default function Home() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [selectedDocs, setSelectedDocs] = useState<string[]>([]);
  const [complexityLevel, setComplexityLevel] = useState(3);
  const [pendingComplexity, setPendingComplexity] = useState(3);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [lastQuestion, setLastQuestion] = useState("");
  const [detailLevel, setDetailLevel] = useState(2000);
  const [pendingDetail, setPendingDetail] = useState(2000);

  const fetchDocuments = useCallback(async () => {
    try {
      const result = await api.listDocuments();
      setDocuments(result.documents);
    } catch (error) {
      console.error("Failed to fetch documents:", error);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleSelectDoc = (docId: string) => {
    setSelectedDocs((prev) =>
      prev.includes(docId)
        ? prev.filter((id) => id !== docId)
        : [...prev, docId]
    );
  };

  const handleApplyComplexity = async () => {
    const newLevel = pendingComplexity;
    setComplexityLevel(newLevel);

    // Regenerate last answer at new complexity level
    if (messages.length > 0 && lastQuestion) {
      setIsLoading(true);
      try {
        const response = await api.regenerate(
          lastQuestion,
          newLevel,
          pendingDetail,
          selectedDocs.length > 0 ? selectedDocs : undefined
        );

        const newMessage: ChatMessage = {
          id: `regenerated-${Date.now()}`,
          role: "assistant",
          content: response.explanation,
          timestamp: new Date(),
          complexity_level: response.complexity_level,
          readability_score: response.readability_score,
          readability_label: response.readability_label,
          tldr: response.tldr,
          prerequisites: response.prerequisites,
          sources: response.sources,
        };

        // Replace last assistant message
        setMessages((prev) => {
          const msgs = [...prev];
          const idx =
            msgs.length -
            1 -
            msgs
              .slice()
              .reverse()
              .findIndex((m) => m.role === "assistant");
          if (idx >= 0) {
            msgs[idx] = newMessage;
          }
          return msgs;
        });
      } catch (error) {
        console.error("Regeneration error:", error);
        setPendingComplexity(complexityLevel);
      } finally {
        setIsLoading(false);
      }
    }
  };

  // Track last question for regeneration
  useEffect(() => {
    const lastUserMsg = [...messages].reverse().find((m) => m.role === "user");
    if (lastUserMsg) {
      setLastQuestion(lastUserMsg.content);
    }
  }, [messages]);

  const handleClearChat = () => {
    setMessages([]);
    setLastQuestion("");
  };

  return (
    <div className="app-container">
      <Sidebar
        documents={documents}
        onDocumentsChange={fetchDocuments}
        selectedDocs={selectedDocs}
        onSelectDoc={handleSelectDoc}
      />

      <main className="main-content">
        {/* Top Bar */}
        <div className="top-bar">
          <ComplexitySlider
            value={complexityLevel}
            pendingValue={pendingComplexity}
            onChange={setPendingComplexity}
            onApply={() => {
              setComplexityLevel(pendingComplexity);
              setDetailLevel(pendingDetail);
              handleApplyComplexity();
            }}
            disabled={isLoading}
          />
          <div className="detail-slider-container" style={{ display: 'flex', alignItems: 'center', gap: 12, marginLeft: 20 }}>
            <span style={{ fontSize: 11, fontWeight: 800, color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Depth</span>
            <input
              type="range"
              min={500}
              max={4000}
              step={500}
              value={pendingDetail}
              onChange={(e) => setPendingDetail(Number(e.target.value))}
              className="complexity-slider"
              title="Explanation word count/depth"
            />
            <span style={{ fontSize: 12, fontWeight: 700, minWidth: 40, color: 'var(--accent)' }}>{~~(pendingDetail / 250)} min</span>
          </div>
          <div className="top-bar-actions">
            <button
              className="btn-icon"
              onClick={handleClearChat}
              title="Clear chat"
            >
              <RefreshCw size={16} />
            </button>
          </div>
        </div>

        {/* Chat */}
        <ChatInterface
          messages={messages}
          setMessages={setMessages}
          complexityLevel={complexityLevel}
          detailLevel={detailLevel}
          selectedDocs={selectedDocs}
          isLoading={isLoading}
          setIsLoading={setIsLoading}
          documentsCount={documents.length}
        />
      </main>
      <FloatingMascot />
    </div>
  );
}
