# semantic_extractor.py
import json
from typing import Tuple
from wrapper import send_prompt
from database.database import save_analysis, init_db

# Ensure DB exists
init_db()

SEMANTIC_PROMPT_TEMPLATE = """
You are a senior semantic analysis engine.

Analyze the given {language} code and return a STRICT JSON object with:

{
  "name": "",
  "description": "",A
  "inputs": [],
  "outputs": [],
  "complexity_estimate": "",
  "dependencies": [],
  "patterns": [],
  "edge_cases": [],
  "optimizations": [],
  "variable_roles": {},
  "summary": ""
}

Rules:
- Return ONLY valid JSON.
- NO markdown.
- NO explanation outside JSON.

CODE:
------------------------
{code}
------------------------
"""


def clean_json(text: str) -> str:
    """Remove accidental markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if "```" in text:
            text = text.split("```")[0]
    return text.strip()


def extract_semantics(language: str, code: str, save_to_db: bool = True) -> Tuple[dict, int]:
    prompt = SEMANTIC_PROMPT_TEMPLATE.format(language=language, code=code)
    raw = send_prompt(prompt)

    raw = clean_json(raw)

    # Try to extract JSON
    try:
        start = raw.find("{")
        end = raw.rfind("}")
        parsed = json.loads(raw[start:end + 1])
    except Exception:
        parsed = {"error": "Could not parse JSON", "raw": raw}

    row_id = 0
    if save_to_db:
        summary = parsed.get("summary") if isinstance(parsed, dict) else None
        row_id = save_analysis(language, "semantic", code, json.dumps(parsed), summary)

    return parsed, row_id
