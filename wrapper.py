from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def gemini_analyze_code(language, user_code):
    prompt = f"""
You are a code analyzer.

Analyze the following {language} code and return:

1. A symbol table listing all functions, classes, and variables with their scopes.
2. A control flow graph (CFG) describing logic flow (if/else, loops, etc).
3. A data flow graph (DFG) showing how data moves between variables/functions.

Code:
{user_code}
"""
    response = model.generate_content(prompt)
    return response.text
