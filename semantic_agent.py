# semantic_agent.py
import json
import requests
from autogen.agentchat import AssistantAgent
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# OpenRouter endpoint
API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
}


def call_llama(prompt: str) -> str:
    """Call LLaMA-3-70B-Instruct via OpenRouter."""
    try:
        payload = {
            "model": "meta-llama/llama-3-70b-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }

        response = requests.post(API_URL, headers=HEADERS, json=payload)
        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ LLaMA API Error: {str(e)}"


class SemanticExtractorAgent(AssistantAgent):
    def generate_reply(self, messages, sender, config=None):
        try:
            msg = messages[-1]["content"]

            if "||SEMANTICS||" not in msg:
                return {"role": "assistant",
                        "content": "⚠️ Use <lang>||SEMANTICS||<code>"}

            language, code = msg.split("||SEMANTICS||", 1)

            # LLaMA prompt
            prompt = f"""
You are a senior semantic analysis expert.

Return STRICT JSON in the following format:

{{
  "name": "",
  "description": "",
  "inputs": [],
  "outputs": [],
  "complexity_estimate": ""
}}

Analyze this {language} code:
--------------------------------
{code}
--------------------------------

Return ONLY JSON. No explanation.
"""

            raw = call_llama(prompt)

            # Parse JSON safely
            try:
                start = raw.find("{")
                end = raw.rfind("}")
                json_text = raw[start:end+1]
                parsed = json.loads(json_text)
            except:
                parsed = {"error": "Invalid JSON returned", "raw": raw}

            return {"role": "assistant", "content": json.dumps(parsed, indent=2)}

        except Exception as e:
            return {"role": "assistant",
                    "content": f"❌ Semantic Extractor Error: {str(e)}"}
