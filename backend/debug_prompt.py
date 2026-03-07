import google.generativeai as genai
import os
import asyncio
from dotenv import load_dotenv
import sys

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model_name = "models/gemini-2.5-flash"
print(f"Testing model: {model_name}")
model = genai.GenerativeModel(model_name)

# Realistic context and question
context = """
DNA replication is the biological process of producing two identical replicas of DNA from one original DNA molecule. 
DNA replication occurs in all living organisms acting as the most essential part for biological inheritance. 
This is essential for cell division during growth and repair of damaged tissues, while it also ensures that each of the new cells receives its own copy of the DNA. 
DNA is made up of a double helix of two complementary strands. During replication, these strands are separated. 
Each strand of the original DNA molecule then serves as a template for the production of its counterpart, a process referred to as semiconservative replication. 
"""

question = "How does DNA replication work and why is it important?"

prompt_template = """You are AdaptiveLens AI, an advanced adaptive learning assistant. Your goal is to provide deep, comprehensive, and engaging academic explanations.

## Complexity Level: 1/5 — "Beginner"
**Target Audience:** Children or total beginners.
**Style Guide:** Simple, analogies-rich, very clear.
**Vocabulary Level:** Extremely basic.

## Relevant Context from Documents:
{context}

## User's Question:
{question}

## Core Instructions:
1. Provide a THOROUGH, multi-paragraph explanation (at least 3-4 sections).
2. Answer using the provided document context, but expand on concepts for clarity.
3. Adapt your depth and detail to exactly match Complexity Level 1.
4. Use formatting like bullet points, bold text, and subheadings to make information digestible.
5. Include relevant analogies and real-world examples to aid understanding.
6. Include relevant formulas or equations using LaTeX notation when appropriate.
7. Identify and define key prerequisite concepts in the 'prerequisites' section.
8. If the current text is too short, elaborate on the implications or importance of the topic.

## Response Format:
Provide your response in the following JSON format:
{{
    "explanation": "# Your Title\\n\\n## Overview\\n[Detailed multi-paragraph explanation here with markdown formatting and rich detail]\\n\\n## Key Details\\n[Further elaboration...]",
    "tldr": "A concise, high-impact 1-2 sentence summary",
    "prerequisites": [
        {{"topic": "Prerequisite Topic Name", "description": "Clear explanation of this fundamental concept"}},
    ]
}}

IMPORTANT: Return ONLY valid JSON. No text before or after context. Maximize the detail in 'explanation'."""

final_prompt = prompt_template.format(context=context, question=question)

async def main():
    try:
        response = await asyncio.to_thread(model.generate_content, final_prompt)
        print("--- RAW CONTENT START ---")
        print(response.text)
        print("--- RAW CONTENT END ---")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
