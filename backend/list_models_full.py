import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print(f"Listing ALL models:")
try:
    models = list(genai.list_models())
    for m in models:
        # print(f"{m.name} -> {m.supported_generation_methods}")
        if 'generateContent' in m.supported_generation_methods:
             print(f"GENERATE-CAPABLE: {m.name}")
except Exception as e:
    print(f"Error: {e}")
