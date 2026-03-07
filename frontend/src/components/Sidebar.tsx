"use client";

import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { FileUp, FileText, Trash2, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import type { DocumentInfo } from "@/types";

interface SidebarProps {
    documents: DocumentInfo[];
    onDocumentsChange: () => void;
    selectedDocs: string[];
    onSelectDoc: (id: string) => void;
}

export default function Sidebar({
    documents,
    onDocumentsChange,
    selectedDocs,
    onSelectDoc,
}: SidebarProps) {
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [uploadStatus, setUploadStatus] = useState("");
    const [deletingId, setDeletingId] = useState<string | null>(null);

    const onDrop = useCallback(
        async (acceptedFiles: File[]) => {
            for (const file of acceptedFiles) {
                if (!file.name.toLowerCase().endsWith(".pdf")) {
                    setUploadStatus("Only PDF files are accepted");
                    continue;
                }

                setIsUploading(true);
                setUploadProgress(30);
                setUploadStatus(`Processing ${file.name}...`);

                try {
                    setUploadProgress(60);
                    const result = await api.uploadDocument(file);
                    setUploadProgress(100);
                    setUploadStatus(result.message);
                    onDocumentsChange();
                } catch (error: unknown) {
                    const msg = error instanceof Error ? error.message : "Upload failed";
                    setUploadStatus(`Error: ${msg}`);
                } finally {
                    setIsUploading(false);
                    setTimeout(() => {
                        setUploadProgress(0);
                        setUploadStatus("");
                    }, 3000);
                }
            }
        },
        [onDocumentsChange]
    );

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { "application/pdf": [".pdf"] },
        disabled: isUploading,
    });

    const handleDelete = async (docId: string, e: React.MouseEvent) => {
        e.stopPropagation();
        setDeletingId(docId);
        try {
            await api.deleteDocument(docId);
            onDocumentsChange();
        } catch (error) {
            console.error("Delete failed:", error);
        } finally {
            setDeletingId(null);
        }
    };

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="sidebar-logo">
                    <div>
                        <h1>AdaptiveLens AI</h1>
                        <p>Adaptive Learning System</p>
                    </div>
                </div>
            </div>

            <div className="sidebar-section">
                <div className="sidebar-section-title">Documents ({documents.length})</div>

                {documents.length === 0 ? (
                    <p className="no-docs">No documents uploaded yet</p>
                ) : (
                    <div className="doc-list">
                        {documents.map((doc) => (
                            <div
                                key={doc.id}
                                className="doc-item"
                                onClick={() => onSelectDoc(doc.id)}
                                style={{
                                    borderColor: selectedDocs.includes(doc.id)
                                        ? "var(--accent)"
                                        : undefined,
                                    background: selectedDocs.includes(doc.id)
                                        ? "var(--accent-muted)"
                                        : undefined,
                                }}
                            >
                                <FileText size={18} className="doc-item-icon" />
                                <div className="doc-item-info">
                                    <div className="doc-item-name">{doc.filename}</div>
                                    <div className="doc-item-meta">
                                        {doc.page_count} pages · {doc.chunk_count} chunks ·{" "}
                                        {doc.file_size_mb} MB
                                    </div>
                                </div>
                                <button
                                    className="doc-item-delete"
                                    onClick={(e) => handleDelete(doc.id, e)}
                                    disabled={deletingId === doc.id}
                                >
                                    {deletingId === doc.id ? (
                                        <Loader2 size={14} className="spinner" />
                                    ) : (
                                        <Trash2 size={14} />
                                    )}
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                <div
                    {...getRootProps()}
                    className={`upload-zone ${isDragActive ? "active" : ""}`}
                >
                    <input {...getInputProps()} />
                    <div className="upload-zone-icon">
                        {isUploading ? <Loader2 size={28} className="spinner" /> : <FileUp size={28} />}
                    </div>
                    <div className="upload-zone-text">
                        {isDragActive
                            ? "Drop PDF here"
                            : isUploading
                                ? "Processing..."
                                : "Drop PDF or click to upload"}
                    </div>
                    <div className="upload-zone-hint">Max 20 MB · 200 pages</div>
                </div>

                {(uploadProgress > 0 || uploadStatus) && (
                    <div className="upload-progress">
                        {uploadProgress > 0 && (
                            <div className="progress-bar">
                                <div
                                    className="progress-fill"
                                    style={{ width: `${uploadProgress}%` }}
                                />
                            </div>
                        )}
                        {uploadStatus && <div className="upload-status">{uploadStatus}</div>}
                    </div>
                )}
            </div>
        </aside>
    );
}
