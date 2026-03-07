/**
 * AdaptiveLens AI - TypeScript Type Definitions
 */

export interface DocumentInfo {
  id: string;
  filename: string;
  page_count: number;
  chunk_count: number;
  file_size_mb: number;
  uploaded_at: string;
}

export interface UploadResponse {
  id: string;
  filename: string;
  page_count: number;
  chunk_count: number;
  message: string;
}

export interface SourceChunk {
  text: string;
  page_number: number | null;
  section_title: string | null;
  document_id: string;
  document_name: string;
  relevance_score: number;
}

export interface PrerequisiteTopic {
  topic: string;
  description: string;
}

export interface QueryResponse {
  explanation: string;
  tldr: string;
  complexity_level: number;
  complexity_name: string;
  readability_score: number;
  readability_label: string;
  prerequisites: PrerequisiteTopic[];
  sources: SourceChunk[];
}

export interface QuizQuestion {
  id: number;
  type: "mcq" | "short_answer" | "conceptual";
  question: string;
  options: string[] | null;
  correct_answer: string;
  explanation: string;
}

export interface QuizResponse {
  questions: QuizQuestion[];
  complexity_level: number;
}

export interface QuizValidation {
  is_correct: boolean;
  closeness_score: number;
  quality: "excellent" | "good" | "partial" | "needs_work";
  feedback: string;
  correct_answer: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  complexity_level?: number;
  readability_score?: number;
  readability_label?: string;
  tldr?: string;
  prerequisites?: PrerequisiteTopic[];
  sources?: SourceChunk[];
  quiz?: QuizQuestion[];
}

export const COMPLEXITY_LABELS: Record<number, string> = {
  1: "Beginner",
  2: "Beginner+",
  3: "Intermediate",
  4: "Intermediate+",
  5: "Advanced",
};

export const COMPLEXITY_COLORS: Record<number, string> = {
  1: "#22c55e",
  2: "#84cc16",
  3: "#eab308",
  4: "#f97316",
  5: "#ef4444",
};
