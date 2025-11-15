# agents/agents.py
from autogen.agentchat import AssistantAgent, UserProxyAgent
from wrapper import gemini_analyze_code
from semantic_agent import SemanticExtractorAgent


class CodeAnalyzerAgent(AssistantAgent):
    def generate_reply(self, messages, sender, config=None):
        try:
            last_msg = messages[-1].get("content", "")

            if "||CODE||" not in last_msg:
                return {"content": "Format: <language>||CODE||<code>"}

            language, code = last_msg.split("||CODE||", 1)
            result = gemini_analyze_code(language.strip(), code.strip())

            return {"content": result}

        except Exception as e:
            return {"content": f"Analyzer Error: {e}"}


def create_agents():
    user_proxy = UserProxyAgent(name="user_proxy", code_execution_config={"use_docker": False})
    analyzer = CodeAnalyzerAgent(name="code_analyzer")
    semantic = SemanticExtractorAgent(name="semantic_extractor")
    return user_proxy, analyzer, semantic
