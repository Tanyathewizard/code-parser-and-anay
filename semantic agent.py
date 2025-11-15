import json
from autogen.agentchat import AssistantAgent
from wrapper import MODEL


class SemanticExtractorAgent(AssistantAgent):
    def generate_reply(self, messages, sender, config=None):
        try:
            user_msg = messages[-1]["content"]

            if "||SEMANTICS||" not in user_msg:
                return {"role": "assistant", "content": "⚠️ Use <lang>||SEMANTICS||<code>"}

            language, code = user_msg.split("||SEMANTICS||", 1)

            prompt = f"""
Extract the following from the {language} code strictly in JSON:

{{
  "name": "",
  "description": "",
  "inputs": [],
  "outputs": [],
  "complexity_estimate": ""
}}

Code:
{code}

Return ONLY JSON.
"""

            raw = MODEL.generate_content(prompt).text

            # Parse JSON safely
            data = json.loads(raw)

            return {"role": "assistant", "content": json.dumps(data, indent=2)}

        except Exception as e:
            return {"role": "assistant", "content": f"❌ Semantic Extractor Error: {str(e)}"}
