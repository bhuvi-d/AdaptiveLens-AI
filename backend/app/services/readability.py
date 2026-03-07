"""
AdaptiveLens AI - Readability Scoring Service
Calculates Flesch Reading Ease scores for explanations.
"""

import textstat
import logging

logger = logging.getLogger(__name__)


class ReadabilityService:
    """Calculates readability metrics for generated explanations."""

    @staticmethod
    def calculate_flesch_score(text: str) -> float:
        """
        Calculate Flesch Reading Ease score.
        
        Score interpretation:
        90-100: Very Easy (5th grade)
        80-89:  Easy (6th grade)
        70-79:  Fairly Easy (7th grade)
        60-69:  Standard (8th-9th grade)
        50-59:  Fairly Difficult (10th-12th grade)
        30-49:  Difficult (College)
        0-29:   Very Confusing (Graduate+)
        """
        if not text or len(text.split()) < 10:
            return 50.0  # Default for very short texts
        
        score = textstat.flesch_reading_ease(text)
        # Clamp between 0 and 100
        return max(0, min(100, round(score, 1)))

    @staticmethod
    def get_readability_label(score: float) -> str:
        """Convert Flesch score to human-readable label."""
        if score >= 90:
            return "Very Easy"
        elif score >= 80:
            return "Easy"
        elif score >= 70:
            return "Fairly Easy"
        elif score >= 60:
            return "Standard"
        elif score >= 50:
            return "Fairly Difficult"
        elif score >= 30:
            return "Difficult"
        else:
            return "Very Complex"

    @staticmethod
    def get_expected_range(complexity_level: int) -> tuple[float, float]:
        """Get expected Flesch score range for a complexity level."""
        ranges = {
            1: (70, 100),   # Beginner: Easy to Very Easy
            2: (60, 85),    # Beginner+: Standard to Easy
            3: (50, 75),    # Intermediate: Fairly Difficult to Fairly Easy
            4: (35, 60),    # Intermediate+: Difficult to Standard
            5: (10, 50),    # Advanced: Very Complex to Fairly Difficult
        }
        return ranges.get(complexity_level, (40, 70))


# Singleton
_readability_service = None

def get_readability_service() -> ReadabilityService:
    global _readability_service
    if _readability_service is None:
        _readability_service = ReadabilityService()
    return _readability_service
