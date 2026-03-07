import google.generativeai as genai
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-flash-latest")

prompt = "Explain quantum entanglement in simple terms. Return ONLY a JSON object with keys: 'explanation', 'tldr', 'prerequisites' (as list of objects with topic/description)."

async def main():
    try:
        print("Sending query...")
        response = model.generate_content(prompt)
        print("Response received!")
        print(f"Text: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
