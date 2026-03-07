"""
AdaptiveLens AI - Quiz Router
Handles quiz generation and answer validation.
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    QuizGenerateRequest, QuizGenerateResponse, QuizQuestion,
    QuizValidateRequest, QuizValidateResponse
)
from app.services.llm import get_llm_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quiz", tags=["Quiz"])


@router.post("/generate", response_model=QuizGenerateResponse)
async def generate_quiz(request: QuizGenerateRequest):
    """Generate quiz questions from an explanation."""
    try:
        llm_service = get_llm_service()
        questions_data = await llm_service.generate_quiz(
            explanation=request.explanation_text,
            complexity_level=request.complexity_level,
            question_count=request.question_count
        )

        questions = []
        for i, q in enumerate(questions_data):
            questions.append(QuizQuestion(
                id=i + 1, # Use guaranteed unique numeric ID for frontend keys
                type=q.get("type", "mcq"),
                question=q.get("question", ""),
                options=q.get("options"),
                correct_answer=q.get("correct_answer", ""),
                explanation=q.get("explanation", "")
            ))

        return QuizGenerateResponse(
            questions=questions,
            complexity_level=request.complexity_level
        )

    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating quiz: {str(e)}"
        )


@router.post("/validate", response_model=QuizValidateResponse)
async def validate_answer(request: QuizValidateRequest):
    """Validate a user's answer to a quiz question."""
    try:
        llm_service = get_llm_service()
        result = await llm_service.validate_answer(
            question=request.question,
            correct_answer=request.correct_answer,
            user_answer=request.user_answer,
            question_type=request.question_type
        )

        return QuizValidateResponse(
            is_correct=result["is_correct"],
            closeness_score=result.get("closeness_score", 0),
            quality=result.get("quality", "needs_work"),
            feedback=result["feedback"],
            correct_answer=request.correct_answer
        )

    except Exception as e:
        logger.error(f"Error validating answer: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error validating answer: {str(e)}"
        )
