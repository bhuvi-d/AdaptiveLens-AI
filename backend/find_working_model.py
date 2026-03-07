import google.generativeai as genai
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

models_to_test = [
    "models/gemini-2.0-flash",
    "models/gemini-pro-latest",
    "models/gemini-flash-latest",
    "models/gemini-2.0-flash-lite",
    "models/gemini-2.5-pro",
]

async def test_model(name):
    print(f"Testing {name}...")
    try:
        model = genai.GenerativeModel(name)
        response = await asyncio.to_thread(model.generate_content, "Hi")
        print(f"  SUCCESS: {name}")
        return True
    except Exception as e:
        print(f"  FAILED {name}: {e}")
        return False

async def main():
    for m in models_to_test:
        if await test_model(m):
            print(f"\nFOUND WORKING MODEL: {m}")
            break

if __name__ == "__main__":
    asyncio.run(main())
