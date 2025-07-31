import os
from autogen.agentchat import AssistantAgent, UserProxyAgent
from wrapper import gemini_analyze_code

SAVE_PATH = r"D:\auto ai project\analysis_result.txt"

class CodeAnalyzerAgent(AssistantAgent):
    def generate_reply(self, messages, sender, config=None):  # ✅ config optional for AutoGen
        try:
            last_msg = messages[-1].get("content", "")

            if "||CODE||" not in last_msg:
                return {"content": "⚠️ Please provide code in '<language>||CODE||<source>' format."}

            language, code = last_msg.split("||CODE||", 1)
            result = gemini_analyze_code(language.strip(), code.strip())

            os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
            with open(SAVE_PATH, "w", encoding="utf-8") as f:
                f.write(result)

            print(f"\n✅ Analysis saved to: {SAVE_PATH}")

            return {"content": result}

        except Exception as e:
            return {"content": f"❌ Error while analyzing code: {str(e)}"}

def create_agents():
    user_proxy = UserProxyAgent(name="user_proxy", code_execution_config={"use_docker": False})
    analyzer = CodeAnalyzerAgent(name="code_analyzer")
    return user_proxy, analyzer

if __name__ == "__main__":
    user_proxy, analyzer = create_agents()
    print("✅ Agents created successfully!")
