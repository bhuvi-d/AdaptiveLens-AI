import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print(f"Listing models with details:")
try:
    models = genai.list_models()
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
             print(f"ID: {m.name}, Display: {m.display_name}")
except Exception as e:
    print(f"Error: {e}")
