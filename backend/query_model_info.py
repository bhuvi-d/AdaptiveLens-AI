import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

try:
    m = genai.get_model("models/gemini-flash-latest")
    print(f"Name: {m.name}")
    print(f"Description: {m.description}")
    print(f"Display Name: {m.display_name}")
except Exception as e:
    print(f"Error: {e}")
