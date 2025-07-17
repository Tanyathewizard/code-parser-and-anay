from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") 
import os
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

def main():
    print(" Code Parser & Analyzer using AutoGen v0.4+")
    print(" Supports Python, Java, C++, JavaScript, and more")
    print(" Type 'END' on a new line when you're done entering code.\n")

    # Step 1: Get language
    language = input(" Enter the programming language (e.g. Python, Java, C++): ").strip()

    # Step 2: Input code
    print("\n Paste your code below (type END to finish):\n")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    user_code = "\n".join(lines)

    if not user_code.strip():
        print(" No code provided. Exiting.")
        return

    # Step 3: Set LLM config (Replace this key with a valid key)
    llm_config = {
        "config_list": [
            {
                "model": "gpt-4",  # or "gpt-3.5-turbo"
                "api_key": "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"  # 👈 Use working key here
            }
        ],
        "temperature": 0
    }

    # Step 4: Define agents
    symbol_agent = AssistantAgent(
        name="SymbolAgent",
        system_message=f"You are an expert in {language}. Extract all variables, functions, classes, and their scopes as a symbol table.",
        llm_config=llm_config
    )

    cfg_agent = AssistantAgent(
        name="CFGBuilder",
        system_message=f"You are a control flow expert. Build a control flow graph for {language} code.",
        llm_config=llm_config
    )

    dfg_agent = AssistantAgent(
        name="DFGBuilder",
        system_message=f"You analyze data flow. Build a data flow graph for the code, tracing how variables are assigned and used.",
        llm_config=llm_config
    )

    code_analyzer = AssistantAgent(
        name="CodeAnalyzer",
        system_message=(
            "You are the coordinator. Break the task into 3 subtasks:\n"
            "1. Ask SymbolAgent to extract a symbol table\n"
            "2. Ask CFGBuilder for a control flow graph\n"
            "3. Ask DFGBuilder for a data flow graph\n"
            "Then combine all results into one structured summary."
        ),
        llm_config=llm_config
    )

    # Step 5: Proxy agent (disabling Docker)
    user_proxy = UserProxyAgent(
        name="Coordinator",
        human_input_mode="NEVER",
        code_execution_config={"use_docker": False}
    )

    # Step 6: Group Chat setup
    group_chat = GroupChat(
        agents=[user_proxy, code_analyzer, symbol_agent, cfg_agent, dfg_agent],
        messages=[]
    )
    manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)

    # Step 7: Prompt
    task_prompt = f"""
Analyze the following {language} code and return:
1. A symbol table listing all functions, classes, and variables with their scopes.
2. A control flow graph (CFG) showing logic flow (conditionals, loops, calls).
3. A data flow graph (DFG) showing how data moves between variables/functions.

Code:
{user_code}

Assign tasks to SymbolAgent, CFGBuilder, and DFGBuilder. Combine all results into a clear final summary.
"""

    # Step 8: Run
    print("\n Analyzing your code using AutoGen agents...\n")
    result = user_proxy.initiate_chat(manager, message=task_prompt)

    # Step 9: Save output
    with open("analysis_output.txt", "w", encoding="utf-8") as f:
        f.write(str(result))

    print("Analysis complete! Results saved in: analysis_output.txt")

if __name__ == "__main__":
    main()

