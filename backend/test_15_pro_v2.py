import google.generativeai as genai
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model_name = "models/gemini-pro-latest"
print(f"Testing model: {model_name}")
model = genai.GenerativeModel(model_name)

prompt = "Hello!"

async def main():
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        print(f"SUCCESS: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
