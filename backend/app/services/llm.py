"""
AdaptiveLens AI - LLM Service
Handles all interactions with Gemini 1.5 Pro for generating explanations and quizzes.
"""

import json
import logging
import asyncio
import re
import google.generativeai as genai
from app.config import settings
from app.models.schemas import COMPLEXITY_DESCRIPTIONS
from app.models.prompts import EXPLANATION_PROMPT, QUIZ_PROMPT, QUIZ_VALIDATE_PROMPT

logger = logging.getLogger(__name__)


class LLMService:
    """Manages Gemini 1.5 Pro interactions for adaptive explanations."""

    def __init__(self):
        genai.configure(api_key=settings.google_api_key)
        self.fallback_models = [
            settings.llm_model,             # Primary (default: gemini-flash-lite-latest)
            "models/gemini-2.0-flash",      # Robust fallback
            "models/gemini-flash-latest",   # Standard alias
            "models/gemini-pro-latest"      # Pro tier fallback
        ]
        self.current_model_idx = 0
        self._init_model()

    def _init_model(self, max_tokens: int = None):
        model_name = self.fallback_models[self.current_model_idx]
        tokens = max_tokens or settings.max_response_tokens
        self.model = genai.GenerativeModel(
            model_name,
            generation_config=genai.GenerationConfig(
                max_output_tokens=tokens,
                temperature=0.7,
            )
        )
        logger.info(f"LLM service initialized with model: {model_name} (limit: {tokens} tokens)")

    async def generate_content(self, prompt: str):
        """Public method for raw content generation with rotation."""
        return await self._call_llm(prompt)

    async def _call_llm(self, prompt: str):
        """Invoke LLM with automatic model rotation on 429 errors."""
        for attempt in range(len(self.fallback_models)):
            try:
                response = await asyncio.to_thread(self.model.generate_content, prompt)
                return response
            except Exception as e:
                # Check for quota error
                if "429" in str(e) or "quota" in str(e).lower():
                    logger.warning(f"Quota hit for {self.fallback_models[self.current_model_idx]}. Rotating...")
                    self.current_model_idx = (self.current_model_idx + 1) % len(self.fallback_models)
                    self._init_model()
                    continue
                # Other errors
                logger.error(f"LLM Call Error: {e}")
                raise e
        raise Exception("All LLM fallback models exhausted or hit quota.")

    async def generate_explanation(self, question: str, context_chunks: list[dict],
                                    complexity_level: int, 
                                    detail_level: int = 2000,
                                    chat_history: list[dict] = None) -> dict:
        """Generate an adaptive explanation at the specified complexity level."""
        # Update model config with requested detail level
        if detail_level != settings.max_response_tokens:
            self._init_model(max_tokens=detail_level)
            
        level_info = COMPLEXITY_DESCRIPTIONS.get(complexity_level, COMPLEXITY_DESCRIPTIONS[3])
        
        # Format context
        context_text = "\n\n---\n\n".join([
            f"[Source: {chunk['metadata'].get('document_name', 'Unknown')}, "
            f"Page {chunk['metadata'].get('page_number', '?')}]\n{chunk['text']}"
            for chunk in context_chunks
        ])

        # Format chat history
        chat_context = ""
        if chat_history:
            chat_context = "## Previous Conversation:\n"
            for msg in chat_history[-6:]:  # Last 6 messages for context
                role = msg.get("role", "user")
                content = msg.get("content", "")
                chat_context += f"**{role.capitalize()}**: {content}\n\n"

        # NEW: Ensure content with curlies doesn't break the prompt formatter
        # We also need to escape any curlies in the dynamic content
        safe_context = context_text.replace("{", "{{").replace("}", "}}")
        safe_question = question.replace("{", "{{").replace("}", "}}")
        safe_chat = chat_context.replace("{", "{{").replace("}", "}}")

        # Build prompt
        prompt = EXPLANATION_PROMPT.format(
            level=complexity_level,
            level_name=level_info["name"],
            audience=level_info["audience"],
            style=level_info["style"],
            vocabulary=level_info["vocabulary"],
            context=safe_context,
            question=safe_question,
            chat_context=safe_chat
        )

        # Generate response using fallback-aware helper
        response = await self._call_llm(prompt)
        response_text = response.text.strip() if response.text else ""
        
        if not response_text:
            return {
                "explanation": "I'm sorry, I couldn't generate an explanation. Please try again.",
                "tldr": "Error generating response.",
                "prerequisites": []
            }

        # New delimiter-based parsing
        explanation = ""
        tldr = ""
        prerequisites = []

        # Parse Explanation
        exp_match = re.search(r"\[EXPLANATION\](.*?)(?=\[TLDR\]|\[PREREQUISITES\]|$)", response_text, re.DOTALL)
        if exp_match:
            explanation = exp_match.group(1).strip()
        
        # Parse TLDR
        tldr_match = re.search(r"\[TLDR\](.*?)(?=\[PREREQUISITES\]|$)", response_text, re.DOTALL)
        if tldr_match:
            tldr = tldr_match.group(1).strip()

        # Parse Prerequisites
        pre_match = re.search(r"\[PREREQUISITES\](.*?)$", response_text, re.DOTALL)
        if pre_match:
            pre_text = pre_match.group(1).strip()
            # Try to grab bullet points
            lines = pre_text.split("\n")
            for line in lines:
                if "**" in line and ":" in line:
                    topic = line.split("**")[1].strip()
                    desc = line.split(":")[1].strip()
                    prerequisites.append({"topic": topic, "description": desc})
                elif ":" in line and len(line.split(":", 1)) == 2:
                    parts = line.split(":", 1)
                    prerequisites.append({"topic": parts[0].strip(" -*#"), "description": parts[1].strip()})

        # Fallback if parsing failed
        if not explanation:
            explanation = response_text

        return {
            "explanation": explanation,
            "tldr": tldr,
            "prerequisites": prerequisites[:3]
        }

    async def generate_quiz(self, explanation: str, complexity_level: int,
                            question_count: int = 5) -> list[dict]:
        """Generate quiz questions from an explanation."""
        level_info = COMPLEXITY_DESCRIPTIONS.get(complexity_level, COMPLEXITY_DESCRIPTIONS[3])
        
        # NEW: Escape any curlies in explanation to avoid format() crash
        safe_explanation = explanation.replace("{", "{{").replace("}", "}}")
        
        prompt = QUIZ_PROMPT.format(
            count=question_count,
            explanation=safe_explanation,
            level=complexity_level,
            level_name=level_info["name"],
            audience=level_info["audience"]
        )

        response = await self._call_llm(prompt)
        response_text = response.text.strip() if response.text else ""
        
        parsed = self._parse_json_response(response_text)
        return parsed.get("questions", [])

    async def validate_answer(self, question: str, correct_answer: str,
                               user_answer: str, question_type: str = "mcq") -> dict:
        """Validate a user's quiz answer with closeness scoring."""
        prompt = QUIZ_VALIDATE_PROMPT.format(
            question_type=question_type,
            question=question,
            correct_answer=correct_answer,
            user_answer=user_answer
        )

        response = await self._call_llm(prompt)
        response_text = response.text.strip() if response.text else ""
        
        parsed = self._parse_json_response(response_text)
        closeness = parsed.get("closeness_score", 0)
        quality = parsed.get("quality", "needs_work")
        return {
            "is_correct": closeness >= 60,
            "closeness_score": closeness,
            "quality": quality,
            "feedback": parsed.get("feedback", "Unable to evaluate the answer.")
        }

    def _parse_json_response(self, text: str) -> dict:
        """Robustly parse JSON from LLM response."""
        if not text:
            return {}

        # Remove markdown code blocks
        clean_text = text
        if "```" in clean_text:
            # Handle ```json ... ``` or just ``` ... ```
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", clean_text, re.DOTALL)
            if match:
                clean_text = match.group(1).strip()
        
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError:
            # Fallback: Find first { and last }
            try:
                start_idx = clean_text.find("{")
                end_idx = clean_text.rfind("}") + 1
                if start_idx != -1 and end_idx > start_idx:
                    return json.loads(clean_text[start_idx:end_idx])
            except:
                pass
            
            logger.warning(f"Could not parse JSON from: {text[:100]}...")
            return {}


# Singleton
_llm_service = None

def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
