import google.generativeai as genai
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model_name = "models/gemini-embedding-001"
print(f"Testing model: {model_name}")

async def main():
    try:
        result = await asyncio.to_thread(
            genai.embed_content,
            model=model_name,
            content="Hello world",
            task_type="retrieval_query"
        )
        print(f"SUCCESS: {len(result['embedding'])} dimensions")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
