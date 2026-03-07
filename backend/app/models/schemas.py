"""
AdaptiveLens AI - Pydantic Models & Schemas
Defines request/response models for all API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import IntEnum


# --- Complexity Levels ---
class ComplexityLevel(IntEnum):
    BEGINNER = 1
    BEGINNER_PLUS = 2
    INTERMEDIATE = 3
    INTERMEDIATE_PLUS = 4
    ADVANCED = 5


COMPLEXITY_DESCRIPTIONS = {
    1: {
        "name": "Beginner",
        "audience": "School students (ages 14-18)",
        "style": "Simple language, analogies, real-world examples. Use everyday words and avoid jargon entirely. Explain as if talking to a curious teenager.",
        "vocabulary": "Everyday words, no technical jargon"
    },
    2: {
        "name": "Beginner+",
        "audience": "Senior school / early college students",
        "style": "Simple explanations with light technical terms introduced gently. Define every new term inline. Use relatable analogies.",
        "vocabulary": "Mostly simple, key terms defined inline"
    },
    3: {
        "name": "Intermediate",
        "audience": "Undergraduate students",
        "style": "Structured explanations with technical terms. Provide context and examples. Use formal but accessible language.",
        "vocabulary": "Domain terms, defined when first used"
    },
    4: {
        "name": "Intermediate+",
        "audience": "Advanced undergrad / early researchers",
        "style": "Semi-formal explanations with some assumed knowledge. Less hand-holding, more depth. Reference related concepts freely.",
        "vocabulary": "Technical terms used freely, less hand-holding"
    },
    5: {
        "name": "Advanced",
        "audience": "Researchers and domain experts",
        "style": "Dense, precise, formal academic tone. Assume full domain knowledge. Include mathematical formulations where relevant.",
        "vocabulary": "Full technical terminology assumed"
    }
}


# --- Document Models ---
class DocumentInfo(BaseModel):
    id: str
    filename: str
    page_count: int
    chunk_count: int
    file_size_mb: float
    uploaded_at: str


class DocumentListResponse(BaseModel):
    documents: list[DocumentInfo]
    total: int


class UploadResponse(BaseModel):
    id: str
    filename: str
    page_count: int
    chunk_count: int
    message: str


# --- Query Models ---
class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    complexity_level: int = Field(default=3, ge=1, le=5)
    detail_level: int = Field(default=2000, ge=500, le=4000)
    document_ids: Optional[list[str]] = None
    chat_history: Optional[list[dict]] = None


class SourceChunk(BaseModel):
    text: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    document_id: str
    document_name: str
    relevance_score: float


class PrerequisiteTopic(BaseModel):
    topic: str
    description: str


class QueryResponse(BaseModel):
    explanation: str
    tldr: str
    complexity_level: int
    complexity_name: str
    readability_score: float
    readability_label: str
    prerequisites: list[PrerequisiteTopic]
    sources: list[SourceChunk]
    chat_id: Optional[str] = None


# --- Quiz Models ---
class QuizQuestion(BaseModel):
    id: int
    type: str  # "mcq", "short_answer", "conceptual"
    question: str
    options: Optional[list[str]] = None  # For MCQ only
    correct_answer: str
    explanation: str


class QuizGenerateRequest(BaseModel):
    explanation_text: str
    complexity_level: int = Field(default=3, ge=1, le=5)
    question_count: int = Field(default=5, ge=1, le=10)


class QuizGenerateResponse(BaseModel):
    questions: list[QuizQuestion]
    complexity_level: int


class QuizValidateRequest(BaseModel):
    question: str
    correct_answer: str
    user_answer: str
    question_type: str = "mcq"  # mcq, short_answer, or conceptual


class QuizValidateResponse(BaseModel):
    is_correct: bool
    closeness_score: int = 0
    quality: str = "needs_work"  # excellent, good, partial, needs_work
    feedback: str
    correct_answer: str


# --- Health ---
class HealthResponse(BaseModel):
    status: str
    version: str
    documents_count: int
