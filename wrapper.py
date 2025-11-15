import os
from dotenv import load_dotenv
import google.generativeai as gen

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file.")

gen.configure(api_key=api_key)

MODEL = gen.GenerativeModel("gemini-2.5-pro")



def send_prompt(prompt: str) -> str:
    """General-purpose Gemini prompt sender."""
    try:
        response = MODEL.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error calling Gemini API: {str(e)}"


def gemini_analyze_code(language, user_code):
    """Return AST/CFG/DFG etc."""
    prompt = f"""
You are an expert code analyzer.

Analyze the following {language} code and provide:

1. Abstract symbol Table
2. Control Flow Graph
3. Data Flow Graph

Code:
{user_code}
"""
    try:
        response = MODEL.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error calling Gemini API: {str(e)}"
